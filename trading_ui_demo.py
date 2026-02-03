#!/usr/bin/env python3
"""
Art Trader UI Demo - Using mock data for demonstration

Run with: streamlit run trading_ui_demo.py
"""

import json
import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from trading_core import TradingDatabase, generate_recommendation
from trading_core_mock import MockPolymarketAnalyzer, MockAlpacaTrader


def main():
    """Main Streamlit UI."""
    st.set_page_config(
        page_title="Art Trader Dashboard (DEMO)",
        page_icon="👾",
        layout="wide"
    )
    
    st.title("👾 Art Trader Dashboard")
    st.markdown("*AI-Powered Trading with Polymarket Intelligence* **[DEMO MODE]**")
    
    # Demo mode warning
    st.warning("🧪 **Demo Mode**: Using mock data for demonstration. Real trading requires proper API connections.")
    
    # Initialize components
    db = TradingDatabase("trading_data_demo.db")  # Use separate demo DB
    analyzer = MockPolymarketAnalyzer()
    trader = MockAlpacaTrader()
    
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


def bet_discovery_page(db: TradingDatabase, analyzer: MockPolymarketAnalyzer):
    """Bet discovery and assessment page."""
    st.header("🔍 Polymarket Bet Discovery")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
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
                    st.session_state['last_scan'] = datetime.now()
                    st.rerun()
                else:
                    st.error("No markets found")
    
    with col2:
        scan_time = st.session_state.get('last_scan')
        if scan_time:
            time_ago = datetime.now() - scan_time
            if time_ago.seconds < 60:
                time_str = f"{time_ago.seconds}s ago"
            elif time_ago.seconds < 3600:
                time_str = f"{time_ago.seconds // 60}m ago"
            else:
                time_str = f"{time_ago.seconds // 3600}h ago"
            st.metric("Last Scan", time_str)
        else:
            st.metric("Last Scan", "Never")
    
    with col3:
        # Count pending proposals
        proposals = db.get_pending_proposals()
        st.metric("Pending Proposals", len(proposals))
    
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
            for idx, row in recent_bets.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{row['title']}**")
                    
                    with col2:
                        relevance_color = "green" if row['finance_relevance_score'] > 0.5 else "orange"
                        st.markdown(f"<span style='color:{relevance_color}'>⭐ {row['finance_relevance_score']:.2f}</span>", unsafe_allow_html=True)
                    
                    with col3:
                        if pd.notna(row['volume_24h']):
                            st.write(f"💰 ${row['volume_24h']:,.0f}")
                        else:
                            st.write("💰 N/A")
                    
                    with col4:
                        # Parse outcome prices and show probabilities
                        try:
                            prices = json.loads(row['outcome_prices'])
                            yes_prob = prices.get('Yes', 0.5)
                            st.write(f"📈 {yes_prob:.0%}")
                        except:
                            st.write("📈 N/A")
                    
                    st.divider()
        else:
            st.info("No finance-related bets found. Click '🔄 Scan Polymarket' to discover new opportunities.")
    
    except Exception as e:
        st.error(f"Error loading recent bets: {e}")


