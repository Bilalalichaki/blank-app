import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="Crypto Live Unlimited Coins", layout="wide")

# Custom Dark UI Styling
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .badge-spot { background-color: #1e3a8a; color: #93c5fd; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .badge-fut { background-color: #581c87; color: #d8b4fe; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .box-entry { background-color: #2e2612; color: #ffe082; padding: 12px; border-radius: 8px; border-left: 4px solid #ffb300; text-align: center; }
    .box-tp { background-color: #122e17; color: #a5d6a7; padding: 12px; border-radius: 8px; border-left: 4px solid #66bb6a; text-align: center; }
    .box-sl { background-color: #3b1414; color: #ef9a9a; padding: 12px; border-radius: 8px; border-left: 4px solid #ef5350; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ UNLIMITED CRYPTO SPOT & FUTURES DASHBOARD")
st.caption("👨‍💻 Developer: Bilal Ali (Shebi)")

# 1. Fetch Top 20 Trending/Popular Coins by Default
@st.cache_data(ttl=15)
def get_top_coins():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1&sparkline=false"
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

# 2. Dynamic Search for ANY Coin in the World
@st.cache_data(ttl=10)
def search_unlimited_coin(query):
    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={query}"
        s_res = requests.get(search_url, timeout=5)
        if s_res.status_code == 200:
            coins = s_res.json().get("coins", [])
            if coins:
                coin_ids = ",".join([c["id"] for c in coins[:10]]) # Get top 10 matching results
                price_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_ids}&sparkline=false"
                p_res = requests.get(price_url, timeout=5)
                if p_res.status_code == 200:
                    return p_res.json()
    except Exception:
        pass
    return []

# Top Control Bar
col1, col2 = st.columns([1, 2])
with col1:
    market_mode = st.radio("Market Mode", ["SPOT Market 🛒", "FUTURES Market ⚡"], horizontal=True)
with col2:
    search_term = st.text_input("🔍 Search Any Coin (e.g. BTC, PEPE, SHIB, FLOKI, NOT, SUI, NEAR)", "")

st.divider()

# Load Data based on Search
if search_term.strip() != "":
    display_coins = search_unlimited_coin(search_term.strip())
    if not display_coins:
        st.warning(f"⚠️ `{search_term}` naam ka koi coin nahi mila. Sahi spelling try karein.")
else:
    display_coins = get_top_coins()

if not display_coins and search_term.strip() == "":
    st.error("⚠️ Connection slow hai, niche refresh button dabayein.")
    if st.button("🔄 Retry"):
        st.rerun()

is_futures = "FUTURES" in market_mode
badge = '<span class="badge-fut">FUTURES ⚡</span>' if is_futures else '<span class="badge-spot">SPOT 🛒</span>'

# Render Cards
for coin in display_coins:
    symbol = coin.get("symbol", "").upper()
    name = coin.get("name", "")
    price = float(coin.get("current_price") or 0)
    change = float(coin.get("price_change_percentage_24h") or 0)
    volume = float(coin.get("total_volume") or 0)

    if price > 0:
        tp_val = price * 1.025
        sl_val = price * 0.985
        rsi_est = max(15, min(85, 50 + (change * 1.5)))

        st.markdown(f"### 📌 **{symbol}** ({name}) &nbsp; {badge}", unsafe_allow_html=True)
        st.write(f"💵 **Live Price:** `${price:,.6f}` | **24h Change:** `{change:+.2f}%` | **Volume:** `${volume:,.0f}`")

        # Live Signal Cards
        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown(f'<div class="box-entry">🟡 <b>SAFE ENTRY</b><br><b>${price:,.6f}</b></div>', unsafe_allow_html=True)
        with b2:
            st.markdown(f'<div class="box-tp">🟢 <b>TAKE PROFIT (TP)</b><br><b>${tp_val:,.6f}</b></div>', unsafe_allow_html=True)
        with b3:
            st.markdown(f'<div class="box-sl">🔴 <b>STOP LOSS (SL)</b><br><b>${sl_val:,.6f}</b></div>', unsafe_allow_html=True)

        trend = "🟢 BULLISH" if change > 1 else "🔴 BEARISH" if change < -1 else "🟡 NEUTRAL"
        st.caption(f"📊 **RSI (Est.):** {rsi_est:.1f} | **Signal:** {trend}")

        if is_futures:
            with st.expander(f"⚡ Futures Calculator — {symbol}"):
                lev = st.slider(f"Leverage (x) [{symbol}]", 1, 75, 10, key=f"lev_{symbol}")
                margin = st.number_input(f"Margin ($) [{symbol}]", min_value=10.0, value=100.0, key=f"mar_{symbol}")
                pos = margin * lev
                st.write(f"💼 **Position Size:** `${pos:,.2f}` | 🟢 **TP Profit:** `+${(tp_val - price) * (pos / price):.2f}` | 🔴 **SL Risk:** `-${(price - sl_val) * (pos / price):.2f}`")

        st.divider()

if st.button("🔄 Live Refresh Market"):
    st.rerun()
