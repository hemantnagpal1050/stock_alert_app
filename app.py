import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator

st.set_page_config(page_title="📈 5-Min RSI + Volume Spike Scanner", layout="wide")
st.title("📈 RSI Rising + Volume Spike (5-Min) Scanner")

tickers_input = st.text_area("Enter stock tickers (comma-separated):", "RELIANCE.NS, TCS.NS, HDFCBANK.NS")

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

def fetch_intraday_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m", progress=False)
        if df.empty or len(df) < 15:
            return None, "Not enough data"
        df.dropna(inplace=True)
        df["RSI"] = RSIIndicator(df["Close"], window=14).rsi()
        return df, None
    except Exception as e:
        return None, str(e)

def check_conditions(df):
    if df["RSI"].iloc[-1] > df["RSI"].iloc[-2]:  # RSI rising
        recent_vol = df["Volume"].iloc[-1]
        avg_vol = df["Volume"].iloc[-11:-1].mean()
        if recent_vol >= 3 * avg_vol:
            return True, recent_vol, avg_vol, df["RSI"].iloc[-1]
    return False, None, None, None

if st.button("🔍 Scan Now"):
    matching_stocks = []
    errors = []

    for ticker in tickers:
        df, err = fetch_intraday_data(ticker)
        if err:
            errors.append(f"{ticker}: {err}")
            continue

        passed, v_spike, v_avg, rsi = check_conditions(df)
        if passed:
            matching_stocks.append({
                "Ticker": ticker,
                "Volume": int(v_spike),
                "Avg Volume": int(v_avg),
                "RSI": round(rsi, 2)
            })

    if matching_stocks:
        st.success("✅ Stocks with RSI rising and volume spike:")
        st.dataframe(pd.DataFrame(matching_stocks).set_index("Ticker"))
    else:
        st.info("No matching stocks found.")

    if errors:
        with st.expander("⚠️ Errors (click to view)"):
            for err in errors:
                st.text(err)
