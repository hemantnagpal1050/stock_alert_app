import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("📈 Volume Spike + RSI Strategy Alert")

tickers = st.text_area("Enter comma-separated stock tickers (e.g. RELIANCE.NS, TCS.NS)", value="RELIANCE.NS, TCS.NS, HDFCBANK.NS")
tickers = [t.strip() for t in tickers.split(",") if t.strip()]

def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period='30d', interval='1d')
        df.dropna(inplace=True)

        # Fix: ensure close is a 1D float Series
         df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'].squeeze()).rsi()
        df['Prev_Close'] = df['Close'].shift(1)
        df['Volume_5wk_Avg'] = df['Volume'].rolling(window=5).mean()
        df['Volume_Spike'] = df['Volume'] > 5 * df['Volume_5wk_Avg']
        df['Price_Up'] = df['Close'] > df['Prev_Close']
        df['RSI_OK'] = df['RSI'] < 70

        df['Alert'] = df['Volume_Spike'] & df['Price_Up'] & df['RSI_OK']
        alert_dates = df[df['Alert']].index.strftime('%Y-%m-%d').tolist()
        return alert_dates
    except Exception as e:
        return f"Error: {e}"

if st.button("Run Strategy"):
    st.write("## Results")
    for ticker in tickers:
        result = analyze_stock(ticker)
        if isinstance(result, list) and result:
            st.success(f"{ticker}: Condition met on {', '.join(result)}")
        elif isinstance(result, list):
            st.info(f"{ticker}: No alerts in last 30 days")
        else:
            st.error(f"{ticker}: {result}")

