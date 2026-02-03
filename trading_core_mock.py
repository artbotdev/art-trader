#!/usr/bin/env python3
"""
Art Trader Core - Mock version for UI testing
"""

import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random


# Import the real database class
from trading_core import TradingDatabase, generate_recommendation


class MockPolymarketAnalyzer:
    """Mock analyzer with sample data for testing."""
    
    def __init__(self):
        self.finance_keywords = [
            'stock', 'market', 'nasdaq', 'sp500', 's&p', 'dow', 'fed', 'interest rate',
            'inflation', 'recession', 'gdp', 'earnings', 'tesla', 'apple', 'microsoft',
            'nvidia', 'bitcoin', 'crypto', 'oil', 'gold', 'treasury', 'bond',
            'unemployment', 'economy', 'financial', 'bank', 'dollar', 'euro'
        ]
    
    def fetch_polymarket_data(self) -> List[Dict]:
        """Return mock market data for testing."""
        return [
            {
                "id": "tsla_q4_2024_delivery",
                "title": "Tesla Q4 2024 deliveries will exceed 500,000 vehicles",
                "description": "Will Tesla deliver more than 500,000 vehicles in Q4 2024?",
                "outcome_prices": {"Yes": 0.75, "No": 0.25},
                "volume_24h": 125000,
                "end_date": "2024-12-31",
                "category": "Technology"
            },
            {
                "id": "fed_rate_cut_march",
                "title": "Federal Reserve will cut rates by 0.25% in March 2024",
                "description": "Will the Fed cut interest rates by at least 25 basis points in March?",
                "outcome_prices": {"Yes": 0.35, "No": 0.65},
                "volume_24h": 89000,
                "end_date": "2024-03-20",
                "category": "Economics"
            },
            {
                "id": "sp500_4800_year_end",
                "title": "S&P 500 will close above 4800 by year end",
                "description": "Will the S&P 500 index close above 4800 on the last trading day of 2024?",
                "outcome_prices": {"Yes": 0.68, "No": 0.32},
                "volume_24h": 156000,
                "end_date": "2024-12-31",
                "category": "Finance"
            },
            {
                "id": "nvidia_earnings_beat",
                "title": "NVIDIA Q4 earnings will beat analyst estimates",
                "description": "Will NVIDIA beat consensus EPS estimates for Q4 2024?",
                "outcome_prices": {"Yes": 0.82, "No": 0.18},
                "volume_24h": 203000,
                "end_date": "2024-02-15",
                "category": "Technology"
            },
            {
                "id": "bitcoin_60k_march",
                "title": "Bitcoin will reach $60,000 by March 2024",
                "description": "Will Bitcoin (BTC) reach or exceed $60,000 USD by March 31, 2024?",
                "outcome_prices": {"Yes": 0.42, "No": 0.58},
                "volume_24h": 312000,
                "end_date": "2024-03-31",
                "category": "Crypto"
            },
            {
                "id": "apple_vision_pro_sales",
                "title": "Apple Vision Pro will sell 1M units in 2024",
                "description": "Will Apple sell at least 1 million Vision Pro units in 2024?",
                "outcome_prices": {"Yes": 0.29, "No": 0.71},
                "volume_24h": 78000,
                "end_date": "2024-12-31",
                "category": "Technology"
            }
        ]
    
    def assess_finance_relevance(self, market_data: Dict) -> float:
        """Score market relevance to finance/stocks (0-1)."""
        text = f"{market_data.get('title', '')} {market_data.get('description', '')}".lower()
        
        score = 0
        for keyword in self.finance_keywords:
            if keyword in text:
                score += 1
        
        # Normalize score
        max_possible = len(self.finance_keywords)
        return min(score / max_possible * 3, 1.0)
    
    def generate_trade_proposal(self, market_data: Dict) -> Optional[Dict]:
        """Generate trade proposal based on mock market data."""
        relevance = self.assess_finance_relevance(market_data)
        
        if relevance < 0.1:
            return None
        
        title = market_data.get('title', '').lower()
        outcome_prices = market_data.get('outcome_prices', {})
        
        proposal = {
            'polymarket_bet_id': market_data['id'],
            'confidence': relevance,
            'duration_days': 30,
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
        elif 'fed' in title or 'federal' in title:
            proposal['symbol'] = 'TLT'  # Treasury ETF
        else:
            proposal['symbol'] = 'SPY'
        
        # Determine action based on probability
        yes_prob = float(outcome_prices.get('Yes', 0.5))
        
        if yes_prob > 0.6:
            proposal['action'] = 'buy'
            proposal['quantity'] = int(500 * relevance)
            proposal['reasoning'] += f" | High YES probability ({yes_prob:.1%}) suggests bullish sentiment"
        elif yes_prob < 0.4:
            proposal['action'] = 'sell'
            proposal['quantity'] = int(500 * relevance)
            proposal['reasoning'] += f" | Low YES probability ({yes_prob:.1%}) suggests bearish sentiment"
        else:
            return None
        
        return proposal


class MockAlpacaTrader:
    """Mock trader for testing."""
    
    def execute_trade(self, proposal: Dict) -> Optional[str]:
        """Simulate trade execution."""
        # Simulate some processing time
        time.sleep(0.5)
        
        # Return a mock order ID
        return f"mock_order_{random.randint(10000, 99999)}"
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Return mock prices for testing."""
        mock_prices = {
            'TSLA': 245.67,
            'AAPL': 178.34,
            'NVDA': 598.23,
            'MSFT': 421.89,
            'SPY': 478.12,
            'QQQ': 389.45,
            'BTC/USD': 43267.89,
            'TLT': 98.76
        }
        
        base_price = mock_prices.get(symbol, 100.0)
        # Add some random variation (+/- 2%)
        variation = random.uniform(-0.02, 0.02)
        return base_price * (1 + variation)