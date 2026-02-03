#!/usr/bin/env python3
"""
Setup script for Alpaca trading integration
Helps configure API keys and test connection
"""

import os
import getpass
from alpaca_trader import AlpacaTrader

def setup_alpaca_credentials():
    """Interactive setup for Alpaca API credentials"""
    
    print("🔑 Alpaca API Setup")
    print("=" * 50)
    print("Get your API keys from: https://app.alpaca.markets/paper/dashboard/overview")
    print()
    
    # Get API credentials
    api_key = input("Enter your Alpaca API Key: ").strip()
    secret_key = getpass.getpass("Enter your Alpaca Secret Key: ").strip()
    
    # Choose environment
    use_paper = input("Use paper trading? (Y/n): ").strip().lower()
    paper_trading = use_paper != 'n'
    
    if paper_trading:
        print("📝 Using PAPER TRADING (recommended for testing)")
    else:
        confirm = input("⚠️  LIVE TRADING - Are you sure? (type 'LIVE' to confirm): ")
        if confirm != 'LIVE':
            print("❌ Cancelled")
            return None, None, True
    
    # Test connection
    print("\n🧪 Testing connection...")
    try:
        trader = AlpacaTrader(api_key, secret_key, paper_trading)
        print("✅ Connection successful!")
        
        # Save credentials to environment file
        with open('.env', 'w') as f:
            f.write(f"ALPACA_API_KEY={api_key}\n")
            f.write(f"ALPACA_SECRET_KEY={secret_key}\n")
            f.write(f"ALPACA_PAPER_TRADING={paper_trading}\n")
        
        print("💾 Credentials saved to .env file")
        return api_key, secret_key, paper_trading
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None, None, paper_trading

def test_basic_operations():
    """Test basic trading operations"""
    print("\n🧪 Testing Basic Operations")
    print("=" * 50)
    
    try:
        # Load credentials
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        trader = AlpacaTrader(paper_trading=True)
        
        # Test 1: Get account info
        print("1️⃣ Account Info:")
        positions = trader.get_positions()
        print(f"   Current positions: {len(positions)}")
        
        # Test 2: Get market data
        print("2️⃣ Market Data Test:")
        data = trader.get_market_data('QQQ', '1Day', 5)
        if data and 'bars' in data:
            latest_price = data['bars']['QQQ'][-1]['c']
            print(f"   QQQ latest price: ${latest_price}")
        
        # Test 3: Simulated order (very small)
        print("3️⃣ Order Test (simulation):")
        print("   Note: Not placing actual order, just testing logic")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏦 Alpaca Trading Setup")
    print("=" * 50)
    
    # Check if already configured
    if os.path.exists('.env'):
        use_existing = input("Found existing .env file. Use existing credentials? (Y/n): ")
        if use_existing.strip().lower() != 'n':
            # Load existing and test
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
            
            print("📂 Using existing credentials")
            test_basic_operations()
        else:
            setup_alpaca_credentials()
    else:
        setup_alpaca_credentials()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run: python3 alpaca_trader.py")
    print("2. Test with small paper trades")
    print("3. Integrate with your morning briefing insights")
    print("4. Scale up once proven profitable")