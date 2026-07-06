import streamlit as st
import yfinance as yf
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="TRADING SYSTEM PRO", layout="wide")
st.title("📊 TRADING SYSTEM PRO (STABLE VERSION)")

asset = st.selectbox("Select Asset", ["GC=F", "QQQ", "BTC-USD"])

# =========================
# SAFE DATA LOAD
# =========================
df = yf.download(asset, period="5d", interval="15m", progress=False)

if df is None or df.empty:
    st.error("No data available from source")
    st.stop()

df = df.dropna()

# =========================
# SAFE NUMERIC EXTRACTION (CRITICAL FIX)
# =========================
try:
    close = df["Close"].to_numpy(dtype=float)
    high = df["High"].to_numpy(dtype=float)
    low = df["Low"].to_numpy(dtype=float)
    open_ = df["Open"].to_numpy(dtype=float)
except Exception:
    st.error("Data format error from provider")
    st.stop()

if len(close) < 50:
    st.error("Not enough market data")
    st.stop()

# =========================
# SAFE PRICE (NO FAIL ZONE)
# =========================
price = float(close[-1])

# =========================
# STRUCTURE
# =========================
high_20 = float(np.max(close[-20:]))
low_20 = float(np.min(close[-20:]))

sweep_high = price > high_20 * 0.999
sweep_low = price < low_20 * 1.001

# =========================
# SIMPLE LOGIC (SAFE LOOP)
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

# =========================
# UI
# =========================
col1, col2 = st.columns([1, 2])

with col1:
    st.metric("💰 Price", round(price, 2))
    st.metric("🧠 Score", score)

    if score >= 3:
        st.success("📈 LONG SETUP")
    elif score <= -3:
        st.error("📉 SHORT SETUP")
    else:
        st.warning("⏸ NO TRADE")

# =========================
# CHART SAFE
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

fig.update_layout(height=650, xaxis_rangeslider_visible=False)

with col2:
    st.plotly_chart(fig, use_container_width=True)
