import streamlit as st
import requests

st.set_page_config(page_title="Crypto Live Dashboard", layout="wide")

st.title("🚀 ALL CRYPTO SPOT & FUTURES DASHBOARD")
st.caption("👨‍💻 Developer: Bilal Ali (Shebi)")

# Coins Mapping for CoinGecko (100% Reliable)
COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "PAXG (Gold)": "pax-gold",
    "ZEC": "zcash"
}

market_type = st.sidebar.radio("📍 Select Market Type", ["SPOT Market 🛒", "FUTURES Market ⚡"])
selected_symbol = st.sidebar.selectbox("🔍 Select Coin", list(COINS.keys()), index=0)
coin_id = COINS[selected_symbol]

@st.cache_data(ttl=10)
def get_crypto_data(c_id):
    try:
        # Ultra fast endpoint
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={c_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json().get(c_id, {})
            price = float(data.get("usd", 0))
            change = float(data.get("usd_24h_change", 0))
            volume = float(data.get("usd_24h_vol", 0))
            return price, change, volume
    except Exception:
        pass
    return None, None, None

price, change, vol = get_crypto_data(coin_id)

if price and price > 0:
    tp_pred = price * 1.025
    sl_pred = price * 0.985
    rsi_est = max(15, min(85, 50 + (change * 1.5)))

    st.markdown(f"## 📌 `{selected_symbol}` — ({market_type})")
    st.markdown(f"### Live Rate: **${price:,.4f}** | 24h Change: **{change:+.2f}%**")

    # 3 MAIN COLOR BOXES
    st.markdown("### 🎯 Live Predictions & Signal Levels")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.warning(f"🟡 SAFE ENTRY RATE\n\n### ${price:,.4f}")
    with col2:
        st.success(f"🟢 TAKE PROFIT (TP)\n\n### ${tp_pred:,.4f}")
    with col3:
        st.error(f"🔴 STOP LOSS (SL)\n\n### ${sl_pred:,.4f}")

    st.divider()

    # INDICATORS
    st.markdown("### 📊 Live Technical Indicators")
    i1, i2, i3 = st.columns(3)
    
    with i1:
        st.info(f"**RSI (Est.)**: {rsi_est:.2f}")
    with i2:
        st.info(f"**24h Volume**: ${vol:,.0f}")
    with i3:
        trend = "🟢 BULLISH ZONE" if change > 1 else "🔴 BEARISH ZONE" if change < -1 else "🟡 NEUTRAL / HOLD"
        st.info(f"**Market Signal**: {trend}")

    # Futures Calculator
    if "FUTURES" in market_type:
        st.divider()
        st.markdown("### ⚡ Futures Profit & Risk Calculator")
        lev = st.slider("Select Leverage (x)", min_value=1, max_value=75, value=10)
        margin = st.number_input("Margin / Capital ($)", min_value=10.0, value=100.0)
        
        pos_size = margin * lev
        estimated_profit = (tp_pred - price) * (pos_size / price)
        estimated_loss = (price - sl_pred) * (pos_size / price)
        
        st.write(f"💼 **Total Position Size**: `${pos_size:,.2f}`")
        st.write(f"🟢 **Estimated Profit at TP**: `+${estimated_profit:.2f}`")
        st.write(f"🔴 **Estimated Loss at SL**: `-${estimated_loss:.2f}`")

    st.divider()
    if st.button("🔄 Refresh Data Now"):
        st.rerun()

else:
    st.error("⚠️ Data connection time out. Please click button below to retry.")
    if st.button("🔄 Retry Connection"):
        st.rerun()
