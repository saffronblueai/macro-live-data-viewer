# Macro Data Dashboard

A dashboard displaying global macro data: bond yields, stock indices, currencies, and sentiment.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Fetch all data and start server
python fetch_data.py
python fetch_sentiment.py
python server.py
```

Open http://127.0.0.1:5000 in your browser.

---

## Updating Data

### Market Data (bonds, stocks, currencies)

```bash
# Full refresh (overwrites last 60 days)
python fetch_data.py

# Incremental update (adds new data only)
python fetch_data.py update

# Regenerate data.js from existing CSVs (no fetch)
python fetch_data.py generate
```

**Partial fetches:**
```bash
python fetch_data.py bonds    # Bond yields only
python fetch_data.py stocks   # Stocks & currencies only
```

### Sentiment Data

```bash
# Full fetch (international)
python fetch_sentiment.py

# Full fetch (domestic)
python fetch_sentiment.py --index-type DOMESTIC

# Incremental updates
python fetch_sentiment.py --update                          # International
python fetch_sentiment.py --update --index-type DOMESTIC    # Domestic
python fetch_sentiment.py --update-all                      # Both
```

---

## Running the Server

```bash
python server.py                    # Default (localhost:5000)
python server.py --port 8080        # Custom port
python server.py --host 0.0.0.0     # Allow external access
python server.py --refresh          # Refresh data before starting
python server.py --debug            # Auto-reload on file changes
```

**API endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Server status & data freshness |
| `/api/refresh` | POST | Trigger data refresh |
| `/api/data` | GET | Get all data as JSON |

---

## Output Files

| File | Description |
|------|-------------|
| `data.js` | Combined data for dashboard |
| `bond_yields_10y.csv` | 10-year bond yields |
| `stock_indices.csv` | Stock index prices |
| `currencies.csv` | Currency rates vs USD |
| `sentiment_data.csv` | International sentiment |
| `sentiment_data_domestic.csv` | Domestic sentiment |
