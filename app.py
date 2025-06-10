import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

def fetch_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_stocks(tickers):
    results = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, period='60d', interval='1d', auto_adjust=True)
            if df.empty or len(df) < 30:
                st.warning(f"{ticker}: Not enough data")
                continue

            df['RSI'] = fetch_rsi(df['Close'])
            df['Volume_5W_Avg'] = df['Volume'].rolling(window=5).mean()

            for i in range(5, len(df)):
                volume_spike = df['Volume'].iloc[i] >= 5 * df['Volume_5W_Avg'].iloc[i]
                price_up = df['Close'].iloc[i] > df['Close'].iloc[i - 1]
                rsi_ok = df['RSI'].iloc[i] < 70

                if volume_spike and price_up and rsi_ok:
                    results.append((ticker, df.index[i].date()))
                    break

        except Exception as e:
            st.error(f"{ticker}: Error - {e}")

    return results

st.title("📈 Volume Spike + RSI Screener")

tickers_input = st.text_area("Enter stock tickers (comma-separated)", 
                             "RELIANCE.NS, TCS.NS, HDFCBANK.NS")
tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

if st.button("Run Screener"):
    with st.spinner("Analyzing..."):
        alerts = analyze_stocks(tickers)
        if alerts:
            st.success("📢 Alerts:")
            for ticker, date in alerts:
                st.write(f"**{ticker}** triggered alert on **{date}**")
        else:
            st.info("No alerts found.")
