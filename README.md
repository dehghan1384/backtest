Install dependencies

bash
pip install streamlit pandas matplotlib numpy ta
Run the application
bash
streamlit run backtestpro.py
🖥️ Usage Guide
Upload market data (CSV/TSV with OHLC format)

Configure indicators in sidebar

Set entry/exit conditions

Adjust money management (leverage, position sizing)

Apply time filters for trading sessions

Run backtest and analyze results

Download full report (Excel/CSV)

⚙️ Configuration Options
Strategy Parameters
Parameter	Description	Default
EMA Short	Short EMA window	9
EMA Long	Long EMA window	21
RSI Window	RSI period	14
MACD Settings	Fast/Slow/Signal periods	12/26/9
Money Management
Feature	Description
Equity-based SL/TP	Risk management by account percentage
Position Sizing	Fixed USD or % of equity
Leverage	1-100x multiplier
Initial Capital	Starting balance ($1000)
Advanced Features
Strategy Presets: Pre-configured trading strategies

Time Filtering: Limit trading to specific hours

Condition Combining: AND/OR logic for entry/exit rules

Dynamic Drawdown Calculation: Per-trade and equity-based

📊 Output Analytics
Trade-by-trade performance breakdown

Equity curve visualization

Win rate and avg profit metrics

Max drawdown analysis

Exit reason classification (TP/SL/Rule)

⚠️ Limitations & Notes
Currently supports long positions only

No commission/fee modeling

No margin interest calculation

Time filters require datetime index

Limited to daily timeframe data

🛣️ Roadmap
Short selling support

Commission/fee modeling

Multi-timeframe analysis

Walk-forward optimization

Monte Carlo simulations

🤝 Contributing
Contributions welcome! Please follow these steps:

Fork the repository

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request


Distributed under the MIT License. See LICENSE for more information.

Created with ❤️ by [Your Name]
