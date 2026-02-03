#!/bin/bash
# Art Trader Demo UI Launcher

echo "🚀 Starting Art Trader Demo Dashboard..."
echo "📊 This demo uses mock data to show the complete trading workflow"

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing requirements..."
    pip3 install -r requirements.txt
fi

# Start the Streamlit demo app
echo "🌐 Opening demo dashboard at http://localhost:8502"
echo "💡 Try the following:"
echo "   1. Go to 'Bet Discovery' and click 'Scan Polymarket'"
echo "   2. Review proposals in 'Pending Proposals'"  
echo "   3. Approve a trade to see it in 'Active Trades'"
echo "   4. Monitor performance and get AI recommendations"
echo ""
streamlit run trading_ui_demo.py --server.port 8502 --server.headless false