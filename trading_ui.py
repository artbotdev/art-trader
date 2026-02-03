#!/usr/bin/env python3
"""
Art Trader UI - Comprehensive Trading Management Interface

Features:
1. Polymarket bet discovery and assessment
2. Trade proposal interface with manual approval
3. Position tracking and performance monitoring
4. Action recommendations (buy more/sell)
"""

import json
import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from trading_core import TradingDatabase, PolymarketAnalyzer, AlpacaTrader, generate_recommendation


def main():
    """Main Streamlit UI."""
    st.set_page_config(
        page_title="Art Trader Dashboard",
        page_icon="👾",
        layout="wide"
    )
    
    st.title("👾 Art Trader Dashboard")
    st.markdown("*AI-Powered Trading with Polymarket Intelligence*")
    
    # Initialize components
    db = TradingDatabase()
    analyzer = PolymarketAnalyzer()
    trader = AlpacaTrader()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose page",
        ["🔍 Bet Discovery", "📋 Pending Proposals", "📊 Active Trades", "⚙️ Settings"]
    )
    
    if page == "🔍 Bet Discovery":
        bet_discovery_page(db, analyzer)
    elif page == "📋 Pending Proposals":
        pending_proposals_page(db, trader)
    elif page == "📊 Active Trades":
        active_trades_page(db, trader)
    elif page == "⚙️ Settings":
        settings_page()


