import streamlit as st
import yfinance as yf
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="TRADING SYSTEM PRO UI", layout="wide")

st.title("📊 TRADING SYSTEM PRO UI (SMC PLATFORM)")

assets = ["GC=F", "QQQ", "BTC-USD"]

asset = st.selectbox("Select Asset", assets)

# =========================
# DATA SAFE LOAD
# =========================
df = yf.download(asset, period="5d", interval="15m", progress=False)

if df is None or df.empty:
    st.error("No data available from Yahoo Finance")
    st.stop()

if len(df) < 50:
    st.warning("No hay suficientes datos para análisis (mínimo 50 velas)")
    st.stop()

close = df["Close"]
price = close.iloc[-1]

# =========================
# STRUCTURE
# =========================
high_20 = close.tail(20).max()
low_20 = close.tail(20).min()

sweep_high = price > high_20 * 0.999
sweep_low = price < low_20 * 1.001

# =========================
# ORDER BLOCKS (SAFE)
# =========================
bull_ob = []
bear_ob = []

for i in range(5, len(df) - 3):

    try:
        if df["Close"].iloc[i+3] > df["Close"].iloc[i] * 1.01:
            if df["Close"].iloc[i] < df["Open"].iloc[i]:
                bull_ob.append(df["Close"].iloc[i])

        if df["Close"].iloc[i+3] < df["Close"].iloc[i] * 0.99:
            if df["Close"].iloc[i] > df["Open"].iloc[i]:
                bear_ob.append(df["Close"].iloc[i])
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

    if df["Low"].iloc[i] > df["High"].iloc[i-2]:
        bull_fvg.append(df["High"].iloc[i-2])

    if df["High"].iloc[i] < df["Low"].iloc[i-2]:
        bear_fvg.append(df["Low"].iloc[i-2])

bull_fvg = bull_fvg[-3:]
bear_fvg = bear_fvg[-3:]

# =========================
# SCORE
# =========================
score = 0

ema_f = close.ewm(span=10).mean().iloc[-1]
ema_s = close.ewm(span=30).mean().iloc[-1]

if ema_f > ema_s:
    score += 1
else:
    score -= 1

if sweep_low:
    score += 2
if sweep_high:
    score -= 2

if any(abs(price - x)/price < 0.002 for x in bull_ob):
    score += 2

if any(abs(price - x)/price < 0.002 for x in bear_ob):
    score -= 2

if any(abs(price - x)/price < 0.002 for x in bull_fvg):
    score += 1

if any(abs(price - x)/price < 0.002 for x in bear_fvg):
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

    st.write("📊 Liquidity Zones")
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
    close=df["Close"],
    name="Price"
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
