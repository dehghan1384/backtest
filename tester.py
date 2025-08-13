import streamlit as st
import pandas as pd
import ta
import matplotlib.pyplot as plt
from backtesting.lib import crossover

st.set_page_config(page_title="BacktestPro", layout="wide")
st.title("🚀 BacktestPro – استفاده از تابع crossover برای تشخیص دقیق سیگنال‌ها")

# 1. آپلود فایل
uploaded_file = st.file_uploader("📁 آپلود فایل (CSV/TSV بدون هدر)", type=["csv", "tsv", "txt"])
if not uploaded_file:
    st.warning("لطفاً یک فایل CSV یا TSV آپلود کنید")
    st.stop()

# 2. خواندن داده بدون هدر
uploaded_file.seek(0)
df = pd.read_csv(uploaded_file, sep=None, engine="python", header=None)
if df.shape[1] < 6:
    st.error("فایل باید حداقل 6 ستون (Date, Time, Open, High, Low, Close) داشته باشد")
    st.stop()


#------------------------------------------------------------------

# df = df.iloc[:, :5]
df.drop(df.columns[5], axis=1, inplace=True)
df.columns = ["Date & Time", "Open", "High", "Low", "Close"]


df["Datetime"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Time"].astype(str), errors="coerce")
df = df.dropna(subset=["Datetime"]).set_index("Datetime").sort_index()

for col in ["Open", "High", "Low", "Close"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["Close"])

# 3. پارامترهای بک‌تست
entry_cond  = st.selectbox("شرط ورود:", ["EMA9 > EMA21", "SMA50 > SMA200", "RSI < 30"])
exit_cond   = st.selectbox("شرط خروج:", ["EMA9 < EMA21", "SMA50 < SMA200", "RSI > 70"])
initial_bal = st.number_input("سرمایه اولیه (USD):", value=1000.0, step=100.0)
trade_pct   = st.slider("درصد سرمایه در هر معامله:", 1, 100, 10)

# 4. محاسبه اندیکاتورها
df["EMA9"]   = ta.trend.ema_indicator(df["Close"], window=9)
df["EMA21"]  = ta.trend.ema_indicator(df["Close"], window=21)
df["SMA50"]  = ta.trend.sma_indicator(df["Close"], window=50)
df["SMA200"] = ta.trend.sma_indicator(df["Close"], window=200)
df["RSI14"]  = ta.momentum.rsi(df["Close"], window=14)

df = df.dropna()


# 5. اجرای بک‌تست با استفاده از crossover
balance  = initial_bal
position = None
trades   = []

for i in range(1, len(df)):
    row = df.iloc[i]
    prev = df.iloc[i - 1]
    time = df.index[i]

    # ورود
    if entry_cond == "EMA9 > EMA21":
        enter = crossover(df["EMA9"], df["EMA21"])[i]
    elif entry_cond == "SMA50 > SMA200":
        enter = crossover(df["SMA50"], df["SMA200"])[i]
    else:  # RSI < 30
        enter = crossover(30 - df["RSI14"], pd.Series([0]*len(df)))[i]

    # خروج
    if exit_cond == "EMA9 < EMA21":
        exit_ = crossover(df["EMA21"], df["EMA9"])[i]
    elif exit_cond == "SMA50 < SMA200":
        exit_ = crossover(df["SMA200"], df["SMA50"])[i]
    else:  # RSI > 70
        exit_ = crossover(df["RSI14"] - 70, pd.Series([0]*len(df)))[i]

    if enter and position is None:
        position = {
            "time":  time,
            "price": row["Close"],
            "size":  balance * (trade_pct / 100)
        }

    elif exit_ and position is not None:
        pnl = (row["Close"] - position["price"]) / position["price"] * position["size"]
        balance += pnl
        trades.append({
            "Entry Time":  position["time"],
            "Entry Price": position["price"],
            "Exit Time":   time,
            "Exit Price":  row["Close"],
            "Profit":      pnl
        })
        position = None

# بستن پوزیشن باقیمانده
if position is not None:
    last_price = df["Close"].iloc[-1]
    pnl = (last_price - position["price"]) / position["price"] * position["size"]
    balance += pnl
    trades.append({
        "Entry Time":  position["time"],
        "Entry Price": position["price"],
        "Exit Time":   df.index[-1],
        "Exit Price":  last_price,
        "Profit":      pnl
    })

# 6. نمایش نتایج
results_df = pd.DataFrame(trades)
equity = pd.Series(initial_bal, index=df.index)
if not results_df.empty:
    cum_profit = results_df["Profit"].cumsum()
    equity = initial_bal + cum_profit.reindex(df.index, method="ffill").fillna(initial_bal)

st.subheader("📈 آمار کلی بک‌تست")
st.metric("تعداد معاملات", len(results_df))
st.metric("درصد برد", f"{(results_df['Profit'] > 0).mean() * 100:.2f}%")
st.metric("میانگین سود/ضرر", f"{results_df['Profit'].mean():.2f} USD" if not results_df.empty else "0.00 USD")
st.metric("بازده کل", f"{equity.iloc[-1] - initial_bal:.2f} USD" if not equity.empty else "0.00 USD")

st.subheader("📊 جزییات معاملات")
if results_df.empty:
    st.info("⚠️ هیچ معامله‌ای ثبت نشد.")
else:
    st.dataframe(results_df)

st.subheader("📈 نمودار رشد سرمایه")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(equity.index, equity.values, color="blue", linewidth=1.5)
ax.set_xlabel("تاریخ")
ax.set_ylabel("سرمایه (USD)")
ax.set_title("Equity Curve")
ax.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig)
