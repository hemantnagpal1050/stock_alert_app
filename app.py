import yfinance as yf
import pandas as pd
import numpy as np
import ta
import streamlit as st

st.title("📈 Volume Spike + RSI Alert System")

tickers_input = st.text_area("Enter comma-separated stock symbols (e.g., RELIANCE.NS, TCS.NS):", "RELIANCE.NS, TCS.NS, HDFCBANK.NS")
tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period='60d', interval='1d')
        if df.empty or len(df) < 30:
            return f"{ticker}: Not enough data"

        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()

        alerts = []

        for i in range(30, len(df)):
            week_volume = df['Volume'].iloc[i-7:i].sum()
            past_5_weeks_volume_avg = []

            for w in range(1, 6):
                start = i - 7 * (w + 1)
                end = i - 7 * w
                if start < 0: continue
                past_5_weeks_volume_avg.append(df['Volume'].iloc[start:end].sum())

            if len(past_5_weeks_volume_avg) < 5:
                continue

            avg_volume = np.mean(past_5_weeks_volume_avg)
            price_up = df['Close'].iloc[i] > df['Close'].iloc[i-1]
            rsi_ok = df['RSI'].iloc[i] < 70

            if week_volume >= 5 * avg_volume and price_up and rsi_ok:
                alerts.append(df.index[i].strftime('%Y-%m-%d'))

        if alerts:
            return f"{ticker}: Alerts on {alerts}"
        else:
            return f"{ticker}: No signal"
    except Exception as e:
        return f"{ticker}: Error - {e}"

if st.button("Run Strategy"):
    with st.spinner("Analyzing..."):
        results = [analyze_stock(ticker) for ticker in tickers]
    st.subheader("📊 Results")
    for res in results:
        st.write(res)
