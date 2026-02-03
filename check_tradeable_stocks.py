#!/usr/bin/env python3
"""
Check which stocks are tradeable on Alpaca and map them to typical Polymarket finance bets
"""

import subprocess
import json
import sys
from typing import List, Dict

class AlpacaTradingChecker:
    def __init__(self):
        # Common stocks that often appear in prediction markets
        self.common_finance_stocks = [
            # FAANG/Tech
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NFLX", "NVDA",
            # Traditional Finance
            "JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA",
            # Popular retail stocks
            "GME", "AMC", "BB", "NOK", "PLTR", "COIN",
            # ETFs
            "SPY", "QQQ", "IWM", "XLF", "XLK", "XLE", "XLV", "XLU",
            # Energy
            "XOM", "CVX", "COP", "EOG",
            # Healthcare
            "JNJ", "PFE", "UNH", "ABBV",
            # Consumer
            "WMT", "PG", "KO", "PEP", "DIS"
        ]
        
    def check_stock_tradeable(self, symbol: str) -> Dict:
        """Check if a stock is tradeable on Alpaca"""
        try:
            cmd = ["mcporter", "--config", "../../config/mcporter.json", 
                   "call", "alpaca.get_stock_latest_quote", f"symbol_or_symbols={symbol}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {"symbol": symbol, "tradeable": True, "data": data}
            else:
                return {"symbol": symbol, "tradeable": False, "error": result.stderr}
        except Exception as e:
            return {"symbol": symbol, "tradeable": False, "error": str(e)}
    
    def check_account_info(self) -> Dict:
        """Check current account status"""
        try:
            cmd = ["mcporter", "--config", "../../config/mcporter.json", 
                   "call", "alpaca.get_account_info"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {"status": "success", "data": json.loads(result.stdout)}
            else:
                return {"status": "error", "error": result.stderr}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def generate_sample_finance_signals(self) -> List[Dict]:
        """Generate sample finance-related signals that might come from Polymarket"""
        return [
            {
                "market_type": "earnings_beat",
                "description": "AAPL will beat Q4 2024 earnings estimates",
                "symbols": ["AAPL"],
                "probability": 0.73,
                "confidence": "high",
                "trade_suggestion": "buy AAPL calls if prob > 70%"
            },
            {
                "market_type": "price_target",
                "description": "TSLA will reach $300 by March 2026",
                "symbols": ["TSLA"],
                "probability": 0.45,
                "confidence": "medium",
                "trade_suggestion": "neutral - wait for higher confidence"
            },
            {
                "market_type": "sector_rotation",
                "description": "Tech will outperform Finance in Q1 2026",
                "symbols": ["XLK", "XLF"],
                "probability": 0.68,
                "confidence": "high",
                "trade_suggestion": "long XLK, short XLF"
            },
            {
                "market_type": "fed_policy",
                "description": "Fed will cut rates by 0.25% in March 2026",
                "symbols": ["XLF", "SPY", "TLT"],
                "probability": 0.82,
                "confidence": "very high",
                "trade_suggestion": "long financial stocks, long bonds"
            },
            {
                "market_type": "crypto_correlation",
                "description": "Bitcoin will break correlation with NASDAQ",
                "symbols": ["QQQ", "COIN"],
                "probability": 0.38,
                "confidence": "low",
                "trade_suggestion": "wait for clearer signal"
            }
        ]
    
    def run_analysis(self) -> Dict:
        """Run complete analysis"""
        print("🔍 Checking Alpaca account status...")
        account_info = self.check_account_info()
        
        if account_info["status"] != "success":
            return {"error": "Cannot connect to Alpaca", "details": account_info}
        
        print("✅ Alpaca connection successful")
        print(f"💰 Account balance: ${float(account_info['data']['cash']):,.2f}")
        print(f"⚡ Buying power: ${float(account_info['data']['buying_power']):,.2f}")
        
        print(f"\n📊 Checking {len(self.common_finance_stocks)} common stocks...")
        
        tradeable_stocks = []
        non_tradeable = []
        
        for i, symbol in enumerate(self.common_finance_stocks):
            print(f"Checking {symbol} ({i+1}/{len(self.common_finance_stocks)})...", end="")
            result = self.check_stock_tradeable(symbol)
            
            if result["tradeable"]:
                tradeable_stocks.append(symbol)
                print(" ✅")
            else:
                non_tradeable.append({"symbol": symbol, "error": result.get("error", "Unknown")})
                print(" ❌")
        
        print(f"\n📈 Generating sample finance prediction signals...")
        signals = self.generate_sample_finance_signals()
        
        # Filter signals to only include tradeable symbols
        valid_signals = []
        for signal in signals:
            valid_symbols = [s for s in signal["symbols"] if s in tradeable_stocks]
            if valid_symbols:
                signal["tradeable_symbols"] = valid_symbols
                signal["can_trade"] = True
                valid_signals.append(signal)
            else:
                signal["can_trade"] = False
        
        return {
            "timestamp": str(datetime.now()),
            "account": {
                "status": "connected",
                "balance": account_info['data']['cash'],
                "buying_power": account_info['data']['buying_power']
            },
            "stock_analysis": {
                "total_checked": len(self.common_finance_stocks),
                "tradeable_count": len(tradeable_stocks),
                "tradeable_symbols": sorted(tradeable_stocks),
                "non_tradeable_count": len(non_tradeable),
                "non_tradeable": non_tradeable[:5]  # Show first 5 errors only
            },
            "prediction_signals": {
                "total_signals": len(signals),
                "tradeable_signals": len(valid_signals),
                "signals": valid_signals
            }
        }

if __name__ == "__main__":
    checker = AlpacaTradingChecker()
    result = checker.run_analysis()
    print(f"\n📋 ANALYSIS COMPLETE")
    print("=" * 50)
    print(json.dumps(result, indent=2, default=str))