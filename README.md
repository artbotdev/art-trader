# Art Trader 👾📈

Art's AI-powered trading system built on OpenClaw with Alpaca Markets integration.

## 🎯 Current Status: LIVE & OPERATIONAL

### 💰 Account Details
- **Platform**: Alpaca Markets (Paper Trading)
- **Balance**: $100,000 virtual money
- **Buying Power**: $200,000 (2x margin)
- **API Keys**: Configured and working
- **MCP Integration**: Functional via mcporter

### 📊 Capabilities
- **Stock Trading**: Market/limit orders for stocks and ETFs
- **Options Trading**: Single and multi-leg strategies with Greeks
- **Crypto Trading**: Bitcoin, Ethereum, and other assets
- **Real-time Data**: Live quotes, historical data, market snapshots
- **Portfolio Management**: Position tracking and analysis

### 🛠 Technical Setup
```bash
# Account info
mcporter call alpaca.get_account_info

# Current positions  
mcporter call alpaca.get_all_positions

# Place stock order
mcporter call alpaca.place_stock_order symbol=AAPL side=buy quantity=1 order_type=market

# Get market data
mcporter call alpaca.get_stock_latest_quote symbol_or_symbols=TSLA
```

### 🔗 Resources
- **GitHub Repo**: https://github.com/artbotdev/art-trader
- **API Documentation**: Alpaca MCP Server
- **Configuration**: ~/.openclaw/workspace/config/mcporter.json

## ⚠️ Safety
All trading is done with **paper money** (fake money, real market data). No real financial risk.

## 🚀 **NEW: Complete Trading UI & Management System**

### **Comprehensive Trading Dashboard**
**Full-featured UI**: From bet discovery to trade execution and performance monitoring

**Features**:
1. **🔍 Bet Discovery** - Scan Polymarket for finance-related opportunities
2. **📋 Trade Proposals** - AI-generated recommendations with manual approval
3. **📊 Active Trades** - Real-time monitoring and performance tracking
4. **⚡ One-Click Actions** - Approve, execute, and close positions

### **How It Works**
1. **Discover**: Scan Polymarket for finance/stock-related bets
2. **Assess**: AI analyzes relevance and generates trade proposals  
3. **Approve**: Manual review and approval of each trade
4. **Execute**: Automatic execution via Alpaca when approved
5. **Monitor**: Real-time tracking with performance metrics and recommendations

### **UI Components**
- **Smart Discovery**: Finance keyword filtering with relevance scoring
- **Trade Intelligence**: Symbol mapping and confidence-based position sizing
- **Approval Workflow**: Manual oversight with detailed reasoning
- **Performance Dashboard**: Real-time P&L, recommendations, and actions
- **Persistent Storage**: SQLite database for all trades and history

### **Quick Start**
```bash
# Launch the full UI dashboard
./run_ui.sh

# Or use CLI for quick operations
./trader_cli.py scan        # Discover new bets
./trader_cli.py proposals   # View pending proposals  
./trader_cli.py trades      # Check active positions
./trader_cli.py update      # Update all prices
```

### **Enhanced Multi-Platform Integration**
- **Polymarket**: Primary source for prediction market intelligence
- **Alpaca Markets**: Execution platform with $100k paper trading
- **Cross-validation**: Multiple data sources for higher confidence trades
- **Risk Management**: Confidence-based position sizing and stop-loss recommendations

---
**Created**: 2026-02-02  
**Enhanced**: 2026-02-02 with Prediction Markets  
**Repository**: Public on GitHub as artbotdev/art-trader