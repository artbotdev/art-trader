#!/bin/bash
# Art Trader: Prediction Markets Setup Script

echo "🚀 Art Trader: Setting up Prediction Markets Integration"
echo "========================================================="

# Check if we're in the right directory
if [[ ! -f "polymarket-alpaca-mapper.py" ]]; then
    echo "❌ Error: Run this script from the art-trader project directory"
    exit 1
fi

echo "📍 Current directory: $(pwd)"

# 1. Check mcporter is installed
echo -e "\n1. Checking mcporter installation..."
if command -v mcporter &> /dev/null; then
    echo "✅ mcporter found"
    mcporter config list | grep -E "(alpaca|polymarket)" || echo "⚠️  No trading servers configured yet"
else
    echo "❌ mcporter not found. Please install mcporter first."
    exit 1
fi

# 2. Check Alpaca MCP server
echo -e "\n2. Testing Alpaca connection..."
if mcporter call alpaca.get_account_info &> /dev/null; then
    echo "✅ Alpaca MCP server working"
    ALPACA_STATUS="✅ Connected"
else
    echo "⚠️  Alpaca MCP server not responding"
    ALPACA_STATUS="❌ Not connected"
fi

# 3. Check Polymarket MCP server
echo -e "\n3. Testing Polymarket connection..."
if [[ -d "polymarket-mcp" ]]; then
    echo "✅ Polymarket MCP server downloaded"
    
    # Check if it's configured with mcporter
    if mcporter list polymarket &> /dev/null; then
        echo "✅ Polymarket server configured"
        POLYMARKET_STATUS="✅ Configured"
    else
        echo "⚠️  Polymarket server not configured with mcporter"
        POLYMARKET_STATUS="⚠️  Not configured"
    fi
else
    echo "❌ Polymarket MCP server not found"
    POLYMARKET_STATUS="❌ Not installed"
fi

# 4. Check Python dependencies
echo -e "\n4. Checking Python environment..."
python3 -c "import json, subprocess, datetime; print('✅ Basic Python modules available')" 2>/dev/null || {
    echo "❌ Python3 or required modules not available"
    exit 1
}

# 5. Make scripts executable
echo -e "\n5. Setting up executable permissions..."
chmod +x test-polymarket-connection.py
chmod +x prediction-trader.py
chmod +x polymarket-alpaca-mapper.py
echo "✅ Scripts are now executable"

# 6. Test configuration
echo -e "\n6. Running connection tests..."
echo "🧪 Testing Prediction Trading System..."

if python3 test-polymarket-connection.py | tail -1 | grep -q "All systems operational"; then
    INTEGRATION_STATUS="✅ Ready"
else
    INTEGRATION_STATUS="⚠️  Issues detected"
fi

# Summary
echo -e "\n========================================================="
echo "📋 SETUP SUMMARY"
echo "========================================================="
echo "Alpaca Trading:     $ALPACA_STATUS"
echo "Polymarket Data:    $POLYMARKET_STATUS" 
echo "Integration:        $INTEGRATION_STATUS"
echo ""

if [[ "$ALPACA_STATUS" == "✅ Connected" && "$POLYMARKET_STATUS" == "✅ Configured" ]]; then
    echo "🎉 Art Trader is ready for prediction-based trading!"
    echo ""
    echo "📚 How to use:"
    echo "   • Test everything: python3 test-polymarket-connection.py"
    echo "   • Single run:      python3 prediction-trader.py"  
    echo "   • Continuous:      python3 prediction-trader.py --continuous"
    echo ""
    echo "⚠️  SAFETY REMINDER:"
    echo "   • This uses PAPER TRADING (fake money)"
    echo "   • Max position size: 2% per trade"
    echo "   • Max daily trades: 10"
    echo "   • Always monitor your trades"
else
    echo "⚠️  Setup incomplete. Please fix the issues above before trading."
    echo ""
    echo "🔧 Troubleshooting:"
    if [[ "$ALPACA_STATUS" != "✅ Connected" ]]; then
        echo "   • Check Alpaca API keys in mcporter config"
        echo "   • Verify: mcporter call alpaca.get_account_info"
    fi
    if [[ "$POLYMARKET_STATUS" != "✅ Configured" ]]; then
        echo "   • Ensure polymarket-mcp directory exists"
        echo "   • Run: mcporter config add polymarket --transport stdio --command node --args $(pwd)/polymarket-mcp/build/index.js"
    fi
fi

echo ""
echo "📊 Current Account Status:"
mcporter call alpaca.get_account_info 2>/dev/null | grep -E "(Balance|Buying Power)" || echo "   (Run test to see account details)"

echo ""
echo "🚀 Ready to make money from prediction markets!"