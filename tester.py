import streamlit as st
import pandas as pd
import ta
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from backtesting.lib import crossover
import time

st.set_page_config(page_title="BacktestPro — Enhanced", layout="wide")
st.title("🚀 BacktestPro — Enhanced Backtester")

st.markdown(
    "قبل از آپلود فایل: برای دسترسی به داده‌های تاریخی فارکس از این سایت استفاده کنید: [https://forexsb.com/historical-forex-data](https://forexsb.com/historical-forex-data)"
)

# -------------------------
# File upload
# -------------------------
uploaded_file = st.file_uploader("📁 آپلود فایل (CSV/TSV بدون هدر) — ستون‌ها: Date/Time, Open, High, Low, Close", type=["csv", "tsv", "txt"])
if not uploaded_file:
    st.info("لطفاً فایل خود را آپلود کنید یا از لینک بالا دیتا دانلود کنید.")
    st.stop()

uploaded_file.seek(0)
# try to infer separator
try:
    df = pd.read_csv(uploaded_file, sep=None, engine="python", header=None)
except Exception as e:
    st.error(f"خطا هنگام خواندن فایل: {e}")
    st.stop()

if df.shape[1] < 5:
    st.error("فایل باید حداقل 5 ستون داشته باشد: Date/Time, Open, High, Low, Close")
    st.stop()

# keep only first 5 columns
df = df.iloc[:, :5].copy()
# name columns
df.columns = ["Date & Time", "Open", "High", "Low", "Close"]

