#!/usr/bin/env python3
"""
Polymarket to Alpaca Mapping System
Maps prediction market outcomes to tradeable instruments on Alpaca
"""

import json
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

@dataclass
class PredictionSignal:
    market_id: str
    title: str
    description: str
    current_prob: float
    prob_change: float
    volume_24h: float
    liquidity: float
    end_date: datetime
    category: str

@dataclass
class AlpacaTrade:
    symbol: str
    action: str  # buy/sell
    order_type: str  # market/limit/options
    quantity: int
    confidence: float
    reasoning: str
    risk_level: str
    expiration: Optional[datetime] = None  # For options

class PolymarketAlpacaMapper:
    def __init__(self):
        # Define mapping rules between prediction markets and tradeable instruments
        self.mapping_rules = {
            # Election/Political
            "election": {
                "republican": {
                    "bullish": ["RTX", "LMT", "XLE", "XLF"],  # Defense, Energy, Finance
                    "bearish": ["XLK", "TSLA"],  # Tech might be hurt by regulation
                },
                "democrat": {
                    "bullish": ["XLK", "TSLA", "XLV", "PBW"],  # Tech, Healthcare, Clean Energy
                    "bearish": ["XLE", "XME"],  # Oil/Gas, Metals
                }
            },
            
            # Federal Reserve
            "fed": {
                "rate_cut": {
                    "bullish": ["VNQ", "XLU", "TLT"],  # REITs, Utilities, Long bonds
                    "bearish": ["XLF"],  # Banks hurt by lower rates
                },
                "rate_hike": {
                    "bullish": ["XLF", "DXY"],  # Banks, Dollar
                    "bearish": ["VNQ", "XLU", "TLT"],  # Rate sensitive assets
                }
            },
            
            # Earnings/Corporate
            "earnings": {
                "beat": {
                    "direct": True,  # Trade the specific stock
                    "options": True,  # Use options for leverage
                },
                "miss": {
                    "short": True,  # Consider shorting
                    "puts": True,   # Buy puts
                }
            },
            
            # Crypto/Tech
            "crypto": {
                "adoption": {
                    "bullish": ["MSTR", "COIN", "SQ", "TSLA"],
                    "etf": ["BITO", "IBIT"],
                },
                "regulation": {
                    "bearish": ["COIN", "MSTR"],
                    "bullish": ["JPM", "BAC"],  # Traditional finance benefits
                }
            },
            
            # Economic Events
            "economic": {
                "recession": {
                    "bullish": ["TLT", "GLD", "VXX"],  # Safe havens, volatility
                    "bearish": ["SPY", "QQQ", "IWM"],  # Broad market
                },
                "growth": {
                    "bullish": ["QQQ", "XLK", "IWM"],  # Growth stocks, small caps
                    "bearish": ["TLT", "GLD"],  # Risk-off assets
                }
            }
        }
        
        # Stock symbol to company name mapping for better matching
        self.symbol_map = {
            "AAPL": ["apple", "iphone"],
            "TSLA": ["tesla", "elon", "musk"],
            "MSFT": ["microsoft"],
            "GOOGL": ["google", "alphabet"],
            "AMZN": ["amazon"],
            "META": ["meta", "facebook"],
            "NVDA": ["nvidia", "ai chip"],
            "RTX": ["raytheon", "defense"],
            "LMT": ["lockheed", "martin"],
            "JPM": ["jpmorgan", "chase"],
            "BAC": ["bank of america"],
        }

    def categorize_prediction(self, title: str, description: str) -> str:
        """Categorize a prediction market into trading categories"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ["election", "republican", "democrat", "president", "congress"]):
            return "election"
        elif any(word in text for word in ["fed", "federal reserve", "interest rate", "rate cut", "rate hike"]):
            return "fed"
        elif any(word in text for word in ["earnings", "revenue", "profit", "beat", "miss"]):
            return "earnings"
        elif any(word in text for word in ["crypto", "bitcoin", "ethereum", "blockchain"]):
            return "crypto"
        elif any(word in text for word in ["recession", "gdp", "unemployment", "inflation"]):
            return "economic"
        else:
            return "other"

    def extract_stock_symbol(self, title: str, description: str) -> Optional[str]:
        """Extract stock symbol from prediction text"""
        text = f"{title} {description}".lower()
        
        # Direct symbol matching (e.g., "AAPL" in text)
        symbol_pattern = r'\b([A-Z]{1,5})\b'
        matches = re.findall(symbol_pattern, f"{title} {description}")
        for match in matches:
            if len(match) <= 5 and match.isalpha():
                return match
        
        # Company name matching
        for symbol, keywords in self.symbol_map.items():
            if any(keyword in text for keyword in keywords):
                return symbol
                
        return None

    def calculate_signal_strength(self, prediction: PredictionSignal) -> float:
        """Calculate signal strength based on probability change, volume, and liquidity"""
        # Normalize factors
        prob_score = abs(prediction.prob_change) / 100  # Convert to 0-1 scale
        volume_score = min(prediction.volume_24h / 1000000, 1)  # Cap at $1M volume
        liquidity_score = min(prediction.liquidity / 100000, 1)  # Cap at $100k liquidity
        
        # Time decay - stronger signal closer to resolution
        days_to_end = (prediction.end_date - datetime.now()).days
        time_score = max(0, (30 - days_to_end) / 30)  # Stronger signal within 30 days
        
        # Weighted combination
        signal_strength = (
            prob_score * 0.4 +      # Probability change most important
            volume_score * 0.25 +    # Volume shows conviction
            liquidity_score * 0.15 + # Liquidity shows serious money
            time_score * 0.2         # Time urgency
        )
        
        return min(signal_strength, 1.0)

    def map_to_alpaca_trades(self, prediction: PredictionSignal) -> List[AlpacaTrade]:
        """Map a prediction signal to specific Alpaca trades"""
        trades = []
        category = self.categorize_prediction(prediction.title, prediction.description)
        signal_strength = self.calculate_signal_strength(prediction)
        
        # Skip weak signals
        if signal_strength < 0.3:
            return trades
            
        # Check for direct stock mapping first
        stock_symbol = self.extract_stock_symbol(prediction.title, prediction.description)
        if stock_symbol and category == "earnings":
            return self._create_earnings_trades(stock_symbol, prediction, signal_strength)
        
        # Use category-based mapping
        if category in self.mapping_rules:
            return self._create_category_trades(category, prediction, signal_strength)
            
        return trades

    def _create_earnings_trades(self, symbol: str, prediction: PredictionSignal, signal_strength: float) -> List[AlpacaTrade]:
        """Create earnings-specific trades"""
        trades = []
        
        # Determine if it's a beat or miss prediction
        is_beat = any(word in prediction.title.lower() for word in ["beat", "exceed", "above"])
        is_miss = any(word in prediction.title.lower() for word in ["miss", "below", "under"])
        
        if is_beat and prediction.prob_change > 0:
            # Probability of beat increasing
            if signal_strength > 0.7:
                # High confidence - use options
                trades.append(AlpacaTrade(
                    symbol=f"{symbol}_CALL",  # Will need to format properly for options
                    action="buy",
                    order_type="options",
                    quantity=int(signal_strength * 10),
                    confidence=signal_strength,
                    reasoning=f"Beat probability increased by {prediction.prob_change:.1f}%",
                    risk_level="medium",
                    expiration=prediction.end_date + timedelta(days=7)
                ))
            else:
                # Medium confidence - buy stock
                trades.append(AlpacaTrade(
                    symbol=symbol,
                    action="buy",
                    order_type="market",
                    quantity=int(signal_strength * 100),
                    confidence=signal_strength,
                    reasoning=f"Beat probability increased by {prediction.prob_change:.1f}%",
                    risk_level="low"
                ))
                
        elif is_miss and prediction.prob_change > 0:
            # Probability of miss increasing
            trades.append(AlpacaTrade(
                symbol=f"{symbol}_PUT",  # Will need to format properly for options
                action="buy",
                order_type="options",
                quantity=int(signal_strength * 5),
                confidence=signal_strength,
                reasoning=f"Miss probability increased by {prediction.prob_change:.1f}%",
                risk_level="medium",
                expiration=prediction.end_date + timedelta(days=7)
            ))
            
        return trades

    def _create_category_trades(self, category: str, prediction: PredictionSignal, signal_strength: float) -> List[AlpacaTrade]:
        """Create trades based on category mapping"""
        trades = []
        rules = self.mapping_rules[category]
        
        # Determine direction based on prediction content
        direction = self._determine_direction(prediction, category)
        
        if direction in rules:
            symbols = rules[direction].get("bullish" if prediction.prob_change > 0 else "bearish", [])
            
            for symbol in symbols[:3]:  # Limit to top 3 symbols
                position_size = int(signal_strength * 50)  # Scale position by confidence
                
                trades.append(AlpacaTrade(
                    symbol=symbol,
                    action="buy" if prediction.prob_change > 0 else "sell",
                    order_type="market",
                    quantity=position_size,
                    confidence=signal_strength,
                    reasoning=f"{category} prediction: {prediction.title}",
                    risk_level="medium" if signal_strength > 0.6 else "low"
                ))
                
        return trades

    def _determine_direction(self, prediction: PredictionSignal, category: str) -> str:
        """Determine the directional implication of the prediction"""
        text = prediction.title.lower()
        
        if category == "election":
            if any(word in text for word in ["republican", "trump", "gop"]):
                return "republican"
            elif any(word in text for word in ["democrat", "biden", "harris"]):
                return "democrat"
                
        elif category == "fed":
            if any(word in text for word in ["cut", "lower", "reduce"]):
                return "rate_cut"
            elif any(word in text for word in ["hike", "raise", "increase"]):
                return "rate_hike"
                
        elif category == "earnings":
            if any(word in text for word in ["beat", "exceed"]):
                return "beat"
            elif any(word in text for word in ["miss", "below"]):
                return "miss"
                
        return "unknown"

    def generate_trading_report(self, predictions: List[PredictionSignal]) -> Dict:
        """Generate a comprehensive trading report"""
        all_trades = []
        total_signals = len(predictions)
        actionable_signals = 0
        
        for prediction in predictions:
            trades = self.map_to_alpaca_trades(prediction)
            if trades:
                actionable_signals += 1
                all_trades.extend(trades)
                
        # Aggregate by symbol
        symbol_trades = {}
        for trade in all_trades:
            if trade.symbol not in symbol_trades:
                symbol_trades[trade.symbol] = []
            symbol_trades[trade.symbol].append(trade)
            
        return {
            "timestamp": datetime.now().isoformat(),
            "total_signals": total_signals,
            "actionable_signals": actionable_signals,
            "conversion_rate": actionable_signals / total_signals if total_signals > 0 else 0,
            "total_trades": len(all_trades),
            "unique_symbols": len(symbol_trades),
            "trades": all_trades,
            "symbol_summary": symbol_trades
        }

def main():
    # Example usage
    mapper = PolymarketAlpacaMapper()
    
    # Example prediction signals
    test_predictions = [
        PredictionSignal(
            market_id="test1",
            title="Republicans win House majority",
            description="Will Republicans control the House after 2024 election?",
            current_prob=65.0,
            prob_change=10.0,  # Increased by 10%
            volume_24h=500000,
            liquidity=200000,
            end_date=datetime(2024, 11, 6),
            category="election"
        ),
        PredictionSignal(
            market_id="test2", 
            title="Apple beats Q4 earnings by 5%+",
            description="Will Apple exceed analyst estimates by 5% or more?",
            current_prob=70.0,
            prob_change=15.0,  # Strong increase
            volume_24h=1200000,
            liquidity=400000,
            end_date=datetime(2024, 10, 31),
            category="earnings"
        )
    ]
    
    report = mapper.generate_trading_report(test_predictions)
    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    main()