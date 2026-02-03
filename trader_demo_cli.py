#!/usr/bin/env python3
"""
Art Trader Demo CLI - Using mock data

Usage:
  ./trader_demo_cli.py scan           # Scan Polymarket for new bets (mock data)
  ./trader_demo_cli.py proposals      # Show pending proposals
  ./trader_demo_cli.py trades         # Show active trades
  ./trader_demo_cli.py update         # Update all trade prices
"""

import sys
from trading_core import TradingDatabase
from trading_core_mock import MockPolymarketAnalyzer, MockAlpacaTrader


def scan_polymarket():
    """Scan Polymarket and generate proposals."""
    print("🔍 Scanning Polymarket (Demo Mode)...")
    
    db = TradingDatabase("trading_data_demo.db")
    analyzer = MockPolymarketAnalyzer()
    
    markets = analyzer.fetch_polymarket_data()
    print(f"📊 Found {len(markets)} mock markets")
    
    proposals_generated = 0
    for market in markets:
        market['finance_relevance_score'] = analyzer.assess_finance_relevance(market)
        db.store_polymarket_bet(market)
        
        if market['finance_relevance_score'] > 0.1:
            proposal = analyzer.generate_trade_proposal(market)
            if proposal:
                db.store_trade_proposal(proposal)
                proposals_generated += 1
                print(f"  💡 Generated proposal: {proposal['action'].upper()} {proposal['quantity']} {proposal['symbol']} (confidence: {proposal['confidence']:.1%})")
    
    print(f"✅ Generated {proposals_generated} trade proposals")


def show_proposals():
    """Show pending proposals."""
    print("📋 Pending Trade Proposals:")
    
    db = TradingDatabase("trading_data_demo.db")
    proposals = db.get_pending_proposals()
    
    if not proposals:
        print("  No pending proposals. Run 'scan' first.")
        return
    
    for i, prop in enumerate(proposals):
        print(f"  {i+1}. {prop['proposed_action'].upper()} {prop['proposed_quantity']} {prop['proposed_symbol']}")
        print(f"     Confidence: {prop['proposed_confidence']:.1%}")
        print(f"     Bet: {prop['title'][:60]}...")
        print()


def show_trades():
    """Show active trades."""
    print("📊 Active Trades:")
    
    db = TradingDatabase("trading_data_demo.db")
    trades = db.get_active_trades()
    
    if not trades:
        print("  No active trades. Approve some proposals first.")
        return
    
    for trade in trades:
        status = "📈" if trade.get('performance_pct', 0) > 0 else "📉"
        perf = f"{trade.get('performance_pct', 0):.1%}" if trade.get('performance_pct') else "N/A"
        
        print(f"  {status} {trade['symbol']}: {trade['action'].upper()} {trade['quantity']} shares")
        print(f"     Performance: {perf} | P&L: ${trade.get('unrealized_pnl', 0):.2f}")
        if trade.get('recommendation'):
            print(f"     💡 {trade['recommendation']}")
        print()


def update_prices():
    """Update all trade prices."""
    print("🔄 Updating trade prices (Demo Mode)...")
    
    db = TradingDatabase("trading_data_demo.db")
    trader = MockAlpacaTrader()
    trades = db.get_active_trades()
    
    if not trades:
        print("  No active trades to update.")
        return
    
    updated = 0
    for trade in trades:
        current_price = trader.get_current_price(trade['symbol'])
        if current_price and trade.get('executed_price'):
            print(f"  📊 {trade['symbol']}: ${current_price:.2f}")
            
            # Calculate performance
            if trade['action'] == 'buy':
                pnl = (current_price - trade['executed_price']) * trade['quantity']
                perf_pct = (current_price - trade['executed_price']) / trade['executed_price']
            else:
                pnl = (trade['executed_price'] - current_price) * trade['quantity']
                perf_pct = (trade['executed_price'] - current_price) / trade['executed_price']
            
            # Store performance update
            from trading_core import generate_recommendation
            recommendation = generate_recommendation(trade, current_price, perf_pct)
            
            import sqlite3
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO trade_performance 
                (trade_id, current_price, unrealized_pnl, performance_pct, recommendation)
                VALUES (?, ?, ?, ?, ?)
            ''', (trade['id'], current_price, pnl, perf_pct, recommendation))
            conn.commit()
            conn.close()
            
            updated += 1
    
    print(f"✅ Updated {updated} trades")


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
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()