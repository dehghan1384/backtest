# 🚀 BacktestPro — Enhanced Backtester  

**A powerful, interactive trading strategy backtester built with [Streamlit](https://streamlit.io/).**  
Easily test trading strategies using historical Forex/stock data, customize indicators, apply presets, and analyze results with equity curves, trade logs, and downloadable reports.  

![Preview](https://img.shields.io/badge/Streamlit-App-blue?logo=streamlit)  
![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)  


---

## 📑 Table of Contents
- [Introduction](#-introduction)  
- [Features](#-features)  
- [Installation](#-installation)  
- [Usage](#-usage)  
- [Indicators & Strategies](#-indicators--strategies)  
- [Configuration](#-configuration)  
- [Reports & Exports](#-reports--exports)  
- [Examples](#-examples)  
- [Troubleshooting](#-troubleshooting)  
- [Contributors](#-contributors)  


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
