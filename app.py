import yfinance as yf
import pandas as pd
import ta
from datetime import datetime


def fetch_stock_data(ticker):
    df = yf.download(ticker, period="60d", interval="1d", auto_adjust=True)
    if df.empty or len(df) < 30:
        raise ValueError("Not enough data")

    df = df[['Close', 'Volume']].dropna()

    # Calculate RSI
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    return df.dropna()


def check_conditions(df):
    alerts = []

    for i in range(30, len(df)):
        current_day = df.iloc[i]
        prev_day = df.iloc[i - 1]
        week_volume = df['Volume'].iloc[i-6:i+1].sum()
        prev_5_week_volume = df['Volume'].iloc[i-35:i-6].sum() / 5 if i >= 35 else 0

        # Condition 1: Last week volume is 5x of last 5 weeks avg volume
        volume_spike = week_volume >= 5 * prev_5_week_volume if prev_5_week_volume > 0 else False

        # Condition 2: Current close > previous close
        price_up = current_day['Close'] > prev_day['Close']

        # Condition 3: RSI not overbought (i.e., < 70)
        rsi_ok = current_day['RSI'] < 70

        if volume_spike and price_up and rsi_ok:
            alerts.append((df.index[i].strftime('%Y-%m-%d')))

    return alerts


def analyze_stocks(tickers):
    final_alerts = {}

    for ticker in tickers:
        try:
            df = fetch_stock_data(ticker)
            alert_dates = check_conditions(df)
            if alert_dates:
                final_alerts[ticker] = alert_dates
        except Exception as e:
            print(f"{ticker}: Error - {e}")

    return final_alerts


# Example list of stocks (you can replace with Nifty Midcap 100)
tickers = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'LT.NS',
    'KOTAKBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'ITC.NS', 'INFY.NS'
]

alerts = analyze_stocks(tickers)

print("\nStock Alerts (Volume Spike + RSI Strategy):")
for stock, dates in alerts.items():
    print(f"{stock}: Alert Dates: {dates}")