# numeric conversion
for col in ["Open", "High", "Low", "Close"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# try to parse datetimes
try:
    df["Date & Time"] = pd.to_datetime(df["Date & Time"], errors="coerce")
    df.set_index("Date & Time", inplace=True)
    has_datetime_index = True
except Exception:
    # if parsing fails, keep integer index
    st.warning("فرمت تاریخ قابل‌تبدیل نبود — از ایندکس عددی استفاده می‌شود. (Time filter will be disabled)")
    has_datetime_index = False

df = df.dropna(subset=["Close"]).copy()
if df.empty:
    st.error("داده‌های قیمت معتبر یافت نشد.")
    st.stop()

# =========================
# IMPORTANT: Handle pending preset BEFORE widgets are created
# (fixes: StreamlitAPIException about modifying widget keys)
# =========================
if 'apply_preset_values' in st.session_state:
    # apply values to session_state before widgets are instantiated
    for k, v in st.session_state['apply_preset_values'].items():
        st.session_state[k] = v
    del st.session_state['apply_preset_values']

# -------------------------
# Strategy parameters (customizable indicators)
# -------------------------
st.sidebar.header("⚙️ Indicator settings")
# initialize session state for strategy presets
if 'strategy_preset' not in st.session_state:
    st.session_state['strategy_preset'] = ''

ema_short = st.sidebar.number_input("EMA short window:", min_value=2, max_value=200, value=9, key='ema_short')
ema_long  = st.sidebar.number_input("EMA long window:", min_value=2, max_value=500, value=21, key='ema_long')
sma_short = st.sidebar.number_input("SMA short window:", min_value=2, max_value=500, value=50, key='sma_short')
sma_long  = st.sidebar.number_input("SMA long window:", min_value=2, max_value=1000, value=200, key='sma_long')
rsi_window= st.sidebar.number_input("RSI window:", min_value=2, max_value=200, value=14, key='rsi_window')
macd_fast = st.sidebar.number_input("MACD fast:", min_value=2, max_value=200, value=12, key='macd_fast')
macd_slow = st.sidebar.number_input("MACD slow:", min_value=2, max_value=500, value=26, key='macd_slow')
macd_signal=st.sidebar.number_input("MACD signal:", min_value=1, max_value=200, value=9, key='macd_signal')
bb_window = st.sidebar.number_input("Bollinger window:", min_value=2, max_value=200, value=20, key='bb_window')
bb_std    = st.sidebar.number_input("Bollinger std dev:", min_value=1.0, max_value=5.0, value=2.0, step=0.1, key='bb_std')
st.sidebar.markdown("---")

# -------------------------
# Time filter and SL/TP settings
# -------------------------
st.sidebar.header("⏱️ Time window & SL/TP")
trade_start_hour = st.sidebar.slider("Trade start hour (local) — inclusive:", 0, 23, 12, key='trade_start')
trade_end_hour   = st.sidebar.slider("Trade end hour (local) — inclusive:", 0, 23, 20, key='trade_end')

# Split checkboxes for SL and TP (equity-based) separately
use_equity_sl = st.sidebar.checkbox(
    "✅ Enable equity-based SL (risk by account %)",
    value=False, key="use_equity_sl",
    help="اگر فعال باشد، مقدار SL به‌صورت درصدی از موجودی حساب محاسبه می‌شود (مثلاً 2٪ از 1000$ = حداکثر 20$ ضرر)."
)
use_equity_tp = st.sidebar.checkbox(
    "✅ Enable equity-based TP (target by account %)",
    value=False, key="use_equity_tp",
    help="اگر فعال باشد، مقدار TP به‌صورت درصدی از موجودی حساب محاسبه می‌شود (مثلاً 4٪ از 1000$ = هدف 40$ سود)."
)

# Removed old price-based Manual % SL/TP and Risk:Reward inputs.
# We keep price-based inputs disabled by default.
sl_pct = 0.0
tp_pct = 0.0

# When equity-based SL/TP are ON, show SL/TP % of equity (separately)
if use_equity_sl:
    sl_equity_pct = st.sidebar.number_input("SL as % of equity (max loss):", min_value=0.0, value=2.0, step=0.1, key='sl_equity_pct')
if use_equity_tp:
    tp_equity_pct = st.sidebar.number_input("TP as % of equity (target profit):", min_value=0.0, value=4.0, step=0.1, key='tp_equity_pct')

st.sidebar.markdown("---")

# -------------------------
# Money management
# -------------------------
st.sidebar.header("💰 Money management")
initial_bal = st.sidebar.number_input("Initial capital (USD):", value=1000.0, step=100.0, key='initial_bal')
trade_pct   = st.sidebar.slider("Percent of capital per trade:", 1, 100, 10, key='trade_pct')
leverage    = st.sidebar.number_input("Leverage (x):", min_value=1.0, max_value=100.0, value=1.0, step=0.5, key='leverage')
position_sizing_mode = st.sidebar.selectbox("Position sizing:", ["Percent of equity (exposure = pct * equity * leverage)", "Fixed USD per trade"], key='pos_size_mode') 
fixed_size = None
if position_sizing_mode.startswith("Fixed"):
    fixed_size = st.sidebar.number_input("Fixed USD per trade:", value=100.0, key='fixed_size')

st.sidebar.markdown("---")

# -------------------------
# Strategy suggestions (presets)
# -------------------------
st.sidebar.header("🎯 Strategy presets")
strategy_presets = {
    "EMA9/21 + RSI filter": {
        'ema_short':9,'ema_long':21,'entry':['EMA cross 9/21'], 'exit':['EMA cross 9/21','RSI > 70 (14)'], 'trade_pct':10, 'leverage':1
    },
    "SMA50/200 Momentum":{
        'sma_short':50,'sma_long':200,'entry':['SMA cross 50/200'],'exit':['SMA cross 50/200'], 'trade_pct':15, 'leverage':1
    },
    "MACD trend-follow":{
        'macd_fast':12,'macd_slow':26,'macd_signal':9,'entry':['MACD cross'],'exit':['MACD cross'], 'trade_pct':12, 'leverage':1
    },
    "Bollinger mean-revert":{
        'bb_window':20,'bb_std':2.0,'entry':['BB touch lower'],'exit':['BB breakout upper'], 'trade_pct':8, 'leverage':1
    }
}
sel_preset = st.sidebar.selectbox("Pick a preset to view details:", [''] + list(strategy_presets.keys()))
if sel_preset:
    st.sidebar.write("Preset details:")
    st.sidebar.json(strategy_presets[sel_preset])
    if st.sidebar.button("Apply preset"):
        preset = strategy_presets[sel_preset]
        # IMPORTANT: set a pending apply flag (will be applied at top on next run)
        st.session_state['apply_preset_values'] = preset
        st.session_state['strategy_preset'] = sel_preset
        # Try to force a rerun in a safe, cross-version way
        try:
            # preferred method if available
            st.experimental_rerun()
        except Exception:
            try:
                # fallback: change query params to trigger a rerun in many Streamlit versions
                st.experimental_set_query_params(_refresh=int(time.time()*1000))
            except Exception:
                # last fallback: inform the user that preset was applied to session_state,
                # and UI will reflect on next interaction / reload.
                st.success("Preset applied — please interact with the app (e.g., change any input) or reload the page to see the preset values applied.")

# -------------------------
# Compute indicators
# -------------------------
close = df["Close"]
high = df["High"]
low = df["Low"]

# EMAs & SMAs
try:
    df[f"EMA{ema_short}"] = ta.trend.ema_indicator(close, window=ema_short)
    df[f"EMA{ema_long}"]  = ta.trend.ema_indicator(close, window=ema_long)
    df[f"SMA{int(sma_short)}"] = ta.trend.sma_indicator(close, window=int(sma_short))
    df[f"SMA{int(sma_long)}"]  = ta.trend.sma_indicator(close, window=int(sma_long))
except Exception as e:
    st.error(f"خطا در محاسبه EMA/SMA: {e}")

# RSI
try:
    df[f"RSI{rsi_window}"] = ta.momentum.rsi(close, window=rsi_window)
except Exception:
    df[f"RSI{rsi_window}"] = pd.Series([np.nan]*len(df), index=df.index)

# MACD
try:
    macd = ta.trend.MACD(close, window_slow=macd_slow, window_fast=macd_fast, window_sign=macd_signal)
    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()
except Exception:
    df["MACD"] = pd.Series([np.nan]*len(df), index=df.index)
    df["MACD_SIGNAL"] = pd.Series([np.nan]*len(df), index=df.index)

# Bollinger
try:
    bb = ta.volatility.BollingerBands(close, window=bb_window, window_dev=bb_std)
    df["BB_MIDDLE"] = bb.bollinger_mavg()
    df["BB_UPPER"]  = bb.bollinger_hband()
    df["BB_LOWER"]  = bb.bollinger_lband()
except Exception:
    df[["BB_MIDDLE","BB_UPPER","BB_LOWER"]] = pd.DataFrame(np.nan, index=df.index, columns=["BB_MIDDLE","BB_UPPER","BB_LOWER"])

# Stochastic %K
try:
    df["STO_K"] = ta.momentum.stoch(high, low, close, window=14, smooth_window=3)
except Exception:
    df["STO_K"] = pd.Series([np.nan]*len(df), index=df.index)

# drop rows with NaNs in core indicators
df = df.dropna(subset=[f"EMA{ema_short}", f"EMA{ema_long}"]).copy()
if df.empty:
    st.error("بعد از محاسبه اندیکاتورها، داده‌ای برای بک‌تست باقی نماند (ممکن است دوره‌ها خیلی بزرگ باشند).")
    st.stop()

# -------------------------
# Entry/Exit conditions selection
# -------------------------
st.sidebar.header("🔁 Entry / Exit Conditions")
all_conditions = [
    f"EMA cross {ema_short}/{ema_long}",
    f"SMA cross {int(sma_short)}/{int(sma_long)}",
    f"RSI < 30 ({rsi_window})",
    f"RSI > 70 ({rsi_window})",
    "MACD cross",
    "BB touch lower",
    "BB breakout upper",
    "Price cross EMA short",
    "Stochastic < 20",
]

# default selections if session state has presets applied
default_entry = st.session_state.get('entry', [f"EMA cross {ema_short}/{ema_long}"])
default_exit  = st.session_state.get('exit', [f"EMA cross {ema_short}/{ema_long}", f"RSI > 70 ({rsi_window})"]) 

entry_choices = st.sidebar.multiselect("Entry conditions (choose 1+):", all_conditions, default=default_entry)
exit_choices  = st.sidebar.multiselect("Exit conditions (choose 1+):", all_conditions, default=default_exit)
combine_mode = st.sidebar.radio("Combine entry/exit rules using:", ["Any (OR)", "All (AND)"], index=0)

# -------------------------
# Prepare boolean series/functions for conditions
# -------------------------
# Helper to detect crosses (rising cross)
def cross_up(a, b, i):
    return (a.iloc[i-1] <= b.iloc[i-1]) and (a.iloc[i] > b.iloc[i])

def cross_down(a, b, i):
    return (a.iloc[i-1] >= b.iloc[i-1]) and (a.iloc[i] < b.iloc[i])

# compute condition series where possible
cond_map = {}
cond_map[f"EMA cross {ema_short}/{ema_long}"] = ((df[f"EMA{ema_short}"] > df[f"EMA{ema_long}"]), (df[f"EMA{ema_short}"] < df[f"EMA{ema_long}"]))
cond_map[f"SMA cross {int(sma_short)}/{int(sma_long)}"] = ((df[f"SMA{int(sma_short)}"] > df[f"SMA{int(sma_long)}"]), (df[f"SMA{int(sma_short)}"] < df[f"SMA{int(sma_long)}"]))
cond_map[f"RSI < 30 ({rsi_window})"] = (df[f"RSI{rsi_window}"] < 30, None)
cond_map[f"RSI > 70 ({rsi_window})"] = (df[f"RSI{rsi_window}"] > 70, None)
cond_map["MACD cross"] = ((df["MACD"] > df["MACD_SIGNAL"]), (df["MACD"] < df["MACD_SIGNAL"]))
cond_map["BB touch lower"] = (df["Close"] < df["BB_LOWER"], None)
cond_map["BB breakout upper"] = (df["Close"] > df["BB_UPPER"], None)
cond_map["Price cross EMA short"] = ((df["Close"] > df[f"EMA{ema_short}"]), (df["Close"] < df[f"EMA{ema_short}"]))
cond_map["Stochastic < 20"] = (df["STO_K"] < 20, None)

# -------------------------
# Backtest loop with SL/TP and time window
# -------------------------
balance = float(initial_bal)  # cash (realized)
position = None
trades = []

# equity history (includes unrealized PnL)
equity_series = pd.Series(index=df.index, dtype=float)

for i in range(1, len(df)):
    cur_idx = df.index[i]
    price = df["Close"].iloc[i]

    # check time window for entries
    hour_ok = True
    if has_datetime_index:
        h = cur_idx.hour
        # allow window wrap-around (e.g., start 20, end 4)
        if trade_start_hour <= trade_end_hour:
            hour_ok = (h >= trade_start_hour) and (h <= trade_end_hour)
        else:
            hour_ok = (h >= trade_start_hour) or (h <= trade_end_hour)
    else:
        # no datetime — cannot enforce
        hour_ok = True

    # evaluate each selected condition at index i (for crossover conditions we will detect edge)
    entry_flags = []
    exit_flags  = []
    for cond in entry_choices:
        if cond not in cond_map:
            entry_flags.append(False)
            continue
        series_true, series_false = cond_map[cond]
        # if it's a crossover pair (series_true exists and we want cross up)
        if isinstance(series_true, pd.Series) and series_false is not None:
            try:
                val = cross_up(series_true, series_false, i)
            except Exception:
                val = False
        else:
            # threshold condition
            try:
                val = bool(series_true.iloc[i])
            except Exception:
                val = False
        entry_flags.append(val)

    for cond in exit_choices:
        if cond not in cond_map:
            exit_flags.append(False)
            continue
        series_true, series_false = cond_map[cond]
        if isinstance(series_true, pd.Series) and series_false is not None:
            try:
                val = cross_down(series_true, series_false, i)
            except Exception:
                val = False
        else:
            try:
                val = bool(series_true.iloc[i])
            except Exception:
                val = False
        exit_flags.append(val)

    # combine according to mode
    if len(entry_flags) == 0:
        enter_signal = False
    else:
        enter_signal = any(entry_flags) if combine_mode.startswith("Any") else all(entry_flags)

    if len(exit_flags) == 0:
        rule_exit_signal = False
    else:
        rule_exit_signal = any(exit_flags) if combine_mode.startswith("Any") else all(exit_flags)

    # equity while holding
    if position is None:
        equity_series.iloc[i] = balance
    else:
        # unrealized pnl
        units = position["units"]
        unreal = (price - position["entry_price"]) * units
        equity_series.iloc[i] = balance + unreal

    # entry logic: open only if not in position and inside time window
    if enter_signal and position is None and hour_ok:
        # determine exposure
        if position_sizing_mode.startswith("Percent"):
            exposure = balance * (trade_pct / 100.0) * leverage
        else:
            exposure = float(fixed_size) * leverage
        units = exposure / price if price > 0 else 0

        # Default price-based SL/TP removed (set to disabled by default)
        sl_price = -np.inf
        tp_price = np.inf

        # If equity-based SL is enabled, compute SL price from equity % (risk_usd)
        if use_equity_sl and units > 0:
            risk_usd = balance * (sl_equity_pct / 100.0) if 'sl_equity_pct' in locals() else 0.0
            if risk_usd > 0:
                sl_price = price - (risk_usd / units)

        # If equity-based TP is enabled, compute TP price from equity % (target_usd)
        if use_equity_tp and units > 0:
            target_usd = balance * (tp_equity_pct / 100.0) if 'tp_equity_pct' in locals() else 0.0
            if target_usd > 0:
                tp_price = price + (target_usd / units)

        position = {
            "entry_index": cur_idx,
            "entry_price": price,
            "exposure": exposure,
            "units": units,
            "sl_price": sl_price,
            "tp_price": tp_price,
        }

    # exit logic: close if in position and either rule triggered OR sl/tp hit
    if position is not None:
        exit_by_sl = price <= position["sl_price"]
        exit_by_tp = price >= position["tp_price"]
        if (rule_exit_signal or exit_by_sl or exit_by_tp):
            exit_price = price
            units = position["units"]
            realized_pnl = (exit_price - position["entry_price"]) * units
            balance += realized_pnl
            trades.append({
                "Entry Time": position["entry_index"],
                "Entry Price": position["entry_price"],
                "Exit Time": cur_idx,
                "Exit Price": exit_price,
                "Units": units,
                "Exposure": position["exposure"],
                "Profit": realized_pnl,
                "Exit Reason": "TP" if exit_by_tp else ("SL" if exit_by_sl else "Rule")
            })
            position = None
            equity_series.iloc[i] = balance

# close last open position at final price
if position is not None:
    last_price = df["Close"].iloc[-1]
    units = position["units"]
    realized_pnl = (last_price - position["entry_price"]) * units
    balance += realized_pnl
    trades.append({
        "Entry Time": position["entry_index"],
        "Entry Price": position["entry_price"],
        "Exit Time": df.index[-1],
        "Exit Price": last_price,
        "Units": units,
        "Exposure": position["exposure"],
        "Profit": realized_pnl,
        "Exit Reason": "Close at end"
    })
    position = None
    equity_series.iloc[-1] = balance

# fill any remaining NaNs in equity_series
equity_series = equity_series.fillna(method="ffill").fillna(initial_bal)

# -------------------------
# Compute per-trade drawdown and overall metrics
# -------------------------
trades_df = pd.DataFrame(trades)

# compute per-trade max drawdown using equity slice between entry and exit
trade_drawdowns = []
for idx, tr in trades_df.iterrows():
    start = tr["Entry Time"]
    end = tr["Exit Time"]
    try:
        slice_eq = equity_series.loc[start:end].copy()
        if len(slice_eq) <= 1:
            md = 0.0
        else:
            peak = slice_eq.cummax()
            dd = (peak - slice_eq) / peak
            md = dd.max()
            if not np.isfinite(md):
                md = 0.0
    except Exception:
        md = 0.0
    trade_drawdowns.append(md)

if not trades_df.empty:
    trades_df["Max Drawdown (trade, %) "] = [d * 100 for d in trade_drawdowns]

# overall max drawdown
if not equity_series.empty:
    peak = equity_series.cummax()
    dd = (peak - equity_series) / peak
    overall_max_dd = dd.max() * 100
else:
    overall_max_dd = 0.0

# -------------------------
# Results display
# -------------------------
st.subheader("📈 Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Trades", len(trades_df))
win_rate = (trades_df["Profit"] > 0).mean() * 100 if not trades_df.empty else 0.0
col2.metric("Win rate", f"{win_rate:.2f}%")
avg_pl = trades_df["Profit"].mean() if not trades_df.empty else 0.0
col3.metric("Avg P/L", f"{avg_pl:.2f} USD")
final_equity = equity_series.iloc[-1] if not equity_series.empty else initial_bal
col4.metric("Final equity", f"{final_equity:.2f} USD")

st.metric("Max drawdown (equity)", f"{overall_max_dd:.2f}%")

st.subheader("📊 Trades detail")
if trades_df.empty:
    st.info("⚠️ No trades were generated with current rules/settings.")
else:
    st.dataframe(trades_df.sort_values(by="Entry Time"))

# -------------------------
# Plot: Price + indicators + markers and Equity
# -------------------------
st.subheader("📉 Charts")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [3, 1]})

