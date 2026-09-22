import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="All Crypto Spot & Futures Dashboard", layout="wide")

st.title("🚀 ALL CRYPTO SPOT & FUTURES LIVE DASHBOARD")
st.caption("👨‍💻 Developer: Bilal Ali (Shebi)")

# Market Type Selector
market_type = st.sidebar.radio("📍 Select Market Type", ["SPOT Market 🛒", "FUTURES Market ⚡"])

# Fetch All Trading Pairs from Binance
@st.cache_data(ttl=60)
def get_all_symbols(is_futures=False):
    try:
        if is_futures:
            url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        else:
            url = "https://api.binance.com/api/v3/exchangeInfo"
            
        res = requests.get(url, timeout=5).json()
        symbols = [s['symbol'] for s in res['symbols'] if s['symbol'].endswith('USDT') and s['status'] == 'TRADING']
        return sorted(symbols)
    except:
        return ["BTCUSDT", "ETHUSDT", "PAXGUSDT", "SOLUSDT", "BNBUSDT", "ZECUSDT"]

is_fut = "FUTURES" in market_type
all_coins = get_all_symbols(is_futures=is_fut)

# Sidebar Coin Search/Select
selected_coin = st.sidebar.selectbox("🔍 Search Any Coin (Spot / Future)", all_coins, index=0)

# Fetch Live Data for Selected Coin
def get_ticker_and_klines(symbol, is_futures=False):
    headers = {"User-Agent": "Mozilla/5.0"}
    base_url = "https://fapi.binance.com" if is_futures else "https://api.binance.com"
    
    try:
        # Live Price & 24h Change
        ticker_url = f"{base_url}/api/v3/ticker/24hr?symbol={symbol}" if not is_futures else f"{base_url}/fapi/v1/ticker/24hr?symbol={symbol}"
        ticker_res = requests.get(ticker_url, headers=headers, timeout=5).json()
        
        # Kline / Candlestick Data for RSI calculation
        kline_url = f"{base_url}/api/v3/klines?symbol={symbol}&interval=1h&limit=50" if not is_futures else f"{base_url}/fapi/v1/klines?symbol={symbol}&interval=1h&limit=50"
        kline_res = requests.get(kline_url, headers=headers, timeout=5).json()
        
        df = pd.DataFrame(kline_res, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'qav', 'trades', 'tb_base', 'tb_quote', 'ignore'])
        df['close'] = df['close'].astype(float)
        
        return float(ticker_res['lastPrice']), float(ticker_res['priceChangePercent']), float(ticker_res['highPrice']), float(ticker_res['lowPrice']), float(ticker_res['volume']), df
    except:
        return None, None, None, None, None, None

price, change, high, low, vol, df = get_ticker_and_klines(selected_coin, is_futures=is_fut)

if price:
    # Calculations
    tp_pred = price * 1.025
    sl_pred = price * 0.985
    
    # RSI Calculation
    if df is not None and not df.empty:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
    else:
        rsi = 50.0

    st.markdown(f"## 📌 Selected Pair: `{selected_coin}` ({market_type})")
    st.markdown(f"### Current Live Price: **${price:,.4f}** | 24h Change: **{change:+.2f}%**")

    # PREDICTION CARDS
    st.markdown("### 🎯 Live Predictions & Order Levels")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.warning(f"🟡 SAFE ENTRY RATE\n\n### ${price:,.4f}")
    with col2:
        st.success(f"🟢 TAKE PROFIT (TP)\n\n### ${tp_pred:,.4f}")
    with col3:
        st.error(f"🔴 STOP LOSS (SL)\n\n### ${sl_pred:,.4f}")

    st.divider()

    # TECHNICAL INDICATORS
    st.markdown("### 📊 Live Technical Indicators")
    i1, i2, i3, i4 = st.columns(4)
    
    with i1:
        st.info(f"**Live RSI (14)**: {rsi:.2f}")
    with i2:
        st.info(f"**24h Resistance (High)**: ${high:,.4f}")
    with i3:
        st.info(f"**24h Support (Low)**: ${low:,.4f}")
    with i4:
        trend = "🟢 STRONG BULLISH" if change > 2 and rsi > 55 else "🔴 BEARISH / DUMP" if change < -2 and rsi < 45 else "🟡 SIDEWAYS / HOLD"
        st.info(f"**Signal Status**: {trend}")

    # Leverage Calculator for Futures
    if is_fut:
        st.divider()
        st.markdown("### ⚡ Futures Leverage & Profit Calculator")
        lev = st.slider("Select Leverage (x)", min_value=1, max_value=75, value=10)
        margin = st.number_input("Margin / Investment ($)", min_value=10.0, value=100.0)
        
        pos_size = margin * lev
        estimated_profit = (tp_pred - price) * (pos_size / price)
        estimated_loss = (price - sl_pred) * (pos_size / price)
        
        st.write(f"💼 **Total Position Size**: `${pos_size:,.2f}`")
        st.write(f"🟢 **Estimated Profit at TP**: `+${estimated_profit:.2f}`")
        st.write(f"🔴 **Estimated Loss at SL**: `-${estimated_loss:.2f}`")

else:
    st.warning("⏳ Live Data Connect Ho Raha Hai... Re-checking Connection.")

# Auto Refresh Every 5 Seconds
time.sleep(5)
st.rerun()
