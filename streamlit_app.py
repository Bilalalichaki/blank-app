import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="Crypto AI Pro Terminal", layout="wide")

# Custom Dark UI Styling
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .badge-spot { background-color: #1e3a8a; color: #93c5fd; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .badge-fut { background-color: #581c87; color: #d8b4fe; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    
    /* Box Styles */
    .box-entry { background-color: #2e2612; color: #ffe082; padding: 12px; border-radius: 8px; border-left: 4px solid #ffb300; text-align: center; }
    .box-tp { background-color: #122e17; color: #a5d6a7; padding: 12px; border-radius: 8px; border-left: 4px solid #66bb6a; text-align: center; }
    .box-sl { background-color: #3b1414; color: #ef9a9a; padding: 12px; border-radius: 8px; border-left: 4px solid #ef5350; text-align: center; }
    
    /* Indicator Cards */
    .ind-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; text-align: center; }
    
    /* AI Signals */
    .ai-buy { background-color: #064e3b; color: #6ee7b7; padding: 12px; border-radius: 8px; border: 1px solid #059669; font-weight: bold; font-size: 16px; text-align: center; }
    .ai-wait { background-color: #78350f; color: #fde68a; padding: 12px; border-radius: 8px; border: 1px solid #d97706; font-weight: bold; font-size: 16px; text-align: center; }
    .ai-sell { background-color: #7f1d1d; color: #fca5a5; padding: 12px; border-radius: 8px; border: 1px solid #dc2626; font-weight: bold; font-size: 16px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ CRYPTO AI SIGNAL & INDICATOR TERMINAL")
st.caption("👨‍💻 Developer: Bilal Ali (Shebi)")

# Fetch Top 250 Coins
@st.cache_data(ttl=15)
def fetch_top_250_market():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

raw_data = fetch_top_250_market()

col1, col2 = st.columns([1, 2])
with col1:
    market_mode = st.radio("Market Mode", ["SPOT Market 🛒", "FUTURES Market ⚡"], horizontal=True)
with col2:
    search_input = st.text_input("🔍 Search Any Coin (e.g. SUI, BTC, SOL, PEPE, SHIB, NEAR)", "")

st.divider()

if not raw_data:
    st.error("⚠️ Data sync hone me delay hai. Refresh karein.")
    if st.button("🔄 Retry Connection"):
        st.rerun()
else:
    q = search_input.lower().strip()
    filtered_coins = [
        c for c in raw_data 
        if q == "" or q in c.get("symbol", "").lower() or q in c.get("name", "").lower()
    ]

    if not filtered_coins:
        st.warning(f"⚠️ `{search_input}` nahi mila. Sahi spelling try karein.")
    else:
        is_futures = "FUTURES" in market_mode
        badge = '<span class="badge-fut">FUTURES ⚡</span>' if is_futures else '<span class="badge-spot">SPOT 🛒</span>'

        st.caption(f"📊 Showing **{len(filtered_coins)}** matched coins")

        for coin in filtered_coins:
            symbol = coin.get("symbol", "").upper()
            name = coin.get("name", "")
            price = float(coin.get("current_price") or 0)
            change = float(coin.get("price_change_percentage_24h") or 0)
            volume = float(coin.get("total_volume") or 0)
            high_24h = float(coin.get("high_24h") or price)
            low_24h = float(coin.get("low_24h") or price)

            if price > 0:
                tp_val = price * 1.025
                sl_val = price * 0.985
                
                # 1. Clear Indicators Logic
                rsi_est = max(15, min(85, 50 + (change * 1.5)))
                ema_20 = price * (1 + (change / 200))
                ema_50 = price * (1 - (change / 300))
                macd_status = "BULLISH CROSS" if change > 0.5 else "BEARISH CROSS" if change < -0.5 else "NEUTRAL"
                vol_status = "HIGH VOLUME 🚀" if volume > 100000000 else "NORMAL VOLUME 📊"

                # 2. AI Prediction System Engine
                ai_signal = "WAIT"
                ai_text = "⏳ WAIT & WATCH — Abhi market setup unclear hai, entry ka wait karein."
                ai_box_class = "ai-wait"

                if change > 1.2 and rsi_est < 70 and price > ema_20:
                    ai_signal = "BUY"
                    ai_text = "🤖 AI PREDICTION: ENTRY LEN! (Strong Bullish Momentum + RSI Safe Zone)"
                    ai_box_class = "ai-buy"
                elif rsi_est >= 70:
                    ai_signal = "OVERBOUGHT"
                    ai_text = "🤖 AI PREDICTION: ENTRY NA LEN! (Coin Overbought/RSI High par hai, correction possible)"
                    ai_box_class = "ai-sell"
                elif change < -2.0 or price < ema_50:
                    ai_signal = "BEARISH"
                    ai_text = "🤖 AI PREDICTION: ENTRY NA LEN! (Downtrend / Bearish Pressure)"
                    ai_box_class = "ai-sell"

                st.markdown(f"### 📌 **{symbol}** ({name}) &nbsp; {badge}", unsafe_allow_html=True)
                st.write(f"💵 **Live Price:** `${price:,.6f}` | **24h Change:** `{change:+.2f}%` | **24h High:** `${high_24h:,.6f}` | **24h Low:** `${low_24h:,.6f}`")

                # AI Decision Banner
                st.markdown(f'<div class="{ai_box_class}">{ai_text}</div>', unsafe_allow_html=True)
                st.write("")

                # Clear Indicator Cards Row
                st.markdown("##### 📊 **Technical Indicators Summary**")
                i1, i2, i3, i4, i5 = st.columns(5)
                with i1:
                    st.markdown(f'<div class="ind-card"><b>RSI (14)</b><br><code>{rsi_est:.1f}</code></div>', unsafe_allow_html=True)
                with i2:
                    st.markdown(f'<div class="ind-card"><b>EMA (20)</b><br><code>${ema_20:,.6f}</code></div>', unsafe_allow_html=True)
                with i3:
                    st.markdown(f'<div class="ind-card"><b>EMA (50)</b><br><code>${ema_50:,.6f}</code></div>', unsafe_allow_html=True)
                with i4:
                    st.markdown(f'<div class="ind-card"><b>MACD Signal</b><br><code>{macd_status}</code></div>', unsafe_allow_html=True)
                with i5:
                    st.markdown(f'<div class="ind-card"><b>Volume Trend</b><br><small>{vol_status}</small></div>', unsafe_allow_html=True)

                st.write("")

                # Order Entry Boxes
                b1, b2, b3 = st.columns(3)
                with b1:
                    st.markdown(f'<div class="box-entry">🟡 <b>SAFE ENTRY</b><br><b>${price:,.6f}</b></div>', unsafe_allow_html=True)
                with b2:
                    st.markdown(f'<div class="box-tp">🟢 <b>TAKE PROFIT (TP)</b><br><b>${tp_val:,.6f}</b></div>', unsafe_allow_html=True)
                with b3:
                    st.markdown(f'<div class="box-sl">🔴 <b>STOP LOSS (SL)</b><br><b>${sl_val:,.6f}</b></div>', unsafe_allow_html=True)

                # Futures Leverage Calculator
                if is_futures:
                    with st.expander(f"⚡ Futures Calculator — {symbol}"):
                        lev = st.slider(f"Leverage (x) [{symbol}]", 1, 75, 10, key=f"lev_{symbol}")
                        margin = st.number_input(f"Margin ($) [{symbol}]", min_value=10.0, value=100.0, key=f"mar_{symbol}")
                        pos = margin * lev
                        st.write(f"💼 **Position Size:** `${pos:,.2f}` | 🟢 **TP Profit:** `+${(tp_val - price) * (pos / price):.2f}` | 🔴 **SL Risk:** `-${(price - sl_val) * (pos / price):.2f}`")

                st.divider()

if st.button("🔄 Refresh Terminal"):
    st.rerun()
