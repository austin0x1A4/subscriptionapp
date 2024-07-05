import time
import yfinance as yf
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from stockist.models import IndexPerformance, StockPerformance

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
        market_cap = stock.info.get('marketCap')
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
    help = 'Calculate and store the top performers'

    def handle(self, *args, **kwargs):
        indices_tickers = {
           'S&P 500': '^GSPC',
    'Dow Jones': '^DJI',
    'DAX': '^GDAXI',
    'CAC 40': '^FCHI',
    'EURO STOXX 50': '^STOXX50E',
    'Nikkei': '^N225',
    'Hang Seng': '^HSI',
    'Russell 2000': '^RUT',
    'SENSEX': '^BSESN',
    'Nifty Bank': '^NSEBANK',
    'Copper Futures': 'HG=F',
    'Nifty 50': '^NSEI',
    'NASDAQ': '^IXIC',
    'FTSE 100': '^FTSE',
    'FTSE All-Share': '^FTAS',
    'Shanghai Composite': '^SSEC',
    'BSE Sensex': '^BSESN',
    'S&P/TSX Composite Index': '^GSPTSE',
    'S&P/ASX 200': '^AXJO',
    'Bovespa Index': '^BVSP'
        }
        stocks_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
'BRK-B', 'NVDA', 'META', 'JPM', 'V',
'UNH', 'JNJ', 'WMT', 'PG', 'MA',
'XOM', 'HD', 'CVX', 'BAC', 'ABBV',
'PFE', 'AVGO', 'KO', 'PEP', 'COST',
'LLY', 'TMO', 'MRK', 'CSCO', 'ABT',
'ADBE', 'MCD', 'CRM', 'ACN', 'DHR',
'NKE', 'DIS', 'VZ', 'NEE', 'TXN',
'PM', 'WFC', 'CMCSA', 'INTC', 'UPS',
'BMY', 'RTX', 'QCOM', 'AMD', 'HON',
'UNP', 'T', 'ORCL', 'LIN', 'AMGN',
'LOW', 'IBM', 'SBUX', 'INTU', 'CVS',
'BA', 'SPGI', 'CAT', 'DE', 'GS',
'BLK', 'AXP', 'ISRG', 'MDLZ', 'GILD',
'ADI', 'TGT', 'PYPL', 'BKNG', 'C',
'MMM', 'SYK', 'ZTS', 'PLD', 'AMAT',
'ADP', 'CHTR', 'MO', 'NFLX', 'COP',
'SCHW', 'GE', 'EOG', 'TJX', 'DUK',
'PNC', 'SO', 'CSX', 'MS', 'BDX',
'USB', 'TFC', 'CME', 'ANTM', 'CL',
'LRCX', 'CI', 'APD', 'CB', 'ICE'
        ]

        cache_key = 'top_performers_data'
        cached_data = cache.get(cache_key)

        if cached_data:
            indices_data, stocks_data, indices_percentage_changes, stocks_percentage_changes, stocks_market_caps, stocks_volumes = cached_data
        else:
            indices_data = download_data_with_retry(list(indices_tickers.values()))
            stocks_data = download_data_with_retry(stocks_tickers)

            if not indices_data or not stocks_data:
                self.stderr.write('Failed to download data for all indices or stocks after multiple attempts.')
                return

            indices_percentage_changes = {}
            for name, ticker in indices_tickers.items():
                if ticker in indices_data:
                    close_prices = indices_data[ticker]['Close']
                    percentage_change = (close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0] * 100
                    indices_percentage_changes[name] = percentage_change

            stocks_percentage_changes = {}
            stocks_market_caps = {}
            stocks_volumes = {}
            for ticker in stocks_tickers:
                if ticker in stocks_data:
                    close_prices = stocks_data[ticker]['Close']
                    percentage_change = (close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0] * 100
                    stocks_percentage_changes[ticker] = percentage_change
                    market_cap = get_market_cap(ticker)
                    stocks_market_caps[ticker] = market_cap
                    volume = get_volume(ticker)
                    stocks_volumes[ticker] = volume

            cached_data = (indices_data, stocks_data, indices_percentage_changes, stocks_percentage_changes, stocks_market_caps, stocks_volumes)
            cache.set(cache_key, cached_data, CACHE_TIMEOUT)

        sorted_indices_changes = sorted(indices_percentage_changes.items(), key=lambda x: x[1], reverse=True)
        top_indices_performers = [{'name': name, 'change': change} for name, change in sorted_indices_changes[:10]]

        # Filter out tickers that don't have corresponding data
        valid_tickers = [ticker for ticker in stocks_tickers if ticker in stocks_percentage_changes and ticker in stocks_market_caps and ticker in stocks_volumes]
        stocks_percentage_changes_list = [stocks_percentage_changes[ticker] for ticker in valid_tickers]
        stocks_market_caps_list = [stocks_market_caps[ticker] for ticker in valid_tickers]
        stocks_volumes_list = [stocks_volumes[ticker] for ticker in valid_tickers]

        normalized_percentage_changes = normalize(stocks_percentage_changes_list)
        normalized_market_caps = normalize(stocks_market_caps_list)
        normalized_volumes = normalize(stocks_volumes_list)

        weights = {'percentage_change': 0.4, 'market_cap': 0.3, 'volume': 0.3}
        
        composite_scores = {}
        for idx, ticker in enumerate(valid_tickers):
            composite_scores[ticker] = (weights['percentage_change'] * normalized_percentage_changes[idx] +
                                        weights['market_cap'] * normalized_market_caps[idx] +
                                        weights['volume'] * normalized_volumes[idx])
        
        sorted_composite_scores = sorted(composite_scores.items(), key=lambda x: x[1], reverse=True)
        
        top_stocks_performers = [{'name': name, 'score': score, 'change': stocks_percentage_changes[name], 'market_cap': stocks_market_caps[name], 'volume': stocks_volumes[name]} for name, score in sorted_composite_scores[:10]]

        # Store results in the database
        IndexPerformance.objects.all().delete()
        for performer in top_indices_performers:
            IndexPerformance.objects.create(name=performer['name'], change=performer['change'])

        StockPerformance.objects.all().delete()
        for performer in top_stocks_performers:
            StockPerformance.objects.create(
                name=performer['name'],
                score=performer['score'],
                change=performer['change'],
                market_cap=performer['market_cap'],
                volume=performer['volume']
            )

        self.stdout.write(self.style.SUCCESS('Successfully calculated and stored top performers'))
