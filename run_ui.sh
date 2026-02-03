#!/bin/bash
# Art Trader UI Launcher

echo "🚀 Starting Art Trader Dashboard..."

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing requirements..."
    pip3 install -r requirements.txt
fi

# Start the Streamlit app
echo "🌐 Opening dashboard at http://localhost:8501"
streamlit run trading_ui.py --server.port 8501 --server.headless false
