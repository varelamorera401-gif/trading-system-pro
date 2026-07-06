import streamlit as st
import yfinance as yf
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="TRADING SYSTEM PRO UI", layout="wide")

st.title("📊 TRADING SYSTEM PRO UI (SMC PLATFORM)")

assets = ["GC=F", "QQQ", "BTC-USD"]
asset = st.selectbox("Select Asset", assets)

# =========================
# DATA LOAD
# =========================
df = yf.download(asset, period="5d", interval="15m", progress=False)
df = df.dropna()

if df.empty:
    st.error("No data available")
    st.stop()

if len(df) < 50:
    st.warning("Not enough data (min 50 candles)")
    st.stop()

# =========================
# CLEAN DATA
# =========================
close = df["Close"].dropna()
high = df["High"].dropna()
low = df["Low"].dropna()
open_ = df["Open"].dropna()

# 🔥 SINGLE SOURCE OF PRICE (NO ERRORES)
price = float(close.iloc[-1])

# =========================
# STRUCTURE
# =========================
high_20 = float(close.tail(20).max())
low_20 = float(close.tail(20).min())

sweep_high = price > high_20 * 0.999
sweep_low = price < low_20 * 1.001

# =========================
# ORDER BLOCKS
# =========================
bull_ob = []
bear_ob = []

for i in range(5, len(df) - 3):
    try:
        c = close.iloc[i]
        c3 = close.iloc[i + 3]
        o = open_.iloc[i]

        if c3 > c * 1.01 and c < o:
            bull_ob.append(float(c))

        if c3 < c * 0.99 and c > o:
            bear_ob.append(float(c))

    except:
        continue

bull_ob = bull_ob[-3:]
bear_ob = bear_ob[-3:]

# =========================
# FVG
# =========================
bull_fvg = []
bear_fvg = []

for i in range(2, len(df)):
    try:
        if low.iloc[i] > high.iloc[i - 2]:
            bull_fvg.append(float(high.iloc[i - 2]))

        if high.iloc[i] < low.iloc[i - 2]:
            bear_fvg.append(float(low.iloc[i - 2]))
    except:
        continue

bull_fvg = bull_fvg[-3:]
bear_fvg = bear_fvg[-3:]

# =========================
# SCORE SYSTEM
# =========================
score = 0

ema_fast = close.ewm(span=10).mean().iloc[-1]
ema_slow = close.ewm(span=30).mean().iloc[-1]

if ema_fast > ema_slow:
    score += 1
else:
    score -= 1

if sweep_low:
    score += 2
if sweep_high:
    score -= 2

if any(abs(price - x) / price < 0.002 for x in bull_ob):
    score += 2

if any(abs(price - x) / price < 0.002 for x in bear_ob):
    score -= 2

if any(abs(price - x) / price < 0.002 for x in bull_fvg):
    score += 1

if any(abs(price - x) / price < 0.002 for x in bear_fvg):
    score -= 1

# =========================
# UI
# =========================
col1, col2 = st.columns([1, 2])

with col1:
    st.metric("💰 Price", round(price, 2))
    st.metric("🧠 SMC Score", score)

    if score >= 3:
        st.success("📈 LONG SETUP")
    elif score <= -3:
        st.error("📉 SHORT SETUP")
    else:
        st.warning("⏸ NO TRADE")

    st.divider()
    st.write("High:", round(high_20, 2))
    st.write("Low:", round(low_20, 2))

# =========================
# CHART
# =========================
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"]
))

fig.add_hline(y=high_20, line_dash="dash", line_color="red")
fig.add_hline(y=low_20, line_dash="dash", line_color="green")

for x in bull_ob:
    fig.add_hline(y=x, line_color="green", line_dash="dot")

for x in bear_ob:
    fig.add_hline(y=x, line_color="red", line_dash="dot")

for x in bull_fvg:
    fig.add_hline(y=x, line_color="lime", line_dash="dash")

for x in bear_fvg:
    fig.add_hline(y=x, line_color="orange", line_dash="dash")

fig.update_layout(height=650, xaxis_rangeslider_visible=False)

with col2:
    st.plotly_chart(fig, use_container_width=True)
