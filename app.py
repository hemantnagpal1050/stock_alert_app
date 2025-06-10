import yfinance as yf
import pandas as pd
import streamlit as st
import ta  # Make sure to install the 'ta' package: pip install ta

def fetch_data(ticker):
    df = yf.download(ticker, period="45d", interval="1d", auto_adjust=True)
    df = df[['Close', 'Volume']].dropna()
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    return df

def check_conditions(df):
    alerts = []
    for i in range(30, len(df)):
        last_5_week_volume_avg = df['Volume'].iloc[i-5:i].mean()
        current_volume = df['Volume'].iloc[i]
        current_close = df['Close'].iloc[i]
        prev_close = df['Close'].iloc[i-1]
        current_rsi = df['RSI'].iloc[i]

        if current_volume >= 5 * last_5_week_volume_avg and current_close > prev_close and current_rsi < 70:
            alerts.append((df.index[i].date(), current_volume, current_close, current_rsi))
    return alerts

st.title("📊 Volume Spike + RSI Strategy")

stock_input = st.text_area("Enter stock symbols (comma separated):", "RELIANCE.NS, TCS.NS, HDFCBANK.NS")
tickers = [s.strip().upper() for s in stock_input.split(',') if s.strip()]

if st.button("Run Strategy"):
    with st.spinner("Analyzing stocks..."):
        alert_results = {}
        for ticker in tickers:
            try:
                df = fetch_data(ticker)
                alerts = check_conditions(df)
                if alerts:
                    alert_results[ticker] = alerts
            except Exception as e:
                st.warning(f"{ticker}: Error - {e}")

        if alert_results:
            st.success("Stocks that matched the alert conditions:")
            for ticker, alerts in alert_results.items():
                st.write(f"**{ticker}**")
                st.dataframe(pd.DataFrame(alerts, columns=["Date", "Volume", "Close", "RSI"]))
        else:
            st.info("No stocks matched the conditions.")
