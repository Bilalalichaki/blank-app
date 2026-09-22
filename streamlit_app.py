import streamlit as st
import requests

# Page Layout
st.set_page_config(page_title="Crypto Live Pro Dashboard", layout="wide")

# Custom UI Styling (Clean Mobile App Look)
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .coin-card {
        background-color: #1a1c23;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        border: 1px solid #2d313e;
    }
    .badge-spot { background-color: #1e3a8a; color: #93c5fd; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .badge-fut { background-color: #581c87; color: #d8b4fe; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .box-entry { background-color: #3e2723; color: #ffe082; padding: 12px; border-radius: 8px; border-left: 4px solid #ffb300; }
    .box-tp { background-color: #1b5e20; color: #a5d6a7; padding: 12px; border-radius: 8px; border-left: 4px solid #66bb6a; }
    .box-sl { background-color: #b71c1c; color: #ef9a9a; padding: 12px; border-radius: 8px; border-left: 4px solid #ef5350; }
</style>
""", unsafe_allow_html=True)

# Header Section
st.title("⚡ ALL CRYPTO PRO DASHBOARD")
st.caption("👨‍💻 Developer: Bilal Ali (Shebi)")

# Coins Database
COINS_DATA = [
    {"symbol": "BTC", "id": "bitcoin"},
    {"symbol": "ETH", "id": "ethereum"},
    {"symbol": "SOL", "id": "solana"},
    {"symbol": "BNB", "id": "binancecoin"},
    {"symbol": "XRP", "id": "ripple"},
    {"symbol": "ADA", "id": "cardano"},
    {"symbol": "DOGE", "id": "dogecoin"},
    {"symbol": "PAXG (Gold)", "id": "pax-gold"},
    {"symbol": "ZEC", "id": "zcash"}
]

# Single Call to Fetch All Data Instantly (No Hanging)
@st.cache_data(ttl=10)
def fetch_all_market_data():
    ids = ",".join([c["id"] for c in COINS_DATA])
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}

market_data = fetch_all_market_data()

# Top Navigation Controls
col_nav1, col_nav2 = st.columns([1, 2])
with col_nav1:
    market_mode = st.radio("Market Type", ["SPOT Market 🛒", "FUTURES Market ⚡"], horizontal=True)
with col_nav2:
    search_query = st.text_input("🔍 Search Coin (e.g. BTC, SOL, Gold)", "")

st.divider()

if not market_data:
    st.warning("⚠️ Market feed sync ho raha hai... Refresh button dabayein.")
    if st.button("🔄 Force Refresh"):
        st.rerun()
else:
    # Filter Coins based on Search
    filtered_coins = [
        c for c in COINS_DATA 
        if search_query.lower() in c["symbol"].lower() or search_query.lower() in c["id"].lower()
    ]

    is_futures = "FUTURES" in market_mode
    badge_html = '<span class="badge-fut">FUTURES ⚡</span>' if is_futures else '<span class="badge-spot">SPOT 🛒</span>'

    # Render All Coins as Cards
    for coin in filtered_coins:
        c_id = coin["id"]
        symbol = coin["symbol"]
        
        c_info = market_data.get(c_id, {})
        price = float(c_info.get("usd", 0))
        change = float(c_info.get("usd_24h_change", 0))
        vol = float(c_info.get("usd_24h_vol", 0))

        if price > 0:
            tp_val = price * 1.025
            sl_val = price * 0.985
            rsi_est = max(15, min(85, 50 + (change * 1.5)))

            # Card Wrapper
            st.markdown(f"### 📌 **{symbol}** / USDT &nbsp; {badge_html}", unsafe_allow_html=True)
            st.write(f"**Live Price:** `${price:,.4f}` | **24h Change:** `{change:+.2f}%` | **Volume:** `${vol:,.0f}`")

            # 3 Color Order Signal Boxes
            b1, b2, b3 = st.columns(3)
            with b1:
                st.markdown(f'<div class="box-entry"><b>🟡 SAFE ENTRY</b><br><span style="font-size:20px;">${price:,.4f}</span></div>', unsafe_allow_html=True)
            with b2:
                st.markdown(f'<div class="box-tp"><b>🟢 TAKE PROFIT (TP)</b><br><span style="font-size:20px;">${tp_val:,.4f}</span></div>', unsafe_allow_html=True)
            with b3:
                st.markdown(f'<div class="box-sl"><b>🔴 STOP LOSS (SL)</b><br><span style="font-size:20px;">${sl_val:,.4f}</span></div>', unsafe_allow_html=True)

            # Indicator Status Row
            trend_str = "🟢 BULLISH" if change > 1 else "🔴 BEARISH" if change < -1 else "🟡 NEUTRAL"
            st.caption(f"📊 **RSI (Est.)**: {rsi_est:.1f} | **Trend Signal**: {trend_str}")
            
            # Futures Calculator inside Expander (Clean UI)
            if is_futures:
                with st.expander(f"⚡ Futures Calculator for {symbol}"):
                    lev = st.slider(f"Leverage (x) - {symbol}", 1, 75, 10)
                    margin = st.number_input(f"Margin ($) - {symbol}", 10.0, value=100.0)
                    pos = margin * lev
                    st.write(f"**Position Size**: `${pos:,.2f}` | **TP Profit**: `+${(tp_val - price) * (pos / price):.2f}` | **SL Risk**: `-${(price - sl_val) * (pos / price):.2f}`")

            st.divider()

    if st.button("🔄 Live Refresh Market"):
        st.rerun()
