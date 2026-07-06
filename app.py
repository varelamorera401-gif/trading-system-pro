import streamlit as st
import yfinance as yf
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="TRADING SYSTEM PRO (BLINDED)", layout="wide")

st.title("📊 TRADING SYSTEM PRO UI (BLINDED VERSION)")

assets = ["GC=F", "QQQ", "BTC-USD"]
asset = st.selectbox("Select Asset", assets)

# =========================
# DATA SAFE LOAD (ROBUST)
# =========================
df = yf.download(asset, period="5d", interval="15m", progress=False)

if df is None or len(df) == 0:
    st.error("No data received from source")
    st.stop()

df = df.dropna()

if len(df) < 50:
    st.warning("Not enough data (min 50 candles)")
    st.stop()

# =========================
# FORCE NUMERIC CLEAN DATA
# =========================
close = df["Close"].astype("float64").dropna().to_numpy()
high = df["High"].astype("float64").dropna().to_numpy()
low = df["Low"].astype("float64").dropna().to_numpy()
open_ = df["Open"].astype("float64").dropna().to_numpy()

# =========================
# SAFE PRICE (NO PANDAS)
# =========================
if close.size == 0:
    st.error("No price data available")
    st.stop()

price = float(close[-1])

# =========================
# STRUCTURE
# =========================
high_20 = float(np.max(close[-20:]))
low_20 = float(np.min(close[-20:]))

sweep_high = price > high_20 * 0.999
sweep_low = price < low_20 * 1.001

# =========================
# ORDER BLOCKS (ARRAY SAFE)
# =========================
bull_ob = []
bear_ob = []

for i in range(5, len(close) - 3):
    c = close[i]
    c3 = close[i + 3]
    o = open_[i]

    if c3 > c * 1.01 and c < o:
        bull_ob.append(c)

    if c3 < c * 0.99 and c > o:
        bear_ob.append(c)

bull_ob = bull_ob[-3:]
bear_ob = bear_ob[-3:]

# =========================
# FVG SAFE
# =========================
bull_fvg = []
bear_fvg = []

for i in range(2, len(close)):
    if low[i] > high[i - 2]:
        bull_fvg.append(high[i - 2])

    if high[i] < low[i - 2]:
        bear_fvg.append(low[i - 2])

bull_fvg = bull_fvg[-3:]
bear_fvg = bear_fvg[-3:]

# =========================
# SCORE ENGINE
# =========================
score = 0

ema_fast = np.mean(close[-10:])
ema_slow = np.mean(close[-30:])

score += 1 if ema_fast > ema_slow else -1
score += 2 if sweep_low else 0
score -= 2 if sweep_high else 0

score += 2 if any(abs(price - x) / price < 0.002 for x in bull_ob) else 0
score -= 2 if any(abs(price - x) / price < 0.002 for x in bear_ob) else 0
score += 1 if any(abs(price - x) / price < 0.002 for x in bull_fvg) else 0
score -= 1 if any(abs(price - x) / price < 0.002 for x in bear_fvg) else 0

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
