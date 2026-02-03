#!/usr/bin/env python3
"""
Art Trader: Prediction Markets to Alpaca Trading System
Monitors Polymarket, generates signals, executes trades on Alpaca
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from polymarket_alpaca_mapper import PolymarketAlpacaMapper, PredictionSignal, AlpacaTrade

class PredictionTrader:
    def __init__(self, max_position_size_pct: float = 2.0, max_daily_trades: int = 10):
        self.mapper = PolymarketAlpacaMapper()
        self.max_position_size_pct = max_position_size_pct  # Max 2% of account per trade
        self.max_daily_trades = max_daily_trades
        self.daily_trade_count = 0
        self.trade_log = []
        
    def get_polymarket_data(self) -> List[Dict]:
        """Fetch active markets from Polymarket via mcporter"""
        try:
            cmd = ["mcporter", "call", "polymarket.get_markets", "active=true", "order=volume", "limit=50"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse the output (assuming JSON format)
                return json.loads(result.stdout)
            else:
                print(f"Error fetching Polymarket data: {result.stderr}")
                return []
        except subprocess.TimeoutExpired:
            print("Timeout fetching Polymarket data")
            return []
        except Exception as e:
            print(f"Exception fetching Polymarket data: {e}")
            return []
            
    def get_alpaca_account_info(self) -> Dict:
        """Get current Alpaca account information"""
        try:
            cmd = ["mcporter", "call", "alpaca.get_account_info"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse account info from text output
                lines = result.stdout.strip().split('\\n')
                account_info = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        account_info[key.strip()] = value.strip()
                return account_info
            else:
                print(f"Error fetching account info: {result.stderr}")
                return {}
        except Exception as e:
            print(f"Exception fetching account info: {e}")
            return {}

    def parse_polymarket_response(self, raw_data: List[Dict]) -> List[PredictionSignal]:
        """Parse Polymarket API response into PredictionSignal objects"""
        signals = []
        
        for market in raw_data:
            try:
                # Extract relevant fields (adjust based on actual API response)
                signal = PredictionSignal(
                    market_id=market.get('id', ''),
                    title=market.get('title', ''),
                    description=market.get('description', ''),
                    current_prob=float(market.get('probability', 0)) * 100,
                    prob_change=float(market.get('prob_change_24h', 0)) * 100,
                    volume_24h=float(market.get('volume_24h', 0)),
                    liquidity=float(market.get('liquidity', 0)),
                    end_date=datetime.fromisoformat(market.get('end_date', datetime.now().isoformat())),
                    category=self.mapper.categorize_prediction(
                        market.get('title', ''), 
                        market.get('description', '')
                    )
                )
                signals.append(signal)
            except Exception as e:
                print(f"Error parsing market data: {e}")
                continue
                
        return signals

    def calculate_position_size(self, trade: AlpacaTrade, account_balance: float) -> int:
        """Calculate appropriate position size based on risk management"""
        # Get current stock price (simplified - in reality would call Alpaca)
        base_price = 100  # Placeholder - would get from Alpaca API
        
        # Calculate max dollar amount for this trade
        max_dollar_amount = account_balance * (self.max_position_size_pct / 100)
        
        # Adjust for confidence level
        confidence_adjusted_amount = max_dollar_amount * trade.confidence
        
        # Calculate shares
        max_shares = int(confidence_adjusted_amount / base_price)
        
        # Don't exceed the trade's recommended quantity
        return min(max_shares, trade.quantity)

    def execute_alpaca_trade(self, trade: AlpacaTrade, position_size: int) -> bool:
        """Execute a trade on Alpaca via mcporter"""
        if self.daily_trade_count >= self.max_daily_trades:
            print(f"Daily trade limit reached ({self.max_daily_trades})")
            return False
            
        try:
            # For now, only handle stock trades (options require more complex formatting)
            if trade.order_type != "market" or "_CALL" in trade.symbol or "_PUT" in trade.symbol:
                print(f"Skipping complex order type: {trade.symbol} {trade.order_type}")
                return False
                
            cmd = [
                "mcporter", "call", "alpaca.place_stock_order",
                f"symbol={trade.symbol}",
                f"side={trade.action}",
                f"quantity={position_size}",
                f"order_type={trade.order_type}"
            ]
            
            print(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Trade executed: {trade.action} {position_size} {trade.symbol}")
                self.daily_trade_count += 1
                
                # Log the trade
                trade_record = {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": trade.symbol,
                    "action": trade.action,
                    "quantity": position_size,
                    "confidence": trade.confidence,
                    "reasoning": trade.reasoning,
                    "alpaca_response": result.stdout
                }
                self.trade_log.append(trade_record)
                return True
            else:
                print(f"❌ Trade failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Exception executing trade: {e}")
            return False

    def run_trading_cycle(self):
        """Main trading cycle - fetch data, analyze, trade"""
        print(f"\n🚀 Starting trading cycle at {datetime.now()}")
        
        # 1. Get Polymarket data
        print("📊 Fetching Polymarket data...")
        raw_markets = self.get_polymarket_data()
        if not raw_markets:
            print("❌ No Polymarket data available")
            return
            
        # 2. Parse into signals
        signals = self.parse_polymarket_response(raw_markets)
        print(f"📈 Found {len(signals)} prediction signals")
        
        # 3. Generate trades
        print("🧠 Analyzing signals and generating trades...")
        report = self.mapper.generate_trading_report(signals)
        trades = report.get('trades', [])
        
        if not trades:
            print("💤 No actionable trades generated")
            return
            
        print(f"⚡ Generated {len(trades)} potential trades")
        
        # 4. Get account info
        account_info = self.get_alpaca_account_info()
        account_balance = float(account_info.get('Portfolio Value', '100000').replace('$', '').replace(',', ''))
        
        print(f"💰 Account balance: ${account_balance:,.2f}")
        
        # 5. Execute trades
        executed_trades = 0
        for trade in trades:
            if trade.confidence < 0.5:  # Skip low confidence trades
                print(f"⏭️  Skipping low confidence trade: {trade.symbol} (confidence: {trade.confidence:.2f})")
                continue
                
            position_size = self.calculate_position_size(trade, account_balance)
            
            if position_size > 0:
                success = self.execute_alpaca_trade(trade, position_size)
                if success:
                    executed_trades += 1
                    time.sleep(1)  # Rate limiting
                    
        print(f"✅ Executed {executed_trades} trades")
        
        # 6. Save report
        self.save_trading_report(report)

    def save_trading_report(self, report: Dict):
        """Save trading report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trading_report_{timestamp}.json"
        
        # Add trade log to report
        report['executed_trades'] = self.trade_log
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"📄 Report saved: {filename}")

    def run_continuous_monitoring(self, interval_minutes: int = 30):
        """Run continuous monitoring with specified interval"""
        print(f"🔄 Starting continuous monitoring (every {interval_minutes} minutes)")
        
        while True:
            try:
                self.run_trading_cycle()
                
                # Reset daily counter at midnight
                now = datetime.now()
                if now.hour == 0 and now.minute < interval_minutes:
                    self.daily_trade_count = 0
                    print("🌅 New trading day - resetting counters")
                
                print(f"😴 Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping trader...")
                break
            except Exception as e:
                print(f"❌ Error in trading cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        trader = PredictionTrader()
        trader.run_continuous_monitoring()
    else:
        # Single run
        trader = PredictionTrader()
        trader.run_trading_cycle()

if __name__ == "__main__":
    main()