# price and indicators
ax1.plot(df.index, df["Close"], label="Close", linewidth=1.2)
if f"EMA{ema_short}" in df.columns:
    ax1.plot(df.index, df[f"EMA{ema_short}"], label=f"EMA{ema_short}")
if f"EMA{ema_long}" in df.columns:
    ax1.plot(df.index, df[f"EMA{ema_long}"], label=f"EMA{ema_long}")
if f"SMA{int(sma_short)}" in df.columns:
    ax1.plot(df.index, df[f"SMA{int(sma_short)}"], label=f"SMA{int(sma_short)}", linestyle='--')
if f"SMA{int(sma_long)}" in df.columns:
    ax1.plot(df.index, df[f"SMA{int(sma_long)}"], label=f"SMA{int(sma_long)}", linestyle='--')

# plot Bollinger bands if present
if "BB_UPPER" in df.columns:
    ax1.fill_between(df.index, df["BB_LOWER"], df["BB_UPPER"], alpha=0.08)

# mark entries/exits
if not trades_df.empty:
    for _, tr in trades_df.iterrows():
        color = "green" if tr["Profit"] >= 0 else "red"
        ax1.scatter(tr["Entry Time"], tr["Entry Price"], marker="^", color="green", s=80, zorder=5)
        ax1.scatter(tr["Exit Time"], tr["Exit Price"], marker="v", color=color, s=80, zorder=5)

