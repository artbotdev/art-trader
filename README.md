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

## 🔮 **NEW: Multi-Platform Prediction Markets Integration**

### **Polymarket + Kalshi + PredictIt → Alpaca Strategy**
**Revolutionary approach**: Cross-platform prediction market intelligence for superior alpha

**How it works**:
1. **Monitor 3 platforms** - Polymarket, Kalshi, PredictIt simultaneously  
2. **Find consensus signals** - When multiple platforms agree (higher confidence)
3. **Detect arbitrage** - Platform price differences reveal opportunities
4. **Execute via Alpaca** - Confidence-based position sizing and execution

### **Enhanced Strategies**
- **Consensus trades**: All platforms agree = 2.0% position size
- **Arbitrage plays**: Platform differences = directional signals  
- **Early warnings**: Platform divergence = avoid false signals
- **Risk reduction**: Multi-source validation reduces bad trades

### **Platform Strengths**
- **Polymarket**: Crypto-native, global traders, high liquidity
- **Kalshi**: CFTC-regulated, US institutional money  
- **PredictIt**: Academic traders, political expertise

### **Current Setup**
✅ Polymarket MCP server installed  
✅ Multi-platform MCP server installed (Polymarket + Kalshi + PredictIt)  
✅ Alpaca integration working ($100k paper trading)  
✅ Enhanced risk management (consensus-based position sizing)  
✅ Cross-platform demo ready  

**Try it**: `python3 demo-prediction-trading.py`  
**Enhanced**: `python3 multi-prediction-demo.py`

---
**Created**: 2026-02-02  
**Enhanced**: 2026-02-02 with Prediction Markets  
**Repository**: Public on GitHub as artbotdev/art-trader