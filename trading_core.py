#!/usr/bin/env python3
"""
Art Trader Core - Shared components without UI dependencies
"""

import json
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class TradingDatabase:
    """Manages persistent storage of trades and positions."""
    
    def __init__(self, db_path="trading_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Polymarket bets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polymarket_bets (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                outcome_prices TEXT,
                volume_24h REAL,
                end_date TEXT,
                category TEXT,
                finance_relevance_score REAL,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trade proposals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                polymarket_bet_id TEXT,
                proposed_symbol TEXT,
                proposed_action TEXT,
                proposed_quantity REAL,
                proposed_confidence REAL,
                expected_duration_days INTEGER,
                reasoning TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (polymarket_bet_id) REFERENCES polymarket_bets (id)
            )
        ''')
        
        # Executed trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS executed_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id INTEGER,
                alpaca_order_id TEXT,
                symbol TEXT,
                action TEXT,
                quantity REAL,
                executed_price REAL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expected_end_date DATE,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (proposal_id) REFERENCES trade_proposals (id)
            )
        ''')
        
        # Performance tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                current_price REAL,
                unrealized_pnl REAL,
                realized_pnl REAL,
                performance_pct REAL,
                recommendation TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_id) REFERENCES executed_trades (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_polymarket_bet(self, bet_data: Dict) -> None:
        """Store discovered Polymarket bet."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO polymarket_bets 
            (id, title, description, outcome_prices, volume_24h, end_date, category, finance_relevance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bet_data['id'],
            bet_data['title'],
            bet_data.get('description', ''),
            json.dumps(bet_data.get('outcome_prices', {})),
            bet_data.get('volume_24h', 0),
            bet_data.get('end_date', ''),
            bet_data.get('category', ''),
            bet_data.get('finance_relevance_score', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def store_trade_proposal(self, proposal: Dict) -> int:
        """Store trade proposal and return its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trade_proposals 
            (polymarket_bet_id, proposed_symbol, proposed_action, proposed_quantity, 
             proposed_confidence, expected_duration_days, reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            proposal['polymarket_bet_id'],
            proposal['symbol'],
            proposal['action'],
            proposal['quantity'],
            proposal['confidence'],
            proposal['duration_days'],
            proposal['reasoning']
        ))
        
        proposal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return proposal_id
    
    def get_pending_proposals(self) -> List[Dict]:
        """Get all pending trade proposals."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tp.*, pb.title, pb.outcome_prices, pb.end_date
            FROM trade_proposals tp
            JOIN polymarket_bets pb ON tp.polymarket_bet_id = pb.id
            WHERE tp.status = 'pending'
            ORDER BY tp.created_at DESC
        ''')
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_active_trades(self) -> List[Dict]:
        """Get all active trades with performance data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT et.*, tp.reasoning, pb.title as bet_title, 
                   tperf.current_price, tperf.unrealized_pnl, tperf.performance_pct,
                   tperf.recommendation, tperf.updated_at as last_update
            FROM executed_trades et
            JOIN trade_proposals tp ON et.proposal_id = tp.id
            JOIN polymarket_bets pb ON tp.polymarket_bet_id = pb.id
            LEFT JOIN trade_performance tperf ON et.id = tperf.trade_id
            WHERE et.status = 'active'
            ORDER BY et.executed_at DESC
        ''')
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results


class PolymarketAnalyzer:
    """Analyzes Polymarket data for trading opportunities."""
    
    def __init__(self):
        self.finance_keywords = [
            'stock', 'market', 'nasdaq', 'sp500', 's&p', 'dow', 'fed', 'interest rate',
            'inflation', 'recession', 'gdp', 'earnings', 'tesla', 'apple', 'microsoft',
            'nvidia', 'bitcoin', 'crypto', 'oil', 'gold', 'treasury', 'bond',
            'unemployment', 'economy', 'financial', 'bank', 'dollar', 'euro'
        ]
    
    def fetch_polymarket_data(self) -> List[Dict]:
        """Fetch current markets from Polymarket via MCP."""
        try:
            result = subprocess.run([
                'mcporter', 'call', 'polymarket.get_markets',
                'limit=50', 'active=true'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('markets', [])
            else:
                print(f"Failed to fetch Polymarket data: {result.stderr}")
                return []
        except Exception as e:
            print(f"Error fetching Polymarket data: {e}")
            return []
    
    def assess_finance_relevance(self, market_data: Dict) -> float:
        """Score market relevance to finance/stocks (0-1)."""
        text = f"{market_data.get('title', '')} {market_data.get('description', '')}".lower()
        
        score = 0
        for keyword in self.finance_keywords:
            if keyword in text:
                score += 1
        
        # Normalize score
        max_possible = len(self.finance_keywords)
        return min(score / max_possible * 3, 1.0)  # Cap at 1.0, boost relevance
    
    def generate_trade_proposal(self, market_data: Dict) -> Optional[Dict]:
        """Generate trade proposal based on Polymarket data."""
        relevance = self.assess_finance_relevance(market_data)
        
        if relevance < 0.1:  # Not finance-related enough
            return None
        
        # Simple heuristic-based trade proposal
        title = market_data.get('title', '').lower()
        outcome_prices = market_data.get('outcome_prices', {})
        
        proposal = {
            'polymarket_bet_id': market_data['id'],
            'confidence': relevance,
            'duration_days': 30,  # Default 30 days
            'reasoning': f"Finance relevance score: {relevance:.2f}"
        }
        
        # Determine stock symbol and action based on title
        if 'tesla' in title or 'tsla' in title:
            proposal['symbol'] = 'TSLA'
        elif 'apple' in title or 'aapl' in title:
            proposal['symbol'] = 'AAPL'
        elif 'nvidia' in title or 'nvda' in title:
            proposal['symbol'] = 'NVDA'
        elif 'microsoft' in title or 'msft' in title:
            proposal['symbol'] = 'MSFT'
        elif 'sp500' in title or 's&p' in title:
            proposal['symbol'] = 'SPY'
        elif 'nasdaq' in title:
            proposal['symbol'] = 'QQQ'
        elif 'bitcoin' in title or 'btc' in title:
            proposal['symbol'] = 'BTC/USD'
        else:
            proposal['symbol'] = 'SPY'  # Default to S&P 500
        
        # Determine action based on probability
        yes_prob = float(outcome_prices.get('Yes', 0.5))
        
        if yes_prob > 0.6:
            proposal['action'] = 'buy'
            proposal['quantity'] = int(1000 * relevance)  # Scale quantity by confidence
            proposal['reasoning'] += f" | High YES probability ({yes_prob:.1%}) suggests bullish sentiment"
        elif yes_prob < 0.4:
            proposal['action'] = 'sell'
            proposal['quantity'] = int(1000 * relevance)
            proposal['reasoning'] += f" | Low YES probability ({yes_prob:.1%}) suggests bearish sentiment"
        else:
            return None  # Too uncertain
        
        return proposal


class AlpacaTrader:
    """Executes trades via Alpaca using MCP."""
    
    def execute_trade(self, proposal: Dict) -> Optional[str]:
        """Execute trade proposal via Alpaca MCP."""
        try:
            symbol = proposal['symbol']
            action = proposal['action']  # 'buy' or 'sell'
            quantity = proposal['quantity']
            
            # Execute via MCP
            result = subprocess.run([
                'mcporter', 'call', 'alpaca.place_stock_order',
                f'symbol={symbol}',
                f'side={action}',
                f'quantity={quantity}',
                'order_type=market'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('order_id')
            else:
                print(f"Failed to execute trade: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error executing trade: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol."""
        try:
            result = subprocess.run([
                'mcporter', 'call', 'alpaca.get_stock_latest_quote',
                f'symbol_or_symbols={symbol}'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                quotes = data.get('quotes', {})
                quote = quotes.get(symbol, {})
                return float(quote.get('bid_price', 0))
            return None
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None


def generate_recommendation(trade: Dict, current_price: float, perf_pct: float) -> str:
    """Generate trading recommendation based on performance."""
    if perf_pct > 0.1:  # 10%+ gain
        return "🎯 Strong performance! Consider taking profits."
    elif perf_pct > 0.05:  # 5-10% gain
        return "📈 Good performance. Hold or take partial profits."
    elif perf_pct > -0.05:  # -5% to +5%
        return "➖ Neutral performance. Monitor closely."
    elif perf_pct > -0.1:  # -5% to -10% loss
        return "⚠️ Small loss. Consider stop-loss or averaging down."
    else:  # 10%+ loss
        return "🚨 Significant loss! Review and consider exiting."