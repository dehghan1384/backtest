# 🚀 BacktestPro — Enhanced Backtester  

**A powerful, interactive trading strategy backtester built with [Streamlit](https://streamlit.io/).**  
Easily test trading strategies using historical Forex/stock data, customize indicators, apply presets, and analyze results with equity curves, trade logs, and downloadable reports.  

![Preview](https://img.shields.io/badge/Streamlit-App-blue?logo=streamlit)  
![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)  
![Python](https://img.shields.io/badge/TA--Lib-0.4.0+-yellowgreen.svg)  

---

## 📑 Table of Contents
- [Introduction](#-introduction)  
- [Features](#-features)  
- [Installation](#-installation)  
- [Requirements](#-Requirements)
- [Usage](#-usage)  
- [Configuration](#-configuration)  
- [Reports & Exports](#-reports--exports)  
- [Examples](#-examples)  
- [Troubleshooting](#-troubleshooting)  
- [Contributors](#-contributors)  
- [License](#-license)  

---

## 🌟 Introduction  

**BacktestPro — Enhanced** is a flexible **backtesting app** designed for traders and quants who want to:  

- Upload **historical market data** (Forex, stocks, crypto).  
- Quickly **test custom strategies** with indicators and money management rules.  
- Get **detailed results**: win rate, equity curve, drawdowns, and trade logs.  
- Export a **ready-to-share report** (Excel/CSV).  

👉 For sample Forex data, download from: [forexsb.com/historical-forex-data](https://forexsb.com/historical-forex-data).  

---

## 🔥 Features  

- 📁 **Upload historical price data** (CSV/TSV without header).  
- 📊 **Indicators supported**:  
  - EMA / SMA crossovers  
  - RSI filters  
  - MACD  
  - Bollinger Bands  
  - Stochastic Oscillator  
- 🎯 **Strategy presets** (one-click setup).  
- 🛠 **Custom entry & exit conditions** (AND/OR logic).  
- 📉 **Equity-based SL/TP** (risk % & target %).  
- 💰 **Money management** — fixed USD or % of equity, with leverage.  
- ⏱ **Time-windowed trading** (restrict entries to specific hours).  
- 📈 **Charts & visualizations**.  
- 📝 **Detailed trade logs & metrics**.  
- 📥 **Export full reports** (Excel with multiple sheets, or CSV fallback).  

---

## ⚙️ Installation  

```bash
# Clone repo
git clone https://github.com/your-username/backtestpro-enhanced.git
cd backtestpro-enhanced

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

## 📋 Requirements


Python 3.8+

Streamlit

Pandas

NumPy

TA (Technical Analysis library)

Matplotlib

---

## ▶️ Usage

Run the app locally:
```bash


streamlit run app.py

```
Then open your browser at http://localhost:8501
.

📁 Upload historical price data.

⚙️ Configure indicators, SL/TP, and money management.

🎯 Pick a strategy preset or define custom entry/exit rules.

📈 Run backtest → See equity curve, trades, and metrics.

📥 Download the Excel/CSV report.

---

## 🛠 Configuration

- Initial Capital (default: $1000)

- Position Sizing: % of equity or fixed USD

- Leverage: 1x – 100x

- SL/TP Modes: equity-based % (dynamic risk/reward)

- Trading Hours: restrict entry to specific hours
---

## 🤝 Contributing

I'm currently the sole developer of BacktestPro and would love to collaborate with others passionate about algorithmic trading and quantitative finance!

If you're interested in contributing:

Feel free to reach out directly at contact part at the end

Let me know what areas interest you (UI/UX, strategy development, performance optimization, etc.)

All skill levels welcome - there are tasks ranging from documentation to advanced features

I'm particularly interested in collaborating on:

Adding new technical indicators

Improving visualization capabilities

Optimizing backtesting performance

Developing more sophisticated risk management tools

---

**Created with ❤️ by Mohammad Dehghan** - [✉️ Contact](mailto:mohammad.dehghan8484@gmail.com)
Special thanks to all who have provided feedback and suggestions to improve BacktestPro!
