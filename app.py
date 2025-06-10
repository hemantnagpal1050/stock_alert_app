import yfinance as yf
import pandas as pd

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def is_rsi_rising(ticker):
    try:
        # Weekly RSI
        weekly_data = yf.download(ticker, period="6mo", interval="1wk", progress=False)
        if weekly_data.empty or len(weekly_data) < 15:
            return f"{ticker}: Not enough weekly data"
        weekly_rsi = calculate_rsi(weekly_data['Close'])
        if weekly_rsi.iloc[-1] <= weekly_rsi.iloc[-2]:
            return f"{ticker}: ❌ RSI not rising weekly"

        # Monthly RSI
        monthly_data = yf.download(ticker, period="2y", interval="1mo", progress=False)
        if monthly_data.empty or len(monthly_data) < 15:
            return f"{ticker}: Not enough monthly data"
        monthly_rsi = calculate_rsi(monthly_data['Close'])
        if monthly_rsi.iloc[-1] <= monthly_rsi.iloc[-2]:
            return f"{ticker}: ❌ RSI not rising monthly"

        return f"{ticker}: ✅ RSI rising on both weekly and monthly"

    except Exception as e:
        return f"{ticker}: Error - {e}"

# Example usage
tickers = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
for ticker in tickers:
    print(is_rsi_rising(ticker))
