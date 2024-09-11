import yfinance as yf
import logging
import re

# Configure logging
logging.basicConfig(
    filename='stock_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
def get_stock_data(symbols):
    data = []
    errors = []
    stock_data = []
    flagged_for_review = []

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if the necessary data is present
            if 'currentPrice' not in info or 'previousClose' not in info:
                logging.warning(f"Data missing for symbol: {symbol}. Skipping this symbol.")
                continue  # Skip this symbol if essential data is missing
            
            current_price = info.get('currentPrice', 'N/A')
            previous_close = info.get('previousClose', 'N/A')
            
            if info.get('regularMarketChangePercent') is not None:
                change_percent = info['regularMarketChangePercent']
            else:
                if previous_close and previous_close > 0:
                    change_percent = ((current_price - previous_close) / previous_close) * 100
                else:
                    change_percent = 'N/A'
            # Flag for review if change_percent is greater than 5000
            if change_percent != 'N/A' and change_percent > 500:
                flagged_for_review.append({
                    'symbol': symbol,
                    'change_percent': change_percent
                })
                logging.warning(f"Stock {symbol} flagged for review. Change percent: {change_percent}")
                continue 
            
            # Retrieve relevant data from stock info
            volume = info.get('regularMarketVolume', 0)
            avg_volume_10d = info.get('averageVolume10days', 0)
            day_high = info.get('dayHigh', 0)
            day_low = info.get('dayLow', 0)
            volatility = ((day_high - day_low) / day_low) * 100 if day_low != 0 else 0  # Avoid division by zero
            beta = info.get('beta', 1)
            market_cap = info.get('marketCap', 0)
            price_to_sales = info.get('priceToSalesTrailing12Months', 0)
            total_revenue = info.get('totalRevenue', 0)
            profit_margin = info.get('profitMargins', 0)
            fifty_two_week_high = info.get('fiftyTwoWeekHigh', 0)
            fifty_two_week_low = info.get('fiftyTwoWeekLow', 0)
            debt_to_equity = info.get('debtToEquity', 0)
            recommendation = info.get('recommendationMean', 'N/A')

            # Calculate long-term volatility
            fifty_two_week_range = ((fifty_two_week_high - fifty_two_week_low) / fifty_two_week_low) * 100 if fifty_two_week_low != 0 else 0

            # Calculate enhanced activity score
            activity_score = 0
            if volume and volatility:
                activity_score += (volume * volatility)  # Core activity: volume & volatility
            if avg_volume_10d:
                activity_score += (avg_volume_10d * 0.5)  # Weight the average volume to smooth out daily fluctuations
            if beta:
                activity_score += (beta * 0.3)  # Add some weight based on market volatility
            if market_cap:
                activity_score += (market_cap * 0.1)  # Higher market cap stocks are generally more stable but less volatile
            if fifty_two_week_range:
                activity_score += (fifty_two_week_range * 0.2)  # Consider long-term price swings
            if price_to_sales:
                activity_score += (price_to_sales * 0.05)  # Lower price-to-sales may attract value investors
            if profit_margin:
                activity_score += (profit_margin * 0.05)  # Consider profitability
            if debt_to_equity:
                activity_score += (1 / debt_to_equity) * 0.1  # Higher debt could mean more risk, inversely affecting activity

            # Final check to ensure activity score is valid
            activity_score = activity_score if activity_score > 0 else 'N/A'

            # Calculate enhanced score
            if change_percent != 'N/A':
                score = change_percent  # Start with price change percentage
                if volume:
                    score += volume * 0.001  # Small weight for volume
                if fifty_two_week_high and fifty_two_week_low:
                    score += ((fifty_two_week_high - fifty_two_week_low) / fifty_two_week_low) * 0.05  # Slight weight for long-term volatility
                if recommendation != 'N/A':
                    score -= recommendation * 2  # Stronger weight for better recommendations

                enhanced_score = score
            else:
                enhanced_score = 'N/A'

            
            stock = {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'current_price': current_price,
                'market_cap': market_cap,
                'change_percent': change_percent,
                'volume': volume,
                'volatility': volatility,
                'activity_score': activity_score,
                'enhanced_score': enhanced_score
            }
            data.append(stock)  # Append to data list
            stock_data.append(stock)

        except ValueError as ve:
            errors.append(str(ve))
            logging.error(str(ve))
        except Exception as e:
            error_message = f"Error fetching data for {symbol}: {str(e)}"
            errors.append(error_message)
            logging.error(error_message)
    
    # Sorting the data based on activity score
    most_active = sorted(stock_data, key=lambda x: x.get('activity_score', 0), reverse=True)[:5]
    top_gainers = sorted([s for s in stock_data if s['change_percent'] != 'N/A'],
                         key=lambda x: x['enhanced_score'], reverse=True)[:5]
    top_losers = sorted([s for s in stock_data if s['change_percent'] != 'N/A'],
                        key=lambda x: x['enhanced_score'])[:5]
    
    return data, errors, most_active, top_gainers, top_losers, flagged_for_review

def validate_stock_symbol(symbol):
    # Simple regex for stock symbol validation (letters, numbers, and some symbols like periods)
    pattern = r'^[A-Z0-9\.\-]{1,5}$'
    return re.match(pattern, symbol) is not None