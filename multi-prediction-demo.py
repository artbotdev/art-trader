#!/usr/bin/env python3
"""
Enhanced Multi-Platform Prediction Markets Demo
Shows integration with Polymarket + Kalshi + PredictIt
"""

import json
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional

def test_prediction_sources():
    """Test all available prediction market sources"""
    print("🔍 TESTING PREDICTION MARKET SOURCES")
    print("=" * 60)
    
    sources = [
        {
            "name": "Polymarket (Direct)",
            "server": "polymarket", 
            "test_call": "polymarket.get_markets",
            "description": "World's largest prediction market - crypto-based"
        },
        {
            "name": "Multi-Platform (Polymarket + Kalshi + PredictIt)",
            "server": "prediction-markets",
            "test_call": "prediction-markets.get_markets",
            "description": "Combined access to all three major platforms"
        },
        {
            "name": "Alpaca Trading",
            "server": "alpaca",
            "test_call": "alpaca.get_account_info", 
            "description": "Traditional markets execution"
        }
    ]
    
    working_sources = []
    config_path = "/Users/artbot/.openclaw/workspace/config/mcporter.json"
    
    for source in sources:
        print(f"\n📡 Testing {source['name']}...")
        print(f"   {source['description']}")
        
        try:
            cmd = ["mcporter", "--config", config_path, "call", source['test_call'], "limit=1"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"   ✅ {source['name']} - WORKING")
                working_sources.append(source)
            else:
                print(f"   ❌ {source['name']} - Failed")
                print(f"      Error: {result.stderr[:100]}...")
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {source['name']} - Timeout")
        except Exception as e:
            print(f"   ❌ {source['name']} - Exception: {e}")
    
    print(f"\n📊 SUMMARY: {len(working_sources)}/{len(sources)} sources working")
    return working_sources

def demo_enhanced_strategy():
    """Demo enhanced strategy with multiple prediction sources"""
    print("\n\n🧠 ENHANCED MULTI-SOURCE STRATEGY")
    print("=" * 60)
    
    print("🎯 Strategy: Cross-Platform Arbitrage & Confirmation")
    print("\nHow it works:")
    print("1. Monitor SAME events across multiple platforms")
    print("2. Look for probability DIFFERENCES between platforms") 
    print("3. Use CONSENSUS signals for higher confidence")
    print("4. Execute trades when multiple sources align")
    
    # Example cross-platform scenarios
    scenarios = [
        {
            "event": "Fed Rate Cut in March 2024",
            "polymarket_prob": 42.3,
            "kalshi_prob": 47.8,
            "predictit_prob": 39.1,
            "consensus": "WEAK BULLISH",
            "confidence": 0.65,
            "trades": ["VNQ (REITs)", "TLT (Bonds)", "XLU (Utilities)"],
            "reasoning": "Kalshi showing higher probability, but spread indicates uncertainty"
        },
        {
            "event": "Apple beats earnings by 5%",
            "polymarket_prob": 73.2,
            "kalshi_prob": 71.8, 
            "predictit_prob": 74.1,
            "consensus": "STRONG BULLISH",
            "confidence": 0.91,
            "trades": ["AAPL", "AAPL Call Options", "QQQ"],
            "reasoning": "All platforms showing 71-74% - strong consensus signal"
        },
        {
            "event": "Bitcoin reaches $100k by Dec 2024",
            "polymarket_prob": 28.5,
            "kalshi_prob": 31.2,
            "predictit_prob": 26.7,
            "consensus": "MODERATE BEARISH",
            "confidence": 0.43,
            "trades": ["No trade - low confidence"],
            "reasoning": "Low probability across all platforms, but rising trend"
        },
        {
            "event": "Republican House Control",
            "polymarket_prob": 68.9,
            "kalshi_prob": 72.3,
            "predictit_prob": 69.8,
            "consensus": "STRONG BULLISH",
            "confidence": 0.88,
            "trades": ["RTX (Defense)", "XLE (Energy)", "XLF (Finance)"],
            "reasoning": "All platforms 68-72% - strong Republican signal for policy trades"
        }
    ]
    
    print(f"\n📈 Analyzing {len(scenarios)} cross-platform scenarios:")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['event']}")
        print(f"   Polymarket: {scenario['polymarket_prob']:.1f}%")
        print(f"   Kalshi:     {scenario['kalshi_prob']:.1f}%") 
        print(f"   PredictIt:  {scenario['predictit_prob']:.1f}%")
        print(f"   📊 Consensus: {scenario['consensus']} (confidence: {scenario['confidence']:.0%})")
        print(f"   💰 Trades: {', '.join(scenario['trades'])}")
        print(f"   🧠 Logic: {scenario['reasoning']}")

