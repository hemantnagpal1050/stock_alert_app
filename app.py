# app.py
import streamlit as st
import pandas as pd
import yfinance as yf

st.title("📊 Stock Volume + RSI Alert")

# Sample ticker input
tickers = st.text_input("Enter stock tickers (comma separated):", "RELIANCE.NS, TCS.NS")

if st.button("Analyze"):
    tickers = [ticker.strip().upper() for ticker in tickers.split(',') if ticker.strip()]
    st.write("Analyzing:", tickers)

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="2mo")
            st.write(f"Showing data for {ticker}:")
            st.dataframe(df.tail())
        except Exception as e:
            st.error(f"{ticker}: Error - {e}")
