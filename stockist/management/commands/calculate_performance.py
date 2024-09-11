import time
import yfinance as yf
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import os
import pandas as pd
import json

CACHE_TIMEOUT = getattr(settings, 'CACHE_TIMEOUT', 36000000)  # 1 hour cache timeout by default

def download_data_with_retry(tickers, max_retries=3, delay=5):
    data = {}
    for ticker in tickers:
        for attempt in range(max_retries):
            try:
                df = yf.download(ticker, period="1y")
                if not df.empty:
                    data[ticker] = df
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} for {ticker} failed: {e}")
                time.sleep(delay)
    return data

def get_market_cap(ticker):
    try:
        stock = yf.Ticker(ticker)
        market_cap = int(stock.info.get('marketCap', 0) or 0)
        return market_cap
    except Exception as e:
        print(f"Failed to get market cap for {ticker}: {e}")
        return None

def get_volume(ticker):
    try:
        stock = yf.Ticker(ticker)
        volume = stock.history(period='1y')['Volume'].mean()
        return volume
    except Exception as e:
        print(f"Failed to get volume for {ticker}: {e}")
        return None

def normalize(values):
    min_val = min(values)
    max_val = max(values)
    return [(val - min_val) / (max_val - min_val) if max_val != min_val else 0 for val in values]


class Command(BaseCommand):
    help = 'Fetch and append stock data and store it as a JSON file'

    def handle(self, *args, **kwargs):
        # Define file paths
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        master_stock_data_path = os.path.join(upload_dir, 'master_stock_data.csv')

        # Load stock tickers from master_stock_data.csv
        try:
            stock_df = pd.read_csv(master_stock_data_path)
            stocks_tickers = stock_df['Symbol'].dropna().tolist()  # Extract stock tickers
        except FileNotFoundError:
            self.stderr.write(f"{master_stock_data_path} not found.")
            return

        # Check if data is cached
        cache_key = 'stock_data_with_metrics'
        cached_data = cache.get(cache_key)

        if cached_data:
            stocks_data = cached_data
        else:
            # Download stock data
            stocks_data = download_data_with_retry(stocks_tickers)

            if not stocks_data:
                self.stderr.write('Failed to download data for stocks after multiple attempts.')
                return

            # Process data for stocks
            stocks_metrics = {}
            for ticker in stocks_tickers:
                if ticker in stocks_data:
                    close_prices = stocks_data[ticker]['Close']
                    percentage_change = (close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0] * 100
                    market_cap = get_market_cap(ticker)
                    volume = get_volume(ticker)
                    stocks_metrics[ticker] = {
                        'change': percentage_change,
                        'market_cap': market_cap,
                        'volume': volume
                    }

            # Cache the downloaded data
            cache.set(cache_key, stocks_metrics, CACHE_TIMEOUT)

        # Append fetched data to the original DataFrame
        stock_df['market_cap'] = stock_df['Symbol'].apply(lambda x: stocks_metrics.get(x, {}).get('market_cap'))
        stock_df['volume'] = stock_df['Symbol'].apply(lambda x: stocks_metrics.get(x, {}).get('volume'))
        stock_df['change'] = stock_df['Symbol'].apply(lambda x: stocks_metrics.get(x, {}).get('change'))

        # Drop rows where market_cap, volume, or change is NaN
        stock_df = stock_df.dropna(subset=['market_cap', 'volume', 'change'])

        # Convert the DataFrame to a list of dictionaries
        stock_data_json = stock_df.to_dict(orient='records')

        # Save the final data as a JSON file
        output_path = os.path.join(settings.MEDIA_ROOT, 'final_stock_data.json')
        with open(output_path, 'w') as json_file:
            json.dump(stock_data_json, json_file, indent=4)

        self.stdout.write(self.style.SUCCESS(f'Successfully fetched and saved stock data in {output_path}'))
