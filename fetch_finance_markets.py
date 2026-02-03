#!/usr/bin/env python3
"""
Fetch and analyze finance-related markets from Polymarket
"""

import requests
import json
import re
from typing import List, Dict
from datetime import datetime

class PolymarketFinanceExtractor:
    def __init__(self):
        self.api_base = "https://gamma-api.polymarket.com"
        self.finance_keywords = [
            # Stock names
            "Tesla", "TSLA", "Apple", "AAPL", "Microsoft", "MSFT", "Amazon", "AMZN",
            "Google", "GOOGL", "Meta", "META", "Netflix", "NFLX", "Nvidia", "NVDA",
            "GameStop", "GME", "AMC", "Berkshire", "JPMorgan", "Goldman", "Morgan",
            
            # Market terms
            "stock", "Stock", "STOCK", "equity", "share", "NYSE", "NASDAQ", 
            "S&P", "Dow", "Russell", "market", "trading", "earnings", "beat",
            "revenue", "profit", "valuation", "IPO", "acquisition", "merger",
            
            # Financial metrics
            "billion", "trillion", "market cap", "price target", "analyst",
            "upgrade", "downgrade", "buy rating", "sell rating",
            
            # Economic indicators  
            "GDP", "inflation", "Fed", "Federal Reserve", "interest rate",
            "unemployment", "recession", "bull market", "bear market"
        ]
        
    def fetch_markets(self, limit: int = 100) -> List[Dict]:
        """Fetch markets from Polymarket API"""
        try:
            url = f"{self.api_base}/markets?limit={limit}&active=true"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def is_finance_related(self, market: Dict) -> bool:
        """Check if a market is finance-related"""
        question = market.get('question', '').lower()
        description = market.get('description', '').lower()
        text = f"{question} {description}"
        
        return any(keyword.lower() in text for keyword in self.finance_keywords)
    
    def extract_tradeable_symbols(self, market: Dict) -> List[str]:
        """Extract potential tradeable symbols from market text"""
        question = market.get('question', '')
        description = market.get('description', '')
        text = f"{question} {description}"
        
        # Common stock symbols pattern
        symbol_pattern = r'\b[A-Z]{1,5}\b'
        potential_symbols = re.findall(symbol_pattern, text)
        
        # Known major stocks
        known_symbols = {
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NFLX', 
            'NVDA', 'GME', 'AMC', 'BRK.B', 'JPM', 'GS', 'MS', 'BAC', 'WFC',
            'SPY', 'QQQ', 'IWM', 'XLF', 'XLK', 'XLE', 'XLV'
        }
        
        # Filter to likely stock symbols
        likely_symbols = []
        for symbol in potential_symbols:
            if symbol in known_symbols:
                likely_symbols.append(symbol)
            elif len(symbol) <= 4 and symbol not in ['THE', 'AND', 'FOR', 'WILL']:
                likely_symbols.append(symbol)
                
        return list(set(likely_symbols))
    
    def categorize_market(self, market: Dict) -> str:
        """Categorize the type of finance market"""
        question = market.get('question', '').lower()
        
        if any(word in question for word in ['earnings', 'beat', 'revenue', 'profit']):
            return 'earnings'
        elif any(word in question for word in ['price', 'reach', 'above', 'below', '$']):
            return 'price_target'
        elif any(word in question for word in ['ipo', 'public', 'listing']):
            return 'ipo'
        elif any(word in question for word in ['merger', 'acquisition', 'deal']):
            return 'ma'
        elif any(word in question for word in ['fed', 'interest', 'rate', 'inflation']):
            return 'monetary_policy'
        else:
            return 'general'
    
    def analyze_finance_markets(self) -> Dict:
        """Main analysis function"""
        print("Fetching markets from Polymarket...")
        markets = self.fetch_markets(100)
        
        if not markets:
            return {"error": "Failed to fetch markets"}
        
        print(f"Fetched {len(markets)} markets")
        
        finance_markets = []
        for market in markets:
            if self.is_finance_related(market):
                symbols = self.extract_tradeable_symbols(market)
                category = self.categorize_market(market)
                
                finance_market = {
                    'question': market.get('question'),
                    'slug': market.get('slug'),
                    'end_date': market.get('end_date_iso'),
                    'volume_24h': market.get('volume_24hr', 0),
                    'liquidity': market.get('liquidity', 0),
                    'symbols': symbols,
                    'category': category,
                    'url': f"https://polymarket.com/event/{market.get('slug')}"
                }
                finance_markets.append(finance_market)
        
        # Sort by volume
        finance_markets.sort(key=lambda x: x['volume_24h'], reverse=True)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_markets': len(markets),
            'finance_markets': len(finance_markets),
            'markets': finance_markets[:20],  # Top 20 by volume
            'summary': self._create_summary(finance_markets)
        }
    
    def _create_summary(self, markets: List[Dict]) -> Dict:
        """Create summary statistics"""
        categories = {}
        all_symbols = set()
        
        for market in markets:
            cat = market['category']
            categories[cat] = categories.get(cat, 0) + 1
            all_symbols.update(market['symbols'])
        
        return {
            'categories': categories,
            'unique_symbols': sorted(list(all_symbols)),
            'total_volume_24h': sum(m['volume_24h'] for m in markets),
            'avg_liquidity': sum(m['liquidity'] for m in markets) / len(markets) if markets else 0
        }

if __name__ == "__main__":
    extractor = PolymarketFinanceExtractor()
    result = extractor.analyze_finance_markets()
    print(json.dumps(result, indent=2))