def pending_proposals_page(db: TradingDatabase, trader: MockAlpacaTrader):
    """Pending trade proposals approval page."""
    st.header("📋 Pending Trade Proposals")
    
    proposals = db.get_pending_proposals()
    
    if not proposals:
        st.info("No pending trade proposals. Go to 'Bet Discovery' to generate new ones.")
        return
    
    st.write(f"**{len(proposals)} proposals awaiting approval**")
    
    for i, proposal in enumerate(proposals):
        with st.expander(f"💡 Proposal {i+1}: {proposal['proposed_action'].upper()} {proposal['proposed_symbol']} - {proposal['title'][:50]}...", expanded=(i == 0)):
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown("### 📊 Polymarket Bet")
                st.write(f"**Title:** {proposal['title']}")
                
                outcome_prices = json.loads(proposal['outcome_prices'])
                if outcome_prices:
                    yes_prob = outcome_prices.get('Yes', 0)
                    no_prob = outcome_prices.get('No', 0)
                    
                    # Create probability chart
                    fig = go.Figure(data=[
                        go.Bar(x=['YES', 'NO'], y=[yes_prob, no_prob], 
                               marker_color=['green' if yes_prob > 0.5 else 'red', 'red' if yes_prob > 0.5 else 'green'])
                    ])
                    fig.update_layout(title="Market Probabilities", height=200, 
                                     yaxis_title="Probability", showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 💼 Proposed Trade")
                trade_action = proposal['proposed_action'].upper()
                action_color = "green" if trade_action == 'BUY' else "red"
                st.markdown(f"**Action:** <span style='color:{action_color}'>{trade_action}</span> {proposal['proposed_quantity']} shares of **{proposal['proposed_symbol']}**", unsafe_allow_html=True)
                
                # Confidence meter
                confidence = proposal['proposed_confidence']
                st.metric("Confidence Score", f"{confidence:.1%}")
                st.progress(confidence)
                
                st.write(f"**Expected Duration:** {proposal['expected_duration_days']} days")
                st.write(f"**Reasoning:** {proposal['reasoning']}")
            
            with col2:
                st.markdown("### ⚡ Quick Actions")
                
                col_approve, col_reject = st.columns(2)
                
                with col_approve:
                    if st.button("✅ Approve & Execute", key=f"approve_{proposal['id']}", type="primary"):
                        with st.spinner("Executing trade..."):
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
                                
                                # Store executed trade with mock executed price
                                expected_end = datetime.now() + timedelta(days=proposal['expected_duration_days'])
                                mock_price = trader.get_current_price(proposal['proposed_symbol'])
                                
                                cursor.execute('''
                                    INSERT INTO executed_trades 
                                    (proposal_id, alpaca_order_id, symbol, action, quantity, executed_price, expected_end_date)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    proposal['id'], order_id, proposal['proposed_symbol'],
                                    proposal['proposed_action'], proposal['proposed_quantity'],
                                    mock_price, expected_end.date()
                                ))
                                
                                conn.commit()
                                conn.close()
                                
                                st.success(f"✅ Trade executed! Order ID: {order_id}")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Failed to execute trade")
                
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
                        
                        st.success("❌ Proposal rejected")
                        st.rerun()
                
                st.markdown("---")
                st.markdown("### 📈 Risk Assessment")
                
                # Calculate estimated position value
                current_price = trader.get_current_price(proposal['proposed_symbol'])
                if current_price:
                    position_value = current_price * proposal['proposed_quantity']
                    st.metric("Estimated Position Value", f"${position_value:,.2f}")
                    st.metric("Current Price", f"${current_price:.2f}")
                    
                    # Risk percentage (assuming $100k portfolio)
                    risk_pct = position_value / 100000
                    st.metric("Portfolio Risk", f"{risk_pct:.1%}")


def active_trades_page(db: TradingDatabase, trader: MockAlpacaTrader):
    """Active trades monitoring and management page."""
    st.header("📊 Active Trades Portfolio")
    
    trades = db.get_active_trades()
    
    if not trades:
        st.info("🚀 No active trades yet! Approve some proposals to get started trading.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_trades = len(trades)
    total_value = sum(trade.get('quantity', 0) * trade.get('executed_price', 0) for trade in trades if trade.get('executed_price'))
    total_pnl = sum(trade.get('unrealized_pnl', 0) for trade in trades if trade.get('unrealized_pnl'))
    
    with col1:
        st.metric("Active Positions", total_trades)
    
    with col2:
        st.metric("Total Position Value", f"${total_value:,.2f}")
    
    with col3:
        pnl_color = "normal"
        if total_pnl > 0:
            pnl_color = "inverse"
        st.metric("Unrealized P&L", f"${total_pnl:,.2f}", delta=f"{total_pnl:+,.2f}")
    
    with col4:
        if st.button("🔄 Update All Prices", type="primary"):
            with st.spinner("Updating prices..."):
                update_all_prices(db, trader, trades)
                st.success("✅ All prices updated!")
                st.rerun()
    
    # Performance chart
    if trades:
        st.subheader("📈 Portfolio Performance Overview")
        
        perf_data = []
        for trade in trades:
            if trade.get('performance_pct') is not None:
                perf_data.append({
                    'Symbol': trade['symbol'],
                    'Performance': trade['performance_pct'] * 100,
                    'P&L': trade.get('unrealized_pnl', 0),
                    'Action': trade['action'].upper()
                })
        
        if perf_data:
            df = pd.DataFrame(perf_data)
            
            fig = px.bar(df, x='Symbol', y='Performance', color='Action',
                        title="Performance by Symbol", 
                        labels={'Performance': 'Performance (%)'})
            fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
    
    # Individual trades
    st.subheader("🎯 Individual Positions")
    
    for i, trade in enumerate(trades):
        perf_pct = trade.get('performance_pct', 0)
        perf_icon = "📈" if perf_pct > 0 else "📉" if perf_pct < 0 else "➖"
        
        with st.expander(f"{perf_icon} {trade['symbol']} - {trade['action'].upper()} {trade['quantity']} shares ({perf_pct:+.1%})", expanded=(i == 0)):
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown("### 📝 Trade Details")
                st.write(f"**Original Polymarket Bet:** {trade['bet_title'][:60]}...")
                st.write(f"**Executed:** {trade['executed_at']}")
                st.write(f"**Expected End:** {trade['expected_end_date']}")
                st.write(f"**Strategy Reasoning:** {trade['reasoning']}")
            
            with col2:
                st.markdown("### 💰 Financial Performance")
                
                if trade.get('executed_price'):
                    st.metric("Entry Price", f"${trade['executed_price']:.2f}")
                
                if trade.get('current_price'):
                    price_change = trade['current_price'] - trade.get('executed_price', 0)
                    st.metric("Current Price", f"${trade['current_price']:.2f}", 
                             delta=f"{price_change:+.2f}")
                    
                    if trade.get('performance_pct'):
                        perf_pct = trade['performance_pct']
                        perf_color = "green" if perf_pct > 0 else "red"
                        st.markdown(f"**Performance:** <span style='color:{perf_color}'>{perf_pct:+.1%}</span>", unsafe_allow_html=True)
                    
                    if trade.get('unrealized_pnl'):
                        pnl = trade['unrealized_pnl']
                        st.metric("Unrealized P&L", f"${pnl:,.2f}", delta=f"{pnl:+,.2f}")
            
            with col3:
                st.markdown("### ⚡ Actions")
                
                if trade.get('recommendation'):
                    rec = trade['recommendation']
                    if "Strong performance" in rec:
                        st.success(f"💡 {rec}")
                    elif "loss" in rec.lower():
                        st.error(f"⚠️ {rec}")
                    else:
                        st.info(f"💡 {rec}")
                
                if st.button("🔄 Update Price", key=f"update_{trade['id']}"):
                    with st.spinner("Updating..."):
                        update_single_trade(db, trader, trade)
                        st.success("✅ Updated!")
                        st.rerun()
                
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
                        
                        st.success("✅ Position closed!")
                        st.rerun()


def update_single_trade(db: TradingDatabase, trader: MockAlpacaTrader, trade: Dict):
    """Update a single trade's performance."""
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


def update_all_prices(db: TradingDatabase, trader: MockAlpacaTrader, trades: list):
    """Update prices for all active trades."""
    for trade in trades:
        update_single_trade(db, trader, trade)


def settings_page():
    """Settings and configuration page."""
    st.header("⚙️ Trading Settings & Configuration")
    
    st.markdown("### 🎯 Trading Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Max Position Size ($)", value=5000, min_value=100, max_value=50000, help="Maximum dollar amount per position")
        st.number_input("Risk per Trade (%)", value=2.0, min_value=0.5, max_value=10.0, help="Maximum portfolio percentage per trade")
        st.number_input("Min Confidence Score", value=0.3, min_value=0.1, max_value=1.0, help="Minimum AI confidence to generate proposals")
    
    with col2:
        st.number_input("Default Duration (days)", value=30, min_value=1, max_value=365, help="Expected holding period for trades")
        st.selectbox("Default Order Type", ["market", "limit"], help="Order execution type")
        st.checkbox("Auto-approve high confidence trades", value=False, help="Automatically execute trades above 80% confidence")
    
    st.markdown("---")
    st.markdown("### 🔍 Polymarket Discovery Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.multiselect(
            "Finance Keywords",
            ["stock", "market", "fed", "recession", "tesla", "apple", "bitcoin", "nvidia", "inflation", "earnings"],
            default=["stock", "market", "fed", "tesla", "apple"],
            help="Keywords to identify finance-related prediction markets"
        )
    
    with col2:
        st.slider("Minimum Volume (24h)", 0, 500000, 50000, help="Minimum 24h trading volume to consider a market")
        st.slider("Minimum Liquidity", 0, 100000, 10000, help="Minimum market liquidity threshold")
    
    st.markdown("---")
    st.markdown("### 🔧 Advanced Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Risk Management Mode", ["Conservative", "Moderate", "Aggressive"], index=1)
        st.number_input("Stop Loss (%)", value=10.0, min_value=1.0, max_value=50.0, help="Automatic stop loss percentage")
    
    with col2:
        st.number_input("Take Profit (%)", value=25.0, min_value=5.0, max_value=100.0, help="Automatic take profit percentage")
        st.checkbox("Enable trailing stops", value=False, help="Use trailing stop losses")
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved successfully!")
        st.balloons()


if __name__ == "__main__":
    main()