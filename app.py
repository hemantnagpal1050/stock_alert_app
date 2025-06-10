import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta

st.set_page_config(page_title="Volume + RSI Spike Scanner", layout="wide")
st.title("📊 Volume Spike + RSI Momentum Screener")

# Define RSI thresholds
RSI_OVERBOUGHT = 70

# Get ticker list input
tickers_input = st.text_area("Enter up to 200 stock symbols (comma-separated):", 
"RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, LT.NS, SBIN.NS, BAJAJFINSV.NS, "
"AXISBANK.NS, BHARTIARTL.NS, ITC.NS, DABUR.NS, M&M.NS, TATAPOWER.NS, SUNPHARMA.NS, "
"ADANIPOWER.NS, ADANIENT.NS, LICHSGFIN.NS, CHOLAFIN.NS, CUMMINSIND.NS, BHEL.NS, TVSMOTOR.NS, "
"POLYCAB.NS, CROMPTON.NS, VGUARD.NS, IRCTC.NS, IRFC.NS, NHPC.NS, HUDCO.NS, BALKRISIND.NS, "
"MPHASIS.NS, COFORGE.NS, PERSISTENT.NS, NAVINFLUOR.NS, IEX.NS, ASTRAL.NS, AARTIIND.NS, "
"GUJGASLTD.NS, GSPL.NS, VBL.NS, ZEEL.NS, CESC.NS, JUBLFOOD.NS, DELHIVERY.NS")

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

def compute_rsi(series, period):
    return RSIIndicator(close=series, window=period).rsi()

def check_conditions(ticker):
    try:
        df_daily = yf.download(ticker, period='60d', interval='1d', progress=False)
        if df_daily.empty or len(df_daily) < 30:
            return None

        df_daily.dropna(inplace=True)

        # Compute RSI
        df_daily["RSI"] = compute_rsi(df_daily["Close"], 14)

        # Current day condition
        today_close = df_daily["Close"].iloc[-1]
        yesterday_close = df_daily["Close"].iloc[-2]
        rsi_today = df_daily["RSI"].iloc[-1]

        if today_close <= yesterday_close or rsi_today >= RSI_OVERBOUGHT:
            return None

        # Volume spike
        avg_volume = df_daily["Volume"].iloc[-6:-1].mean()  # last 5 days avg (excluding today)
        volume_spike = df_daily["Volume"].iloc[-1] >= 5 * avg_volume

        if not volume_spike:
            return None

        # Weekly and Monthly RSI trend
        df_weekly = yf.download(ticker, period='6mo', interval='1wk', progress=False)
        df_monthly = yf.download(ticker, period='2y', interval='1mo', progress=False)

        if df_weekly.empty or df_monthly.empty:
            return None

        df_weekly["RSI"] = compute_rsi(df_weekly["Close"], 14)
        df_monthly["RSI"] = compute_rsi(df_monthly["Close"], 14)

        if len(df_weekly["RSI"].dropna()) < 2 or len(df_monthly["RSI"].dropna()) < 2:
            return None

        weekly_rising = df_weekly["RSI"].iloc[-1] > df_weekly["RSI"].iloc[-2]
        monthly_rising = df_monthly["RSI"].iloc[-1] > df_monthly["RSI"].iloc[-2]

        if not (weekly_rising and monthly_rising):
            return None

        return {
            "Ticker": ticker,
            "Close": today_close,
            "Volume": df_daily["Volume"].iloc[-1],
            "Avg Volume": avg_volume,
            "RSI": round(rsi_today, 2),
        }

    except Exception as e:
        return f"{ticker}: Error - {e}"

if st.button("🔍 Run Screener"):
    with st.spinner("Fetching and analyzing data..."):
        results = []
        errors = []

        for ticker in tickers:
            result = check_conditions(ticker)
            if isinstance(result, dict):
                results.append(result)
            elif isinstance(result, str) and "Error" in result:
                errors.append(result)

        if results:
            st.success("✅ Stocks matching all conditions:")
            st.dataframe(pd.DataFrame(results).set_index("Ticker"))
        else:
            st.warning("⚠️ No stocks met all the conditions.")

        if errors:
            with st.expander("⚠️ Errors (click to expand)"):
                for e in errors:
                    st.text(e)
