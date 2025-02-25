import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def get_world_indices():
    """
    Get major world indices data
    """
    indices = {
        '^GSPC': 'S&P 500',
        '^DJI': 'Dow Jones',
        '^IXIC': 'NASDAQ',
        '^FTSE': 'FTSE 100',
        '^N225': 'Nikkei 225',
        '^HSI': 'Hang Seng',
        '^GDAXI': 'DAX',
        '^FCHI': 'CAC 40'
    }

    data = []
    for symbol, name in indices.items():
        try:
            index = yf.Ticker(symbol)
            hist = index.history(period='2d')  # Get 2 days of data to calculate change
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change = current - prev_close
                change_pct = (change / prev_close) * 100

                data.append({
                    'Index': name,
                    'Price': f"{current:,.2f}",
                    'Change': f"{change:+,.2f}",
                    'Change %': f"{change_pct:+,.2f}%",
                    'Change_Color': 'green' if change_pct > 0 else 'red'
                })
        except Exception as e:
            print(f"Error fetching {name}: {str(e)}")
            continue

    return pd.DataFrame(data)

def get_top_movers():
    """
    Get top gainers and losers for the day
    """
    gainers = []
    losers = []

    # List of major stocks to check
    stocks = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM',
        'V', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'BAC', 'XOM', 'PFE', 'DIS',
        'NFLX', 'COIN', 'AMD', 'INTC', 'CSCO', 'VZ', 'T', 'PEP', 'KO',
        'ADBE', 'CRM', 'ORCL'
    ]

    for symbol in stocks:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='2d')  # Get 2 days of data
            info = stock.info

            if len(hist) >= 2 and info and 'longName' in info:
                current = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change = current - prev_close
                change_pct = (change / prev_close) * 100

                data = {
                    'Symbol': symbol,
                    'Name': info['longName'],
                    'Price': f"${current:,.2f}",
                    'Change': f"${change:+,.2f}",
                    'Change %': f"{change_pct:+,.2f}%",
                    'Change_Color': 'green' if change_pct > 0 else 'red'
                }

                if change_pct > 0:
                    gainers.append((change_pct, data))
                else:
                    losers.append((change_pct, data))
        except Exception as e:
            print(f"Error fetching {symbol}: {str(e)}")
            continue

    # Sort and get top 10
    gainers = sorted(gainers, key=lambda x: x[0], reverse=True)
    losers = sorted(losers, key=lambda x: x[0])

    top_gainers = pd.DataFrame([x[1] for x in gainers[:10]])
    top_losers = pd.DataFrame([x[1] for x in losers[:10]])

    return top_gainers, top_losers

def search_stock(query):
    """
    Search for stocks by symbol or name
    """
    try:
        # Try direct symbol lookup first
        try:
            stock = yf.Ticker(query)
            info = stock.info
            if info and 'longName' in info and 'symbol' in info:
                print(f"Found direct match: {info['symbol']} - {info['longName']}")
                return [(info['symbol'], info['longName'])]
        except Exception as e:
            print(f"Direct lookup failed: {str(e)}")

        # Try common variations for name search
        variations = [
            query,  # Original query
            query.upper(),  # Uppercase
            query.replace(" ", "-"),  # Replace spaces with hyphens
            query.replace(" ", ""),  # Remove spaces
            query.lower(),  # Lowercase
            ' '.join(word.capitalize() for word in query.split())  # Title Case
        ]

        results = []
        seen_symbols = set()

        for variation in variations:
            print(f"Trying variation: {variation}")
            try:
                # Try with common exchange suffixes
                suffixes = ['', '.DE', '.L', '.PA', '.MI', '.MC']
                for suffix in suffixes:
                    try:
                        stock = yf.Ticker(f"{variation}{suffix}")
                        info = stock.info
                        if info and 'longName' in info and 'symbol' in info:
                            symbol = info['symbol']
                            if symbol not in seen_symbols:
                                seen_symbols.add(symbol)
                                print(f"Found match: {symbol} - {info['longName']}")
                                results.append((symbol, info['longName']))
                    except Exception as e:
                        print(f"Error with suffix {suffix}: {str(e)}")
                        continue

            except Exception as e:
                print(f"Error searching variation {variation}: {str(e)}")
                continue

        # If no results found, try searching for similar names
        if not results:
            common_stocks = {
                'AAPL': 'Apple',
                'MSFT': 'Microsoft',
                'GOOGL': 'Google',
                'AMZN': 'Amazon',
                'NVDA': 'NVIDIA',
                'META': 'Meta',
                'TSLA': 'Tesla',
                'NFLX': 'Netflix'
            }

            query_lower = query.lower()
            for symbol, name in common_stocks.items():
                if query_lower in name.lower():
                    try:
                        stock = yf.Ticker(symbol)
                        info = stock.info
                        if info and 'longName' in info:
                            results.append((symbol, info['longName']))
                            print(f"Found common stock match: {symbol} - {info['longName']}")
                    except Exception as e:
                        print(f"Error checking common stock {symbol}: {str(e)}")

        return results
    except Exception as e:
        print(f"Error searching for stock: {str(e)}")
        return []