ax1.set_title("Price & indicators (entries=green, exits=red/green)")
ax1.legend(loc="upper left", fontsize=8)
ax1.grid(alpha=0.3)

# equity
ax2.plot(equity_series.index, equity_series.values, linewidth=1.5)
ax2.set_title("Equity curve")
ax2.grid(alpha=0.3)

st.pyplot(fig)

# -------------------------
# Download full report (Excel or CSV fallback)
# -------------------------
st.subheader("📥 Download report")
if not trades_df.empty:
    to_download = BytesIO()
    excel_written = False
    # try to pick an available engine
    engine = None
    try:
        import xlsxwriter
        engine = 'xlsxwriter'
    except Exception:
        try:
            import openpyxl
            engine = 'openpyxl'
        except Exception:
            engine = None

    try:
        if engine is not None:
            with pd.ExcelWriter(to_download, engine=engine) as writer:
                trades_df.to_excel(writer, sheet_name="trades", index=False)
                equity_series.to_frame(name="Equity").to_excel(writer, sheet_name="equity")
                summary = pd.DataFrame({
                    "Initial capital": [initial_bal],
                    "Final equity": [final_equity],
                    "Total trades": [len(trades_df)],
                    "Win rate (%)": [win_rate],
                    "Max drawdown (%)": [overall_max_dd],
                })
                summary.to_excel(writer, sheet_name="summary", index=False)
            to_download.seek(0)
            st.download_button("Download full report (Excel)", to_download, file_name="backtest_report.xlsx")
            excel_written = True
        else:
            raise ImportError("No excel engine available")
    except Exception as e:
        # fallback to CSVs
        st.error(f"خطا در ساخت فایل اکسل: {e} — ارائه CSV به‌عنوان جایگزین")
        csv_trades = trades_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download trades CSV", csv_trades, file_name="trades.csv")
        csv_equity = equity_series.to_csv(index=True).encode("utf-8")
        st.download_button("Download equity CSV", csv_equity, file_name="equity.csv")
else:
    st.info("هیچ معامله‌ای برای دانلود موجود نیست.")

st.markdown("---")
st.caption("Notes: Leverage is applied as a multiplier to exposure (exposure = percent_of_equity * equity * leverage). SL/TP are applied as absolute price thresholds from entry if enabled. If گزینه‌های «Enable equity-based SL/TP» فعال باشند، حدضرر/سود بر اساس درصدی از موجودی حساب به قیمت تبدیل می‌شود (مثال: 2٪ از 1000$ = 20$). Entries are only allowed inside selected time window; exits may occur due to rules or SL/TP. Currently only long positions are supported. If you want short selling, margin interest, or commissions, tell me and I will add them.")
