import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Crypto Live Dashboard", layout="wide")

st.title("🚀 CRYPTO LIVE PRO DASHBOARD")
st.caption("👨‍💻 Developer: Bilal Ali (Shebi)")

coin = st.sidebar.selectbox("Select Coin", ["BTC", "ETH", "PAXG", "ZEC", "SOL", "BNB"], index=0)

def get_binance_klines(symbol: str, interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}USDT&interval={interval}&limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
            ])
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)
            return df
        else:
            # Fallback API agar Binance main API block ho
            backup_url = f"https://api1.binance.com/api/v3/klines?symbol={symbol.upper()}USDT&interval={interval}&limit={limit}"
            resp = requests.get(backup_url, headers=headers, timeout=10)
            data = resp.json()
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
            ])
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)
            return df
    except Exception:
        return None

df_1h = get_binance_klines(coin, interval="1h")

if df_1h is not None and not df_1h.empty:
    live_price = df_1h['close'].iloc[-1]
    
    # RSI Calculation
    delta = df_1h['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = (100 - (100 / (1 + rs))).iloc[-1]

    # Target & Stop Loss Predictions
    tp_pred = live_price * 1.025
    sl_pred = live_price * 0.985

    st.markdown("### 🎯 Live Predictions & Signals")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.warning(f"🟡 SAFE ENTRY\n\n### ${live_price:,.4f}")
    with col2:
        st.success(f"🟢 TAKE PROFIT (TP)\n\n### ${tp_pred:,.4f}")
    with col3:
        st.error(f"🔴 STOP LOSS (SL)\n\n### ${sl_pred:,.4f}")

    st.divider()

    st.markdown("### 📊 Live Technical Indicators")
    ind_col1, ind_col2, ind_col3 = st.columns(3)

    with ind_col1:
        st.info(f"**RSI (14)**: {rsi:.2f}")
    with ind_col2:
        ema20 = df_1h['close'].ewm(span=20, adjust=False).mean().iloc[-1]
        st.info(f"**EMA 20**: ${ema20:,.2f}")
    with ind_col3:
        vol = df_1h['volume'].iloc[-1]
        st.info(f"**Live Volume**: {vol:,.2f}")

else:
    st.error("Live Data Fetch Nahi Ho Saka! Re-checking connection...")

time.sleep(5)
st.rerun()
