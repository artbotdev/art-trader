#!/usr/bin/env python3
"""
Art Trader CLI - Quick operations and testing

Usage:
  ./trader_cli.py scan           # Scan Polymarket for new bets
  ./trader_cli.py proposals      # Show pending proposals
  ./trader_cli.py trades         # Show active trades
  ./trader_cli.py update         # Update all trade prices
  ./trader_cli.py test-alpaca    # Test Alpaca connection
"""

import sys
import json
import subprocess
from trading_core import TradingDatabase, PolymarketAnalyzer, AlpacaTrader


def scan_polymarket():
    """Scan Polymarket and generate proposals."""
    print("🔍 Scanning Polymarket...")
    
    db = TradingDatabase()
    analyzer = PolymarketAnalyzer()
    
    markets = analyzer.fetch_polymarket_data()
    if not markets:
        print("❌ No markets found")
        return
    
    print(f"📊 Found {len(markets)} markets")
    
    proposals_generated = 0
    for market in markets:
        market['finance_relevance_score'] = analyzer.assess_finance_relevance(market)
        db.store_polymarket_bet(market)
        
        if market['finance_relevance_score'] > 0.1:
            proposal = analyzer.generate_trade_proposal(market)
            if proposal:
                db.store_trade_proposal(proposal)
                proposals_generated += 1
                print(f"  💡 Generated proposal: {proposal['action'].upper()} {proposal['symbol']}")
    
    print(f"✅ Generated {proposals_generated} trade proposals")


def show_proposals():
    """Show pending proposals."""
    print("📋 Pending Trade Proposals:")
    
    db = TradingDatabase()
    proposals = db.get_pending_proposals()
    
    if not proposals:
        print("  No pending proposals")
        return
    
    for i, prop in enumerate(proposals):
        print(f"  {i+1}. {prop['proposed_action'].upper()} {prop['proposed_quantity']} {prop['proposed_symbol']}")
        print(f"     Confidence: {prop['proposed_confidence']:.1%}")
        print(f"     Bet: {prop['title'][:60]}...")
        print()


def show_trades():
    """Show active trades."""
    print("📊 Active Trades:")
    
    db = TradingDatabase()
    trades = db.get_active_trades()
    
    if not trades:
        print("  No active trades")
        return
    
    for trade in trades:
        status = "📈" if trade.get('performance_pct', 0) > 0 else "📉"
        perf = f"{trade.get('performance_pct', 0):.1%}" if trade.get('performance_pct') else "N/A"
        
        print(f"  {status} {trade['symbol']}: {trade['action'].upper()} {trade['quantity']} shares")
        print(f"     Performance: {perf} | P&L: ${trade.get('unrealized_pnl', 0):.2f}")
        print()


def update_prices():
    """Update all trade prices."""
    print("🔄 Updating trade prices...")
    
    db = TradingDatabase()
    trader = AlpacaTrader()
    trades = db.get_active_trades()
    
    updated = 0
    for trade in trades:
        current_price = trader.get_current_price(trade['symbol'])
        if current_price and trade.get('executed_price'):
            print(f"  📊 {trade['symbol']}: ${current_price:.2f}")
            updated += 1
    
    print(f"✅ Updated {updated} trades")


def test_alpaca():
    """Test Alpaca connection."""
    print("🧪 Testing Alpaca connection...")
    
    try:
        result = subprocess.run([
            'mcporter', 'call', 'alpaca.get_account_info'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print("✅ Alpaca connection successful")
            print(f"   Account: {data.get('account_number', 'N/A')}")
            print(f"   Buying Power: ${float(data.get('buying_power', 0)):,.2f}")
            print(f"   Portfolio Value: ${float(data.get('portfolio_value', 0)):,.2f}")
        else:
            print(f"❌ Alpaca connection failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error testing Alpaca: {e}")


def main():
    """Main CLI function."""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == 'scan':
        scan_polymarket()
    elif command == 'proposals':
        show_proposals()
    elif command == 'trades':
        show_trades()
    elif command == 'update':
        update_prices()
    elif command == 'test-alpaca':
        test_alpaca()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()