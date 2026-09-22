import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Multi-Coin Live Pro Dashboard", layout="wide")

st.title("🚀 ALL-IN-ONE CRYPTO LIVE PRO DASHBOARD")
st.caption("👨‍💻 Developer: Bilal Ali (Shebi)")

# Dynamic Multi-Coin Watchlist
WATCHLIST = [
    {"symbol": "BTC", "id": "bitcoin"},
    {"symbol": "ETH", "id": "ethereum"},
    {"symbol": "PAXG", "id": "pax-gold"},
    {"symbol": "ZEC", "id": "zcash"},
    {"symbol": "SOL", "id": "solana"},
    {"symbol": "BNB", "id": "binancecoin"},
    {"symbol": "XRP", "id": "ripple"},
    {"symbol": "ADA", "id": "cardano"}
]

def fetch_coin_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json().get("market_data", {})
            price = data.get("current_price", {}).get("usd", 0)
            change_24h = data.get("price_change_percentage_24h", 0)
            high_24h = data.get("high_24h", {}).get("usd", price)
            low_24h = data.get("low_24h", {}).get("usd", price)
            vol = data.get("total_volume", {}).get("usd", 0)
            return price, change_24h, high_24h, low_24h, vol
    except Exception:
        pass
    return None, None, None, None, None

st.subheader("📊 Live Market Multi-Coin Overview")

# Loop through all coins
for item in WATCHLIST:
    symbol = item["symbol"]
    c_id = item["id"]
    
    price, change, high, low, vol = fetch_coin_data(c_id)
    
    if price and price > 0:
        # Technical Predictions & Dynamic Indicator Logic
        tp_pred = price * 1.025
        sl_pred = price * 0.985
        
        # Dynamic RSI Estimate based on market momentum
        rsi_val = max(15, min(85, 50 + (change * 1.8)))
        
        if rsi_val < 35:
            rsi_text = f"RSI: {rsi_val:.1f} (OVERSOLD 🟢 BUY)"
            rsi_badge = "🟢 BULLISH"
        elif rsi_val > 65:
            rsi_text = f"RSI: {rsi_val:.1f} (OVERBOUGHT 🔴 SELL)"
            rsi_badge = "🔴 BEARISH"
        else:
            rsi_text = f"RSI: {rsi_val:.1f} (NEUTRAL 🟡 HOLD)"
            rsi_badge = "🟡 NEUTRAL"

        # Signal Determination
        if change > 1.5:
            signal = "🟢 HIGH CONFIRMATION BUY"
        elif change < -1.5:
            signal = "🔴 HIGH CONFIRMATION SELL"
        else:
            signal = "🟡 WAIT / NO TRADE"

        # MAIN CARD FOR EACH COIN
        with st.expander(f"📌 **{symbol}/USDT** — ${price:,.4f} | 24h: {change:+.2f}% | Signal: {signal}", expanded=True):
            
            # Row 1: Prediction Cards (Yellow, Green, Red)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.warning(f"🟡 **SAFE ENTRY**\n\n### ${price:,.4f}")
            with c2:
                st.success(f"🟢 **TAKE PROFIT (TP)**\n\n### ${tp_pred:,.4f}")
            with c3:
                st.error(f"🔴 **STOP LOSS (SL)**\n\n### ${sl_pred:,.4f}")

            # Row 2: Live Indicators Breakdown
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                st.info(f"**Indicator**: {rsi_text}")
            with i2:
                st.info(f"**24h High (Resistance)**: ${high:,.2f}")
            with i3:
                st.info(f"**24h Low (Support)**: ${low:,.2f}")
            with i4:
                st.info(f"**Market Status**: {rsi_badge}")

            st.caption(f"Volume (24h): ${vol:,.0f}")
            st.divider()

    else:
        st.warning(f"⏳ {symbol} Ka Live Data Connect Ho Raha Hai...")

# Live Auto-Refresh every 5 seconds
time.sleep(5)
st.rerun()