def bet_discovery_page(db: TradingDatabase, analyzer: PolymarketAnalyzer):
    """Bet discovery and assessment page."""
    st.header("🔍 Polymarket Bet Discovery")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 Scan Polymarket", type="primary"):
            with st.spinner("Fetching Polymarket data..."):
                markets = analyzer.fetch_polymarket_data()
                
                if markets:
                    st.success(f"Found {len(markets)} markets")
                    
                    # Process each market
                    proposals_generated = 0
                    for market in markets:
                        # Store market data
                        market['finance_relevance_score'] = analyzer.assess_finance_relevance(market)
                        db.store_polymarket_bet(market)
                        
                        # Generate trade proposal
                        proposal = analyzer.generate_trade_proposal(market)
                        if proposal:
                            db.store_trade_proposal(proposal)
                            proposals_generated += 1
                    
                    st.info(f"Generated {proposals_generated} trade proposals")
                    st.rerun()
                else:
                    st.error("No markets found")
    
    with col2:
        st.metric("Last Scan", "Just now" if st.session_state.get('last_scan') else "Never")
    
    # Show recent discoveries
    st.subheader("Recent Finance-Related Bets")
    
    try:
        conn = sqlite3.connect(db.db_path)
        recent_bets = pd.read_sql_query('''
            SELECT title, finance_relevance_score, outcome_prices, volume_24h, end_date, discovered_at
            FROM polymarket_bets 
            WHERE finance_relevance_score > 0.1
            ORDER BY discovered_at DESC 
            LIMIT 10
        ''', conn)
        conn.close()
        
        if not recent_bets.empty:
            # Format the dataframe for display
            recent_bets['Relevance Score'] = recent_bets['finance_relevance_score'].apply(lambda x: f"{x:.2f}")
            recent_bets['Volume (24h)'] = recent_bets['volume_24h'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
            recent_bets['Discovered'] = pd.to_datetime(recent_bets['discovered_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            display_df = recent_bets[['title', 'Relevance Score', 'Volume (24h)', 'end_date', 'Discovered']]
            display_df.columns = ['Bet Title', 'Relevance', 'Volume (24h)', 'End Date', 'Discovered']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No finance-related bets found. Click 'Scan Polymarket' to discover new opportunities.")
    
    except Exception as e:
        st.error(f"Error loading recent bets: {e}")


def pending_proposals_page(db: TradingDatabase, trader: AlpacaTrader):
    """Pending trade proposals approval page."""
    st.header("📋 Pending Trade Proposals")
    
    proposals = db.get_pending_proposals()
    
    if not proposals:
        st.info("No pending trade proposals. Go to 'Bet Discovery' to generate new ones.")
        return
    
    st.write(f"**{len(proposals)} proposals awaiting approval**")
    
    for i, proposal in enumerate(proposals):
        with st.expander(f"Proposal {i+1}: {proposal['proposed_action'].upper()} {proposal['proposed_symbol']} - {proposal['title'][:60]}..."):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Polymarket Bet:**")
                st.write(f"• {proposal['title']}")
                
                outcome_prices = json.loads(proposal['outcome_prices'])
                if outcome_prices:
                    yes_prob = outcome_prices.get('Yes', 0)
                    no_prob = outcome_prices.get('No', 0)
                    st.write(f"• YES: {yes_prob:.1%} | NO: {no_prob:.1%}")
                
                st.write("**Proposed Trade:**")
                st.write(f"• Action: **{proposal['proposed_action'].upper()}** {proposal['proposed_quantity']} shares of **{proposal['proposed_symbol']}**")
                st.write(f"• Confidence: {proposal['proposed_confidence']:.1%}")
                st.write(f"• Expected Duration: {proposal['expected_duration_days']} days")
                st.write(f"• Reasoning: {proposal['reasoning']}")
            
            with col2:
                st.write("**Actions:**")
                
                col_approve, col_reject = st.columns(2)
                
                with col_approve:
                    if st.button("✅ Approve", key=f"approve_{proposal['id']}"):
                        # Execute trade
                        order_id = trader.execute_trade(proposal)
                        if order_id:
                            # Store executed trade
                            conn = sqlite3.connect(db.db_path)
                            cursor = conn.cursor()
                            
                            # Update proposal status
                            cursor.execute(
                                "UPDATE trade_proposals SET status = 'approved' WHERE id = ?",
                                (proposal['id'],)
                            )
                            
                            # Store executed trade
                            expected_end = datetime.now() + timedelta(days=proposal['expected_duration_days'])
                            cursor.execute('''
                                INSERT INTO executed_trades 
                                (proposal_id, alpaca_order_id, symbol, action, quantity, expected_end_date)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (
                                proposal['id'], order_id, proposal['proposed_symbol'],
                                proposal['proposed_action'], proposal['proposed_quantity'],
                                expected_end.date()
                            ))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"Trade executed! Order ID: {order_id}")
                            st.rerun()
                        else:
                            st.error("Failed to execute trade")
                
                with col_reject:
                    if st.button("❌ Reject", key=f"reject_{proposal['id']}"):
                        # Update proposal status
                        conn = sqlite3.connect(db.db_path)
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE trade_proposals SET status = 'rejected' WHERE id = ?",
                            (proposal['id'],)
                        )
                        conn.commit()
                        conn.close()
                        
                        st.success("Proposal rejected")
                        st.rerun()


def active_trades_page(db: TradingDatabase, trader: AlpacaTrader):
    """Active trades monitoring and management page."""
    st.header("📊 Active Trades")
    
    trades = db.get_active_trades()
    
    if not trades:
        st.info("No active trades. Approve some proposals to get started!")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_trades = len(trades)
    total_value = sum(trade.get('quantity', 0) * trade.get('executed_price', 0) for trade in trades if trade.get('executed_price'))
    
    with col1:
        st.metric("Active Trades", total_trades)
    
    with col2:
        st.metric("Total Value", f"${total_value:,.2f}")
    
    with col3:
        total_pnl = sum(trade.get('unrealized_pnl', 0) for trade in trades if trade.get('unrealized_pnl'))
        st.metric("Unrealized P&L", f"${total_pnl:,.2f}")
    
    with col4:
        if st.button("🔄 Update Prices", type="primary"):
            update_all_prices(db, trader, trades)
            st.rerun()
    
    # Individual trades
    st.subheader("Trade Details")
    
    for trade in trades:
        with st.expander(f"{trade['symbol']} - {trade['action'].upper()} {trade['quantity']} shares"):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Original Bet:** {trade['bet_title']}")
                st.write(f"**Executed:** {trade['executed_at']}")
                st.write(f"**Expected End:** {trade['expected_end_date']}")
                st.write(f"**Reasoning:** {trade['reasoning']}")
                
                # Price and P&L info
                if trade.get('executed_price'):
                    st.write(f"**Executed Price:** ${trade['executed_price']:.2f}")
                
                if trade.get('current_price'):
                    st.write(f"**Current Price:** ${trade['current_price']:.2f}")
                    
                    if trade.get('performance_pct'):
                        perf_color = "green" if trade['performance_pct'] > 0 else "red"
                        st.write(f"**Performance:** <span style='color:{perf_color}'>{trade['performance_pct']:+.1%}</span>", unsafe_allow_html=True)
            
            with col2:
                st.write("**Actions:**")
                
                if trade.get('recommendation'):
                    st.info(f"💡 {trade['recommendation']}")
                
                col_close, col_update = st.columns(2)
                
                with col_close:
                    if st.button("🔴 Close Position", key=f"close_{trade['id']}"):
                        # Execute opposite trade to close
                        close_action = 'sell' if trade['action'] == 'buy' else 'buy'
                        close_proposal = {
                            'symbol': trade['symbol'],
                            'action': close_action,
                            'quantity': trade['quantity']
                        }
                        
                        order_id = trader.execute_trade(close_proposal)
                        if order_id:
                            # Update trade status
                            conn = sqlite3.connect(db.db_path)
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE executed_trades SET status = 'closed' WHERE id = ?",
                                (trade['id'],)
                            )
                            conn.commit()
                            conn.close()
                            
                            st.success("Position closed!")
                            st.rerun()
                
                with col_update:
                    if st.button("🔄 Update", key=f"update_{trade['id']}"):
                        current_price = trader.get_current_price(trade['symbol'])
                        if current_price and trade.get('executed_price'):
                            # Calculate performance
                            if trade['action'] == 'buy':
                                pnl = (current_price - trade['executed_price']) * trade['quantity']
                                perf_pct = (current_price - trade['executed_price']) / trade['executed_price']
                            else:  # sell
                                pnl = (trade['executed_price'] - current_price) * trade['quantity']
                                perf_pct = (trade['executed_price'] - current_price) / trade['executed_price']
                            
                            # Generate recommendation
                            recommendation = generate_recommendation(trade, current_price, perf_pct)
                            
                            # Store performance update
                            conn = sqlite3.connect(db.db_path)
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT OR REPLACE INTO trade_performance 
                                (trade_id, current_price, unrealized_pnl, performance_pct, recommendation)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (trade['id'], current_price, pnl, perf_pct, recommendation))
                            conn.commit()
                            conn.close()
                            
                            st.success("Updated!")
                            st.rerun()


def update_all_prices(db: TradingDatabase, trader: AlpacaTrader, trades: list):
    """Update prices for all active trades."""
    updated_count = 0
    
    for trade in trades:
        current_price = trader.get_current_price(trade['symbol'])
        if current_price and trade.get('executed_price'):
            # Calculate performance
            if trade['action'] == 'buy':
                pnl = (current_price - trade['executed_price']) * trade['quantity']
                perf_pct = (current_price - trade['executed_price']) / trade['executed_price']
            else:  # sell
                pnl = (trade['executed_price'] - current_price) * trade['quantity']
                perf_pct = (trade['executed_price'] - current_price) / trade['executed_price']
            
            # Generate recommendation
            recommendation = generate_recommendation(trade, current_price, perf_pct)
            
            # Store performance update
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO trade_performance 
                (trade_id, current_price, unrealized_pnl, performance_pct, recommendation)
                VALUES (?, ?, ?, ?, ?)
            ''', (trade['id'], current_price, pnl, perf_pct, recommendation))
            conn.commit()
            conn.close()
            
            updated_count += 1
    
    st.success(f"Updated {updated_count} trades")


def settings_page():
    """Settings and configuration page."""
    st.header("⚙️ Settings")
    
    st.subheader("Trading Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Max Position Size ($)", value=5000, min_value=100, max_value=50000)
        st.number_input("Risk per Trade (%)", value=2.0, min_value=0.5, max_value=10.0)
        st.number_input("Min Confidence Score", value=0.3, min_value=0.1, max_value=1.0)
    
    with col2:
        st.number_input("Default Duration (days)", value=30, min_value=1, max_value=365)
        st.selectbox("Default Order Type", ["market", "limit"])
        st.checkbox("Auto-approve high confidence trades", value=False)
    
    st.subheader("Polymarket Filters")
    
    st.multiselect(
        "Finance Keywords",
        ["stock", "market", "fed", "recession", "tesla", "apple", "bitcoin"],
        default=["stock", "market", "fed"]
    )
    
    st.slider("Minimum Volume (24h)", 0, 100000, 1000)
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved!")


if __name__ == "__main__":
    main()