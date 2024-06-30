import yfinance as yf
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.conf import settings
import pandas as pd
import time
import json
import os
from .forms import UploadFileForm

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

def top_performers(request):
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
        'FTSE All-Share': '^FTAS'
    }

    stocks_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
        'BRK-B', 'NVDA', 'META', 'JPM', 'V'
    ]

    cache_key = 'top_performers_data'
    cached_data = cache.get(cache_key)

    if cached_data:
        indices_data, stocks_data, indices_percentage_changes, stocks_percentage_changes, stocks_market_caps, stocks_volumes = cached_data
    else:
        indices_data = download_data_with_retry(list(indices_tickers.values()))
        stocks_data = download_data_with_retry(stocks_tickers)

        if not indices_data or not stocks_data:
            context = {
                'error_message': 'Failed to download data for all indices or stocks after multiple attempts.'
            }
            return render(request, 'stockist/error.html', context)

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

    stocks_percentage_changes_list = list(stocks_percentage_changes.values())
    stocks_market_caps_list = list(stocks_market_caps.values())
    stocks_volumes_list = list(stocks_volumes.values())

    normalized_percentage_changes = normalize(stocks_percentage_changes_list)
    normalized_market_caps = normalize(stocks_market_caps_list)
    normalized_volumes = normalize(stocks_volumes_list)

    weights = {'percentage_change': 0.4, 'market_cap': 0.3, 'volume': 0.3}
    
    composite_scores = {}
    for ticker in stocks_tickers:
        composite_scores[ticker] = (weights['percentage_change'] * normalized_percentage_changes[stocks_tickers.index(ticker)] +
                                    weights['market_cap'] * normalized_market_caps[stocks_tickers.index(ticker)] +
                                    weights['volume'] * normalized_volumes[stocks_tickers.index(ticker)])
    
    sorted_composite_scores = sorted(composite_scores.items(), key=lambda x: x[1], reverse=True)
    
    top_stocks_performers = [{'name': name, 'score': score, 'change': stocks_percentage_changes[name], 'market_cap': stocks_market_caps[name], 'volume': stocks_volumes[name]} for name, score in sorted_composite_scores[:10]]

    context = {
        'top_indices_performers': top_indices_performers,
        'top_stocks_performers': top_stocks_performers
    }

    return render(request, 'stockist/top_performers.html', context)


@login_required
def upload_file(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to upload files.")
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/')
    else:
        form = UploadFileForm()
    return render(request, 'stockist/upload.html', {'form': form})

def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, f.name)
    
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    df = pd.read_excel(file_path)
    df = clean_data(df)
    ranked_companies = rank_companies(df)
    save_ranked_companies(ranked_companies)

def clean_data(df):
    # Rename columns by replacing spaces with underscores
    df = df.rename(columns=lambda x: x.strip().replace(" ", "_").replace("Company_Name", "company_name"))

    numeric_columns = [
        'Price_Performance_(52_Weeks)',
        'Total_Return_(1_Yr_Annualized)',
        'Beta_(1_Year_Annualized)',
        'Standard_Deviation_(1_Yr_Annualized)'
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=numeric_columns)

    return df


def rank_companies(df):
    df['Score'] = (
        df['Price_Performance_(52_Weeks)'] +
        df['Total_Return_(1_Yr_Annualized)'] +
        (1 - df['Beta_(1_Year_Annualized)']) -
        df['Standard_Deviation_(1_Yr_Annualized)']
    )
    
    df = df.sort_values(by='Score', ascending=False)
    return df[['company_name', 'Score']].to_dict('records')

def save_ranked_companies(ranked_companies):
    with open(os.path.join(settings.MEDIA_ROOT, 'ranked_companies.json'), 'w') as f:
        json.dump(ranked_companies, f)

@login_required
def display_ranked_companies(request):
    with open(os.path.join(settings.MEDIA_ROOT, 'ranked_companies.json'), 'r') as f:
        ranked_companies = json.load(f)
    print(ranked_companies)
    return render(request, 'stockist/ranked_companies.html', {
        'companies': ranked_companies,
        'user': request.user,
        'form': UploadFileForm()
    })

def success(request):
    return render(request, 'stockist/success.html')