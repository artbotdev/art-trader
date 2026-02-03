#!/usr/bin/env python3
"""
Alpaca Trading Integration for AI Research-Driven Trading
Connects research insights to automated trade execution
"""

import os
import requests
import json
from datetime import datetime, timedelta
import pandas as pd

class AlpacaTrader:
    def __init__(self, api_key=None, secret_key=None, paper_trading=True):
        """Initialize Alpaca API connection"""
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        
        # Use paper trading by default for safety
        if paper_trading:
            self.base_url = "https://paper-api.alpaca.markets"
        else:
            self.base_url = "https://api.alpaca.markets"
        
        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key,
            'Content-Type': 'application/json'
        }
        
        # Validate connection
        self.validate_connection()
    
    def validate_connection(self):
        """Test API connection and get account info"""
        try:
            response = requests.get(f"{self.base_url}/v2/account", headers=self.headers)
            if response.status_code == 200:
                account = response.json()
                print(f"✅ Connected to Alpaca (Paper: {'paper-api' in self.base_url})")
                print(f"💰 Buying Power: ${float(account['buying_power']):,.2f}")
                print(f"📊 Portfolio Value: ${float(account['portfolio_value']):,.2f}")
                return True
            else:
                print(f"❌ Connection failed: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_positions(self):
        """Get current positions"""
        response = requests.get(f"{self.base_url}/v2/positions", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_market_data(self, symbol, timeframe="1Day", limit=100):
        """Get market data for analysis"""
        params = {
            'symbols': symbol,
            'timeframe': timeframe,
            'limit': limit
        }
        response = requests.get(
            f"{self.base_url}/v2/stocks/{symbol}/bars",
            headers=self.headers,
            params=params
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def place_order(self, symbol, qty, side, order_type='market', time_in_force='day', 
                   limit_price=None, stop_price=None, trail_percent=None):
        """
        Place a trade order
        
        Args:
            symbol: Stock symbol (e.g., 'QQQ', 'NVDA')
            qty: Quantity to trade
            side: 'buy' or 'sell'
            order_type: 'market', 'limit', 'stop', 'stop_limit', 'trailing_stop'
            time_in_force: 'day', 'gtc', 'ioc', 'fok'
            limit_price: For limit orders
            stop_price: For stop orders
            trail_percent: For trailing stop orders
        """
        order_data = {
            'symbol': symbol,
            'qty': str(qty),
            'side': side,
            'type': order_type,
            'time_in_force': time_in_force
        }
        
        # Add conditional parameters
        if limit_price:
            order_data['limit_price'] = str(limit_price)
        if stop_price:
            order_data['stop_price'] = str(stop_price)
        if trail_percent:
            order_data['trail_percent'] = str(trail_percent)
        
        response = requests.post(
            f"{self.base_url}/v2/orders",
            headers=self.headers,
            json=order_data
        )
        
        if response.status_code == 201:
            order = response.json()
            print(f"✅ Order placed: {side.upper()} {qty} {symbol} ({order_type})")
            print(f"📋 Order ID: {order['id']}")
            return order
        else:
            print(f"❌ Order failed: {response.status_code}")
            print(response.text)
            return None
    
    def ai_sector_momentum_trade(self, signal_strength, catalyst_type):
        """
        Execute AI sector trade based on research insights
        
        Args:
            signal_strength: 1-10 (confidence level)
            catalyst_type: 'earnings', 'product_launch', 'regulation', 'breakthrough'
        """
        # Define position sizing based on signal strength
        account_response = requests.get(f"{self.base_url}/v2/account", headers=self.headers)
        if account_response.status_code != 200:
            return None
        
        account = account_response.json()
        buying_power = float(account['buying_power'])
        
        # Risk management: max 2% of portfolio per trade
        max_risk = buying_power * 0.02
        
        # Select instrument based on catalyst type
        if catalyst_type in ['earnings', 'product_launch']:
            symbol = 'QQQ'  # Tech-heavy for specific company news
        elif catalyst_type == 'breakthrough':
            symbol = 'XLK'  # Broader tech sector
        elif catalyst_type == 'regulation':
            symbol = 'SOXX'  # Semiconductor focus
        else:
            symbol = 'QQQ'  # Default
        
        # Get current price
        price_data = self.get_market_data(symbol, "1Min", 1)
        if not price_data or 'bars' not in price_data:
            print(f"❌ Could not get price data for {symbol}")
            return None
        
        current_price = float(price_data['bars'][symbol][0]['c'])  # Close price
        
        # Calculate position size (2% risk rule)
        qty = int(max_risk / current_price)
        if qty < 1:
            print(f"❌ Position too small: {max_risk} / {current_price} = {qty}")
            return None
        
        # Determine order type based on signal strength
        if signal_strength >= 8:
            # High conviction: market order
            order = self.place_order(symbol, qty, 'buy', 'market')
        elif signal_strength >= 6:
            # Medium conviction: limit order at slight discount
            limit_price = current_price * 0.999  # 0.1% below current
            order = self.place_order(symbol, qty, 'buy', 'limit', limit_price=limit_price)
        else:
            print(f"❌ Signal strength too low: {signal_strength}")
            return None
        
        # Set stop loss at 5% below entry
        if order:
            stop_price = current_price * 0.95
            stop_order = self.place_order(
                symbol, qty, 'sell', 'stop', 
                stop_price=stop_price, time_in_force='gtc'
            )
            
            return {
                'entry_order': order,
                'stop_order': stop_order,
                'symbol': symbol,
                'qty': qty,
                'entry_price': current_price,
                'stop_price': stop_price,
                'catalyst_type': catalyst_type,
                'signal_strength': signal_strength,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def earnings_play_setup(self, symbol, earnings_date, bullish=True, confidence=7):
        """
        Set up earnings play based on research insights
        
        Args:
            symbol: Company symbol (e.g., 'NVDA')
            earnings_date: Date of earnings (YYYY-MM-DD)
            bullish: True for calls/long, False for puts/short
            confidence: 1-10 confidence level
        """
        print(f"🎯 Setting up earnings play for {symbol}")
        print(f"📅 Earnings: {earnings_date}")
        print(f"📈 Direction: {'Bullish' if bullish else 'Bearish'}")
        print(f"🎲 Confidence: {confidence}/10")
        
        # Note: Alpaca doesn't support options directly
        # For now, we'll do stock plays and suggest options alternatives
        
        account_response = requests.get(f"{self.base_url}/v2/account", headers=self.headers)
        if account_response.status_code != 200:
            return None
        
        account = account_response.json()
        buying_power = float(account['buying_power'])
        max_risk = buying_power * 0.02  # 2% rule
        
        # Get current price
        price_data = self.get_market_data(symbol, "1Min", 1)
        if not price_data or 'bars' not in price_data:
            print(f"❌ Could not get price data for {symbol}")
            return None
        
        current_price = float(price_data['bars'][symbol][0]['c'])
        qty = int(max_risk / current_price)
        
        if qty < 1:
            print(f"❌ Position too small for {symbol} at ${current_price}")
            return None
        
        side = 'buy' if bullish else 'sell'
        order = self.place_order(symbol, qty, side, 'market')
        
        if order:
            print(f"💡 Alternative: Consider {symbol} options for leveraged earnings play")
            print(f"💡 Strategy: {'Call options' if bullish else 'Put options'} expiring post-earnings")
        
        return order


# Trading strategies based on research insights
def execute_research_driven_trade(trader, insight_type, details):
    """
    Execute trades based on research insights from morning briefing
    
    Args:
        trader: AlpacaTrader instance
        insight_type: 'ai_breakthrough', 'earnings_preview', 'sector_rotation', 'regulation_impact'
        details: Dictionary with specific trade parameters
    """
    
    if insight_type == 'ai_breakthrough':
        # Example: OpenAI releases GPT-5, bullish for AI sector
        return trader.ai_sector_momentum_trade(
            signal_strength=details.get('confidence', 7),
            catalyst_type='breakthrough'
        )
    
    elif insight_type == 'earnings_preview':
        # Example: NVDA earnings next week, expect beat based on AI demand
        return trader.earnings_play_setup(
            symbol=details['symbol'],
            earnings_date=details['date'],
            bullish=details.get('bullish', True),
            confidence=details.get('confidence', 7)
        )
    
    elif insight_type == 'sector_rotation':
        # Example: Rotation from growth to value, short tech ETFs
        return trader.ai_sector_momentum_trade(
            signal_strength=details.get('confidence', 6),
            catalyst_type='regulation'
        )
    
    else:
        print(f"❌ Unknown insight type: {insight_type}")
        return None


if __name__ == "__main__":
    # Example usage
    print("🚀 Initializing Alpaca AI Trader")
    
    # Initialize trader (paper trading by default)
    trader = AlpacaTrader(paper_trading=True)
    
    # Example: Execute trade based on AI breakthrough insight
    example_trade = execute_research_driven_trade(
        trader,
        'ai_breakthrough',
        {
            'confidence': 8,
            'catalyst': 'OpenAI GPT-5 announcement',
            'expected_impact': 'Bullish for AI sector'
        }
    )
    
    if example_trade:
        print("✅ Trade executed successfully!")
        print(f"📊 Trade details: {json.dumps(example_trade, indent=2)}")
    else:
        print("❌ Trade execution failed")