def demo_arbitrage_opportunities():
    """Demo arbitrage opportunities between platforms"""
    print("\n\n💎 ARBITRAGE OPPORTUNITIES")
    print("=" * 60)
    
    print("🎯 Strategy: Platform Price Differences")
    print("When the SAME event has different prices on different platforms:")
    
    arbitrage_examples = [
        {
            "event": "Tesla Q4 Earnings Beat",
            "polymarket": {"price": 0.72, "volume": "$850k"},
            "kalshi": {"price": 0.68, "volume": "$420k"},
            "spread": 4.0,
            "opportunity": "MODERATE",
            "action": "Consider Tesla positions - Polymarket more bullish"
        },
        {
            "event": "Fed 0.5% Rate Cut",
            "polymarket": {"price": 0.35, "volume": "$2.1M"}, 
            "kalshi": {"price": 0.42, "volume": "$1.8M"},
            "spread": 7.0,
            "opportunity": "HIGH",
            "action": "Strong signal - Kalshi institutional money more bullish on cuts"
        },
        {
            "event": "AI Regulation Bill Passes",
            "polymarket": {"price": 0.58, "volume": "$650k"},
            "kalshi": {"price": 0.54, "volume": "$280k"}, 
            "spread": 4.0,
            "opportunity": "LOW",
            "action": "Mixed signals - wait for convergence"
        }
    ]
    
    print(f"\n📊 Current arbitrage opportunities:")
    
    for arb in arbitrage_examples:
        print(f"\n🎲 {arb['event']}")
        print(f"   Polymarket: {arb['polymarket']['price']:.0%} ({arb['polymarket']['volume']})")
        print(f"   Kalshi:     {arb['kalshi']['price']:.0%} ({arb['kalshi']['volume']})") 
        print(f"   📈 Spread: {arb['spread']:.1f} percentage points")
        print(f"   🎯 Opportunity: {arb['opportunity']}")
        print(f"   💡 Action: {arb['action']}")

def demo_enhanced_risk_management():
    """Demo enhanced risk management with multiple sources"""
    print("\n\n🛡️  ENHANCED RISK MANAGEMENT")
    print("=" * 60)
    
    print("🎯 Multi-Source Risk Controls:")
    print("• Require 2+ platforms to agree before trading")
    print("• Higher position sizes for consensus signals") 
    print("• Lower sizes for single-platform signals")
    print("• Monitor cross-platform spreads for early warnings")
    
    risk_examples = [
        {
            "signal_type": "Single Platform Signal",
            "platforms_agreeing": 1,
            "max_position": "1.0%",
            "confidence_required": "85%+", 
            "example": "Only Polymarket showing strong signal"
        },
        {
            "signal_type": "Dual Platform Consensus", 
            "platforms_agreeing": 2,
            "max_position": "1.5%",
            "confidence_required": "70%+",
            "example": "Polymarket + Kalshi agreement"
        },
        {
            "signal_type": "Triple Platform Consensus",
            "platforms_agreeing": 3, 
            "max_position": "2.0%",
            "confidence_required": "60%+",
            "example": "All three platforms aligned"
        }
    ]
    
    print(f"\n📊 Position sizing by consensus level:")
    
    for risk in risk_examples:
        print(f"\n🎯 {risk['signal_type']}")
        print(f"   Platforms: {risk['platforms_agreeing']}/3")
        print(f"   Max Position: {risk['max_position']} of account")
        print(f"   Confidence: {risk['confidence_required']}")
        print(f"   Example: {risk['example']}")

def main():
    print("🚀 ART TRADER: MULTI-PLATFORM PREDICTION MARKETS")
    print("🤖 Enhanced intelligence from Polymarket + Kalshi + PredictIt")
    print("=" * 70)
    
    # Test all sources
    working_sources = test_prediction_sources()
    
    # Demo enhanced strategies
    demo_enhanced_strategy()
    demo_arbitrage_opportunities()
    demo_enhanced_risk_management()
    
    print("\n" + "=" * 70)
    print("🎯 ENHANCED SYSTEM BENEFITS")
    print("=" * 70)
    print()
    print("📊 Multiple Data Sources:")
    print("   • Polymarket: Crypto-native, global traders")
    print("   • Kalshi: CFTC-regulated, US institutional money")
    print("   • PredictIt: Political focus, academic traders")
    print()
    print("🧠 Enhanced Intelligence:")
    print("   • Cross-platform consensus signals")
    print("   • Arbitrage opportunity detection")
    print("   • Early warning from platform divergence")
    print("   • Risk-adjusted position sizing")
    print()
    print("💰 Trading Advantages:")
    print("   • Higher confidence trades (multi-platform agreement)")
    print("   • Better timing (platform spread analysis)")
    print("   • Reduced false signals (consensus required)")
    print("   • Enhanced alpha (arbitrage opportunities)")
    print()
    print(f"✅ Ready sources: {len(working_sources)}")
    print("🚀 NEXT: Implement live multi-platform monitoring!")

if __name__ == "__main__":
    main()