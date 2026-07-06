import streamlit as st
import yfinance as yf
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="TRADING SYSTEM PRO UI", layout="wide")

st.title("📊 TRADING SYSTEM PRO UI (SMC PLATFORM)")

assets = ["GC=F", "QQQ", "BTC-USD"]

asset = st.selectbox("Select Asset", assets)

# =========================
# SAFE DATA LOAD
# =========================
df = yf.download(asset, period="5d", interval="15m", progress=False)
df = df.dropna()

if df is None or df.empty:
    st.error("❌ No data received from Yahoo Finance")
    st.stop()

if len(df) < 50:
    st.warning("⚠️ Not enough data (need at least 50 candles)")
    st.stop()

# =========================
# SAFE SERIES
# =========================
close = df["Close"].dropna()
high = df["High"].dropna()
low = df["Low"].dropna()
open_ = df["Open"].dropna()

if len(close) == 0:
    st.error("❌ Invalid price data")
    st.stop()

close_clean = close.dropna()

if close_clean.empty:
    st.error("No valid price data")
    st.stop()

price = float(close_clean.iloc[-1])

# =========================
# STRUCTURE
# =========================
high_20 = float(close.tail(20).max())
low_20 = float(close.tail(20).min())

sweep_high = price > high_20 * 0.999
sweep_low = price < low_20 * 1.001

# =========================
# ORDER BLOCKS SAFE
# =========================
bull_ob = []
bear_ob = []

for i in range(5, len(df) - 3):
    try:
        c = float(close.iloc[i])
        c3 = float(close.iloc[i + 3])
        o = float(open_.iloc[i])

        if c3 > c * 1.01 and c < o:
            bull_ob.append(c)

        if c3 < c * 0.99 and c > o:
            bear_ob.append(c)

    except:
        continue

bull_ob = bull_ob[-3:]
bear_ob = bear_ob[-3:]

# =========================
# FVG SAFE
# =========================
bull_fvg = []
bear_fvg = []

for i in range(2, len(df)):
    try:
        low_i = float(low.iloc[i])
        high_i = float(high.iloc[i])
        low_2 = float(low.iloc[i - 2])
        high_2 = float(high.iloc[i - 2])

        if low_i > high_2:
            bull_fvg.append(high_2)

        if high_i < low_2:
            bear_fvg.append(low_2)

    except:
        continue

bull_fvg = bull_fvg[-3:]
bear_fvg = bear_fvg[-3:]

# =========================
# SCORE
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
