🚀 BacktestPro — Enhanced Backtester

A powerful, interactive trading strategy backtester built with Streamlit
.
Easily test trading strategies using historical Forex/stock data, customize indicators, apply presets, and analyze results with equity curves, trade logs, and downloadable reports.






📑 Table of Contents

Introduction

Features

Installation

Usage

Indicators & Strategies

Configuration

Reports & Exports

Examples

Troubleshooting

Contributors

License

🌟 Introduction

BacktestPro — Enhanced is a flexible backtesting app designed for traders and quants who want to:

Upload historical market data (Forex, stocks, crypto).

Quickly test custom strategies with indicators and money management rules.

Get detailed results: win rate, equity curve, drawdowns, and trade logs.

Export a ready-to-share report (Excel/CSV).

👉 For sample Forex data, download from: forexsb.com/historical-forex-data
.

🔥 Features

✅ File upload — CSV/TSV (no header): Date/Time, Open, High, Low, Close
✅ Indicators supported:

EMA / SMA crossovers

RSI filters

MACD

Bollinger Bands

Stochastic Oscillator

✅ Strategy presets (1-click setup)
✅ Custom entry & exit conditions (AND/OR logic)
✅ Equity-based SL/TP (risk % & target %)
✅ Money management — fixed USD or % of equity, with leverage
✅ Time-windowed trading (only enter trades during specific hours)
✅ Charts & visualizations
✅ Detailed trade logs & metrics
✅ Export full reports (Excel with multiple sheets, or CSV fallback)

⚙️ Installation
# Clone repo
git clone https://github.com/your-username/backtestpro-enhanced.git
cd backtestpro-enhanced

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # on Linux/Mac
venv\Scripts\activate      # on Windows

# Install dependencies
pip install -r requirements.txt


Requirements:

Python 3.8+

Streamlit

Pandas

NumPy

TA (Technical Analysis library)

Matplotlib

XlsxWriter / OpenPyXL (for Excel reports)

▶️ Usage

Run the app locally:

streamlit run app.py


Then open your browser at http://localhost:8501
.

📁 Upload historical price data.

⚙️ Configure indicators, SL/TP, and money management.

🎯 Pick a strategy preset or define custom entry/exit rules.

📈 Run backtest → See equity curve, trades, and metrics.

📥 Download the Excel/CSV report.

📊 Indicators & Strategies
Built-in Presets

EMA9/21 + RSI filter → Trend-following with RSI-based exits

SMA50/200 Momentum → Golden Cross strategy

MACD trend-follow → Classic MACD signals

Bollinger mean-revert → Buy dips, sell bounces

Custom Rules

You can mix & match:

EMA cross short/long

SMA cross short/long

RSI <30 / >70

MACD crossovers

Bollinger Band touches/breakouts

Price cross EMA

Stochastic <20

🛠 Configuration

Initial Capital (default: $1000)

Position Sizing: % of equity or fixed USD

Leverage: 1x – 100x

SL/TP Modes: equity-based % (dynamic risk/reward)

Trading Hours: restrict entry to specific hours

📥 Reports & Exports

Excel report (if engine available):

📄 Trades

💰 Equity curve

📊 Summary metrics

CSV fallback (if Excel not supported).

💡 Examples

📉 Example Equity Curve and Trade Markers:

Green ▲ → Entry

Red ▼ → Losing exit

Green ▼ → Winning exit

🐞 Troubleshooting

Error reading file → Ensure CSV/TSV has 5+ columns: Date/Time, Open, High, Low, Close.

Indicators return NaN → Try smaller window sizes or provide longer historical data.

No trades generated → Adjust entry/exit conditions or trading hours.

Excel report error → Install either xlsxwriter or openpyxl.

👨‍💻 Contributors

Your Name — Creator & Developer

(Add more contributors if needed)

📜 License

MIT License © 2025 — Free to use, modify, and share.