def get_stock_data(symbol, period='1y'):
    """
    Fetch stock data from Yahoo Finance
    Args:
        symbol: Stock symbol
        period: Time period (1d, 5d, 1mo, 6mo, ytd, 1y, 5y, max)
    """
    try:
        stock = yf.Ticker(symbol)
        # Use 1m intervals for intraday data
        interval = '1m' if period in ['1d', '5d'] else '1d'
        hist = stock.history(period=period, interval=interval)
        info = stock.info
        return hist, info
    except Exception as e:
        print(f"Error fetching stock data: {str(e)}")
        return None, None

def create_price_chart(df):
    """
    Create interactive price charts using Plotly
    """
    # Create subplots
    fig = go.Figure()

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick',
        visible=True
    ))

    # Area chart (mountain)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        fill='tozeroy',
        name='Area',
        visible=False
    ))

    # Baseline chart
    baseline = df['Close'].iloc[0]
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        name='Baseline',
        line=dict(color='blue'),
        visible=False
    ))
    fig.add_hline(y=baseline, line_dash="dash", line_color="red", name="Baseline")

    # Add tabs for chart types
    fig.update_layout(
        tabs = [
            dict(
                label = 'Candlestick',
                method = 'update',
                args = [{'visible': [True, False, False]}, {}]
            ),
            dict(
                label = 'Area',
                method = 'update',
                args = [{'visible': [False, True, False]}, {}]
            ),
            dict(
                label = 'Baseline',
                method = 'update',
                args = [{'visible': [False, False, True]}, {}]
            )
        ],
        yaxis_title='Price',
        template='plotly_white',
        xaxis_rangeslider_visible=False,
        height=600
    )

    return fig

def format_large_number(num):
    """
    Format large numbers for display
    """
    if num >= 1e12:
        return f'{num/1e12:.2f}T'
    if num >= 1e9:
        return f'{num/1e9:.2f}B'
    if num >= 1e6:
        return f'{num/1e6:.2f}M'
    return f'{num:,.0f}'

def prepare_metrics_data(info):
    """
    Prepare key metrics for display
    """
    metrics = {
        'Market Cap': format_large_number(info.get('marketCap', 0)),
        'P/E Ratio': f"{info.get('trailingPE', 0):.2f}",
        '52 Week High': f"${info.get('fiftyTwoWeekHigh', 0):.2f}",
        '52 Week Low': f"${info.get('fiftyTwoWeekLow', 0):.2f}",
        'Volume': format_large_number(info.get('volume', 0)),
        'Dividend Yield': f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else 'N/A'
    }
    return metrics

def prepare_table_data(hist):
    """
    Prepare data for table display and CSV export
    """
    df = hist.copy()
    df = df.round(2)
    df.index = df.index.strftime('%Y-%m-%d')
    return df