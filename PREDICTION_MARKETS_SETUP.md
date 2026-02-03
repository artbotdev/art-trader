# Art Trader: Prediction Markets Setup

Integration status for Polymarket and Kalshi MCP servers with Art Trader.

## ✅ **Current Setup**

### **Polymarket MCP Server - INSTALLED**
- **Source**: `guangxiangdebizi/PolyMarket-MCP` (most comprehensive)
- **Location**: `projects/art-trader/polymarket-mcp/`
- **Status**: Server built and configured with mcporter
- **Configuration**: `mcporter config polymarket`

### **Available Tools** (Once Connected)
```bash
# Get active prediction markets
mcporter call polymarket.get_markets active=true order=volume limit=20

# Get specific events (elections, Fed decisions, etc.)
mcporter call polymarket.get_events search="election" active=true

# Get market prices with technical analysis
mcporter call polymarket.get_market_prices market_id=XXX include_orderbook=true

# Get user positions for analysis
mcporter call polymarket.get_user_positions user_address=0x... limit=50

# Get trading history
mcporter call polymarket.get_trades market_id=XXX limit=100

# Get order book with liquidity analysis
mcporter call polymarket.get_order_book market_id=XXX include_liquidity_analysis=true
```

## 🎯 **Trading Strategy Integration**

### **Art Trader Pipeline**
```
1. Polymarket Data → mcporter call polymarket.get_markets
2. Signal Analysis → Custom analysis of probability shifts
3. Traditional Trades → mcporter call alpaca.place_stock_order
4. Risk Management → Position sizing and stop losses
```

### **Example Strategy Flow**
```bash
# 1. Monitor election markets
mcporter call polymarket.get_events search="2024" active=true

# 2. Check probability shifts  
mcporter call polymarket.get_market_prices market_id=election_market interval=1h

# 3. Execute traditional trades based on implications
mcporter call alpaca.place_stock_order symbol=RTX side=buy quantity=10 order_type=market
```

## 📊 **Kalshi Integration (Next)**

### **Available MCP Servers**
1. **`@newyorkcompute/kalshi-mcp`** - Direct Kalshi integration
2. **`jamesanz-prediction-markets`** - Multi-platform (Polymarket + Kalshi + PredictIt)

### **Installation Plan**
```bash
# Option 1: Kalshi-specific
npm install -g @newyorkcompute/kalshi-mcp
mcporter config add kalshi --command "kalshi-mcp"

# Option 2: Multi-platform server  
git clone https://github.com/JamesANZ/prediction-markets-mcp
mcporter config add prediction-markets --command "node" --args "path/to/server.js"
```

## 🔄 **Current Integration with Art Trader**

### **Alpaca + Polymarket Strategy**
```
Art Trader Account Status:
✅ $100,000 paper trading balance
✅ $200,000 buying power  
✅ Real market data via Alpaca MCP
✅ Polymarket data via Polymarket MCP (configured)

Combined Strategy:
Polymarket signals → Traditional market trades → Real execution via Alpaca
```

### **Risk Management Framework**
- **Max position size**: 2% of account per prediction-based trade
- **Stop losses**: 10% on individual positions  
- **Time limits**: Close before predicted events resolve
- **Correlation limits**: Max exposure to correlated predictions

## 🎯 **Next Actions**

### **Phase 1: Test Polymarket Connection**
```bash
# Test if server responds
mcporter list polymarket

# Get sample market data
mcporter call polymarket.get_markets limit=3

# Test specific market analysis
mcporter call polymarket.get_market_prices market_id=XXX
```

### **Phase 2: Build Analysis Tools**
- **Probability shift detection**
- **Correlation analysis** (predictions → traditional markets)
- **Signal strength scoring**
- **Risk assessment**

### **Phase 3: Automated Trading**
- **Monitor prediction markets** via cron
- **Generate trading signals**
- **Execute trades** via Alpaca
- **Track performance** and P&L

## 💡 **Strategy Examples Ready to Implement**

### **Election Trading**
```
Signal: Republican House odds increase 60% → 75%
Action: Buy defense stocks (RTX, LMT), energy (XLE)
Logic: Policy implications favor these sectors
```

### **Fed Rate Predictions**
```
Signal: Rate cut probability increases 30% → 60%  
Action: Buy REITs (VNQ), utilities (XLU)
Logic: Rate cuts benefit dividend-paying stocks
```

### **Tech Earnings**
```
Signal: "Apple beats by 5%" odds increase 45% → 70%
Action: Buy AAPL call options
Logic: Direct correlation prediction → outcome
```

---
**Status**: Polymarket MCP server installed and configured. Ready for live trading integration with Art Trader system.

**Repository**: https://github.com/artbotdev/art-trader  
**Account**: $100k paper trading ready for prediction-based strategies