from django.shortcuts import render
from django.core.cache import cache
from datetime import datetime, timedelta
from .forms import StockForm
import json
import logging
import yfinance as yf
import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd

logger = logging.getLogger(__name__)

def stock_analysis(request):
    symbol_data = {}
    compare_data = {}
    symbols = None
    period = None

    if request.method == 'POST':
        if 'symbol' in request.POST:
            form = StockForm(request.POST)
            if form.is_valid():
                symbol = form.cleaned_data['symbol']
                cache_key = f'stock_data_{symbol}'
                cached_data = cache.get(cache_key)
                if cached_data:
                    symbol_data['data'] = cached_data
                    logger.info(f"Data retrieved from cache for symbol: {symbol}")
                else:
                    try:
                        stock_data = yf.Ticker(symbol).history(period='max')
                        if stock_data.empty:
                            raise ValueError(f"No data found for symbol: {symbol}")
                        data = []
                        for index, row in stock_data.iterrows():
                            data_point = {
                                'Date': index.strftime('%Y-%m-%d'),
                                'Open': float(row['Open']),
                                'High': float(row['High']),
                                'Low': float(row['Low']),
                                'Close': float(row['Close']),
                                'Volume': float(row['Volume'])
                            }
                            data.append(data_point)
                        cache.set(cache_key, data, timeout=60*60)  # Cache for 1 hour
                        symbol_data['data'] = data
                    except Exception as e:
                        logger.error(f"Error fetching data for {symbol}: {e}")
                        error_message = f"Error fetching data for {symbol}: {str(e)}"
                        return render(request, 'analyst/error.html', {'error_message': error_message})
                symbol_data['displayed_data'] = json.dumps(symbol_data['data'])
                symbol_data['symbol'] = symbol
            else:
                logger.warning(f"Invalid form submission: {form.errors}")
        
        if 'symbols' in request.POST:
            active_tab = 'compare'
            symbols = request.POST.get('symbols')
            period = request.POST.get('period')

            if symbols:
                symbols = [symbol.strip().upper() for symbol in symbols.split(',')]
                data = []
                end_date = datetime.now()

                try:
                    for symbol in symbols:
                        start_date = calculate_start_date(period, end_date)
                        stock_data = fetch_stock_data(symbol, start_date, end_date)
                        if stock_data is None or stock_data.empty:
                            raise ValueError(f"No data available for {symbol} for the selected period")
                        trace = go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name=symbol)
                        data.append(trace)
                except Exception as e:
                    logger.error(f"Error fetching comparison data: {e}")
                    return render(request, 'analyst/error.html', {'error_message': str(e)})

                layout = go.Layout(
                    title='Stock Price Comparison',
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='Close Price')
                )
                fig = go.Figure(data=data, layout=layout)
                compare_data['plot_div'] = plot(fig, output_type='div', include_plotlyjs=False)
                compare_data['symbols'] = symbols
                compare_data['period'] = period
            else:
                logger.warning("No symbols provided for comparison")

    context = {
        "active_tab": 'compare',
        "symbol_data": symbol_data,
        "compare_data": compare_data,
    }
    return render(request, 'analyst/stock_analysis.html', context)

def calculate_start_date(period, end_date):
    if period == 'monthly':
        return end_date - timedelta(days=30)
    elif period == 'quarterly':
        return end_date - timedelta(days=90)
    elif period == 'half-yearly':
        return end_date - timedelta(days=180)
    elif period == 'yearly':
        return end_date - timedelta(days=365)
    elif period == 'ytd':
        return datetime(end_date.year, 1, 1)
    else:
        return None

def fetch_stock_data(symbol, start_date, end_date):
    try:
        if start_date is None:
            stock_data = yf.Ticker(symbol).history(period='max')
        else:
            stock_data = yf.Ticker(symbol).history(start=start_date, end=end_date)
        stock_data.index = pd.to_datetime(stock_data.index)
        return stock_data
    except Exception as e:
        logger.error(f"Error fetching data for symbol {symbol}: {e}")
        return None