#!/bin/bash
# Fetch finance-related markets from Polymarket using curl and jq

echo "🔍 Fetching finance markets from Polymarket..."

# Fetch markets and filter for finance-related keywords
curl -s "https://gamma-api.polymarket.com/markets?limit=100&active=true" | \
jq -r '
# Define finance keywords
def finance_keywords: [
  "stock", "Stock", "STOCK", "equity", "share", "NYSE", "NASDAQ", 
  "S&P", "Dow", "Russell", "market", "trading", "earnings", "beat",
  "Tesla", "TSLA", "Apple", "AAPL", "Microsoft", "MSFT", "Amazon", "AMZN",
  "Google", "GOOGL", "Meta", "META", "Netflix", "NFLX", "Nvidia", "NVDA",
  "GameStop", "GME", "Fed", "Federal Reserve", "interest rate", "inflation",
  "billion", "trillion", "market cap", "price target", "IPO", "acquisition"
];

# Filter markets that contain finance keywords
map(select(
  (.question + " " + (.description // "")) as $text |
  finance_keywords | any($text | test(.; "i"))
)) |

# Sort by 24h volume descending
sort_by(-(.volume_24hr // 0)) |

# Format output
{
  timestamp: now | strftime("%Y-%m-%d %H:%M:%S UTC"),
  total_finance_markets: length,
  markets: map({
    question: .question,
    slug: .slug,
    volume_24h: (.volume_24hr // 0),
    liquidity: (.liquidity // 0),
    end_date: .end_date_iso,
    url: "https://polymarket.com/event/\(.slug)",
    
    # Extract potential stock symbols (3-5 letter uppercase words)
    symbols: [(.question + " " + (.description // "")) | 
              scan("\\\\b[A-Z]{2,5}\\\\b") | 
              select(. as $s | ["AAPL","MSFT","GOOGL","AMZN","TSLA","META","NFLX","NVDA","GME","SPY","QQQ"] | 
                     any(. == $s) or ($s | length <= 4 and (. | test("^[A-Z]+$"))))] | unique,
    
    # Categorize market type
    category: (
      if (.question | test("earnings|beat|revenue|profit"; "i")) then "earnings"
      elif (.question | test("price|reach|above|below|\\$"; "i")) then "price_target" 
      elif (.question | test("ipo|public|listing"; "i")) then "ipo"
      elif (.question | test("merger|acquisition|deal"; "i")) then "merger_acquisition"
      elif (.question | test("fed|interest|rate|inflation"; "i")) then "monetary_policy"
      else "general"
      end
    )
  }) | .[0:15]  # Top 15 markets
}'