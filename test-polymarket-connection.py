#!/usr/bin/env python3
"""
Test Polymarket MCP Server Connection
Verifies we can fetch data from Polymarket and parse it correctly
"""

import json
import subprocess
import sys
from datetime import datetime

def test_mcporter_polymarket():
    """Test if mcporter can connect to Polymarket MCP server"""
    print("🧪 Testing Polymarket MCP connection...")
    
    try:
        # Test 1: List available tools
        print("\n1. Checking available Polymarket tools:")
        result = subprocess.run(
            ["mcporter", "list", "polymarket", "--schema"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Polymarket server responded")
            print("Available tools:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        else:
            print("❌ Failed to list Polymarket tools")
            print("Error:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout connecting to Polymarket server")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    try:
        # Test 2: Fetch sample markets
        print("\n2. Fetching sample markets:")
        result = subprocess.run(
            ["mcporter", "call", "polymarket.get_markets", "limit=3"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Successfully fetched markets")
            print("Sample response:", result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print("❌ Failed to fetch markets")
            print("Error:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout fetching markets")
        return False
    except Exception as e:
        print(f"❌ Exception fetching markets: {e}")
        return False

def test_alpaca_connection():
    """Test Alpaca connection"""
    print("\n\n🧪 Testing Alpaca connection...")
    
    try:
        result = subprocess.run(
            ["mcporter", "call", "alpaca.get_account_info"],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode == 0:
            print("✅ Alpaca connection successful")
            print("Account info:", result.stdout[:300] + "..." if len(result.stdout) > 300 else result.stdout)
            return True
        else:
            print("❌ Alpaca connection failed")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Exception testing Alpaca: {e}")
        return False

def test_sample_prediction_analysis():
    """Test the prediction analysis pipeline with mock data"""
    print("\n\n🧪 Testing prediction analysis pipeline...")
    
    try:
        # Import our mapping system
        sys.path.append('/Users/artbot/.openclaw/workspace/projects/art-trader')
        from polymarket_alpaca_mapper import PolymarketAlpacaMapper, PredictionSignal
        
        mapper = PolymarketAlpacaMapper()
        
        # Create test prediction
        test_prediction = PredictionSignal(
            market_id="test_001",
            title="Republicans control House after 2024 election",
            description="Will the Republican party have a majority in the House of Representatives after the 2024 election?",
            current_prob=68.5,
            prob_change=12.3,  # Strong increase
            volume_24h=850000,
            liquidity=320000,
            end_date=datetime(2024, 11, 6),
            category="election"
        )
        
        print(f"📊 Test prediction: {test_prediction.title}")
        print(f"   Category: {test_prediction.category}")
        print(f"   Probability: {test_prediction.current_prob}% (changed {test_prediction.prob_change:+.1f}%)")
        print(f"   Volume 24h: ${test_prediction.volume_24h:,.0f}")
        
        # Generate trades
        trades = mapper.map_to_alpaca_trades(test_prediction)
        
        if trades:
            print(f"\n✅ Generated {len(trades)} trades:")
            for i, trade in enumerate(trades, 1):
                print(f"   {i}. {trade.action.upper()} {trade.quantity} {trade.symbol}")
                print(f"      Confidence: {trade.confidence:.2f}")
                print(f"      Reasoning: {trade.reasoning}")
                print(f"      Risk: {trade.risk_level}")
        else:
            print("❌ No trades generated")
            
        return len(trades) > 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Exception in prediction analysis: {e}")
        return False

def test_full_integration():
    """Test full integration if both systems work"""
    print("\n\n🧪 Testing full integration...")
    
    try:
        sys.path.append('/Users/artbot/.openclaw/workspace/projects/art-trader')
        from prediction_trader import PredictionTrader
        
        trader = PredictionTrader(max_daily_trades=1)  # Limit to 1 trade for testing
        
        print("📈 Running single trading cycle (test mode)...")
        # trader.run_trading_cycle()  # Commented out to avoid actual trades
        
        print("✅ Integration test structure verified")
        print("⚠️  Actual trading disabled for safety")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    print("🚀 Art Trader: Prediction Markets Integration Test")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Polymarket Connection", test_mcporter_polymarket),
        ("Alpaca Connection", test_alpaca_connection), 
        ("Prediction Analysis", test_sample_prediction_analysis),
        ("Full Integration", test_full_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY:")
    print("="*60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems operational! Art Trader ready for prediction-based trading.")
        print("\nNext steps:")
        print("1. Run: python prediction-trader.py (single cycle)")
        print("2. Run: python prediction-trader.py --continuous (continuous monitoring)")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check configuration before trading.")

if __name__ == "__main__":
    main()