import yfinance as yf
import pandas as pd
import ta

def analyze_stocks(tickers):
    results = []

    for ticker in tickers:
        try:
            # Download 60 trading days (~3 months)
            df = yf.download(ticker, period='60d', interval='1d', auto_adjust=True)

            if df.shape[0] < 10:
                print(f"{ticker}: Not enough data")
                continue

            # Calculate RSI (14-day)
            df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()

            # Loop through data starting from the 6th row to ensure we have 5 previous days for volume avg
            for i in range(5, len(df)):
                last_5_avg_volume = df['Volume'].iloc[i-5:i].mean()
                today_volume = df['Volume'].iloc[i]
                today_close = df['Close'].iloc[i]
                prev_close = df['Close'].iloc[i-1]
                today_rsi = df['RSI'].iloc[i]

                volume_condition = today_volume >= 5 * last_5_avg_volume
                price_condition = today_close > prev_close
                rsi_condition = today_rsi < 70

                if volume_condition and price_condition and rsi_condition:
                    alert_date = df.index[i].strftime('%Y-%m-%d')
                    results.append((ticker, alert_date))
                    print(f"{ticker}: Alert on {alert_date} (Volume spike + Price up + RSI {today_rsi:.2f})")
                    break  # Stop after first alert to avoid duplicates

        except Exception as e:
            print(f"{ticker}: Error - {e}")

    return results

# 🔽 Example midcap stock list (10 tickers for demo - replace with full list of 200 if needed)
tickers = [
    'TTML.NS', 'UCOBANK.NS', 'VGUARD.NS', 'VBL.NS', 'ZUARI.NS',
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'LT.NS'
]

alerts = analyze_stocks(tickers)
print("\n✅ Final Alert List:")
for ticker, date in alerts:
    print(f"{ticker} → Alert on {date}")
