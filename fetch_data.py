"""
Unified data fetcher for Macro Dashboard.

Downloads and saves:
  - 10-year bond yields (from FinanceFlowAPI)
  - Stock indices (from Yahoo Finance)
  - Currency rates vs USD (from Yahoo Finance)

Outputs:
  - bond_yields_10y.csv: Bond yield data
  - stock_indices.csv: Stock index close prices
  - currencies.csv: Currency rates vs USD
  - data.js: Combined JavaScript data file for dashboard

Usage:
  python fetch_data.py          # Fetch all data (60 days, overwrites)
  python fetch_data.py bonds    # Fetch only bond yields (60 days)
  python fetch_data.py stocks   # Fetch only stocks and currencies (60 days)
  python fetch_data.py generate # Only regenerate JS from existing CSVs
  python fetch_data.py update   # Update existing CSVs to today (incremental)
"""

import sys
import csv
import json
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import time


# ============================================================================
# Configuration
# ============================================================================

BASE_PATH = Path(__file__).parent

# Bond API Configuration
BOND_API_KEY = "26a51c0ce9c0e35229be63e976797162c47b6ff5b7089a6473c6ecb362a14f2c"
BOND_API_URL = "https://financeflowapi.com/api/v1/bonds-history"

# Top 20 countries for bond yields
BOND_COUNTRIES = [
    "United_States", "United_Kingdom", "Germany", "France", "Japan",
    "Canada", "Australia", "Italy", "Spain", "China",
    "India", "Brazil", "South_Korea", "Netherlands", "Switzerland",
    "Belgium", "Sweden", "Singapore", "Mexico", "Indonesia"
]

# Country display names and flags
COUNTRY_DISPLAY = {
    "United_States": ("United States", "🇺🇸"),
    "United_Kingdom": ("United Kingdom", "🇬🇧"),
    "Germany": ("Germany", "🇩🇪"),
    "France": ("France", "🇫🇷"),
    "Japan": ("Japan", "🇯🇵"),
    "Canada": ("Canada", "🇨🇦"),
    "Australia": ("Australia", "🇦🇺"),
    "Italy": ("Italy", "🇮🇹"),
    "Spain": ("Spain", "🇪🇸"),
    "China": ("China", "🇨🇳"),
    "India": ("India", "🇮🇳"),
    "Brazil": ("Brazil", "🇧🇷"),
    "South_Korea": ("South Korea", "🇰🇷"),
    "Netherlands": ("Netherlands", "🇳🇱"),
    "Switzerland": ("Switzerland", "🇨🇭"),
    "Belgium": ("Belgium", "🇧🇪"),
    "Sweden": ("Sweden", "🇸🇪"),
    "Singapore": ("Singapore", "🇸🇬"),
    "Mexico": ("Mexico", "🇲🇽"),
    "Indonesia": ("Indonesia", "🇮🇩"),
    "Taiwan": ("Taiwan", "🇹🇼"),
    "Poland": ("Poland", "🇵🇱"),
    "Argentina": ("Argentina", "🇦🇷"),
    "Thailand": ("Thailand", "🇹🇭"),
    "Ireland": ("Ireland", "🇮🇪"),
    "Israel": ("Israel", "🇮🇱"),
    "Austria": ("Austria", "🇦🇹"),
    "Norway": ("Norway", "🇳🇴"),
    "United_Arab_Emirates": ("UAE", "🇦🇪"),
    "Nigeria": ("Nigeria", "🇳🇬"),
    "South_Africa": ("South Africa", "🇿🇦"),
    "Malaysia": ("Malaysia", "🇲🇾"),
    "Denmark": ("Denmark", "🇩🇰"),
    "Philippines": ("Philippines", "🇵🇭"),
    "Hong_Kong": ("Hong Kong", "🇭🇰"),
    "Vietnam": ("Vietnam", "🇻🇳"),
    "Bangladesh": ("Bangladesh", "🇧🇩"),
    "Pakistan": ("Pakistan", "🇵🇰"),
    "Chile": ("Chile", "🇨🇱"),
    "Colombia": ("Colombia", "🇨🇴"),
    "Finland": ("Finland", "🇫🇮"),
    "Portugal": ("Portugal", "🇵🇹"),
    "New_Zealand": ("New Zealand", "🇳🇿"),
    "Czech_Republic": ("Czech Republic", "🇨🇿"),
    "Greece": ("Greece", "🇬🇷"),
    "Peru": ("Peru", "🇵🇪"),
    "Qatar": ("Qatar", "🇶🇦"),
    "Russia": ("Russia", "🇷🇺"),
    "Saudi_Arabia": ("Saudi Arabia", "🇸🇦"),
    "Turkey": ("Turkey", "🇹🇷"),
}


# ============================================================================
# Bond Yields Fetching
# ============================================================================

def fetch_bond_data(country: str, date_from: str, date_to: str) -> dict:
    """Fetch bond yield data for a specific country with retry logic."""
    params = {
        "api_key": BOND_API_KEY,
        "country": country.lower(),
        "type": "10y",
        "frequency": "day",
        "date_from": date_from,
        "date_to": date_to
    }
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.get(BOND_API_URL, params=params, timeout=30)
            
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    print(f"    Rate limited, waiting {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                return {}
            
            if response.status_code != 200:
                data = response.json() if response.text else {}
                msg = data.get('message', response.text[:100])
                print(f"    Error {response.status_code}: {msg}")
                return {}
                
            data = response.json()
            
            if data.get("success"):
                return {item["date"]: item["yield"] for item in data.get("data", [])}
            else:
                print(f"    API error: {data.get('message', 'Unknown error')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"    Request error: {e}")
            return {}
    
    return {}


def fetch_bond_yields():
    """Fetch 60 days of 10-year bond yields for all countries."""
    print("\n" + "=" * 60)
    print("FETCHING BOND YIELDS")
    print("=" * 60)
    
    date_to = datetime.now()
    date_from = date_to - timedelta(days=60)
    date_from_str = date_from.strftime("%Y-%m-%d")
    date_to_str = date_to.strftime("%Y-%m-%d")
    
    print(f"Date range: {date_from_str} to {date_to_str}")
    print(f"Countries: {len(BOND_COUNTRIES)}")
    print("-" * 60)
    
    all_data = {}
    
    for i, country in enumerate(BOND_COUNTRIES, 1):
        print(f"[{i}/{len(BOND_COUNTRIES)}] {country}...")
        country_data = fetch_bond_data(country, date_from_str, date_to_str)
        all_data[country] = country_data
        print(f"    Got {len(country_data)} data points")
        
        if i < len(BOND_COUNTRIES):
            time.sleep(1.5)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    df.index.name = "date"
    df = df.sort_index(ascending=False)
    df = df[BOND_COUNTRIES]
    
    # Save to CSV
    output_file = BASE_PATH / "bond_yields_10y.csv"
    df.to_csv(output_file)
    
    print("-" * 60)
    print(f"Saved: {output_file.name}")
    print(f"  Dates: {len(df)}, Countries: {len(df.columns)}")
    
    return df


# ============================================================================
# Stock & Currency Fetching (Yahoo Finance)
# ============================================================================

def load_country_tickers() -> pd.DataFrame:
    """Load country tickers from CSV file."""
    csv_path = BASE_PATH / "countries_tickers.csv"
    return pd.read_csv(csv_path)


def fetch_ticker_data(ticker: str, period_days: int = 60) -> pd.DataFrame:
    """Fetch historical data for a single ticker from Yahoo Finance."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days + 30)
        
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(start=start_date, end=end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        df = df[['Close']].copy()
        df.index = df.index.strftime('%Y-%m-%d')
        df = df.tail(60)
        
        return df
        
    except Exception as e:
        print(f"    Error: {e}")
        return pd.DataFrame()


def fetch_stocks_currencies():
    """Fetch stock indices and currency data from Yahoo Finance."""
    print("\n" + "=" * 60)
    print("FETCHING STOCKS & CURRENCIES (Yahoo Finance)")
    print("=" * 60)
    
    countries_df = load_country_tickers()
    print(f"Found {len(countries_df)} countries in tickers file")
    print("-" * 60)
    
    stock_data = {}
    currency_data = {}
    total = len(countries_df)
    
    for i, row in countries_df.iterrows():
        country = row['country']
        stock_ticker = row['stock_index_ticker']
        currency_ticker = row['currency_ticker']
        
        print(f"[{i+1}/{total}] {country}")
        
        # Fetch stock index
        print(f"    Stock: {stock_ticker}")
        stock_df = fetch_ticker_data(stock_ticker)
        if not stock_df.empty:
            stock_data[country] = stock_df['Close']
            print(f"    Got {len(stock_df)} stock data points")
        
        time.sleep(0.3)
        
        # Fetch currency
        print(f"    Currency: {currency_ticker}")
        currency_df = fetch_ticker_data(currency_ticker)
        if not currency_df.empty:
            currency_data[country] = currency_df['Close']
            print(f"    Got {len(currency_df)} currency data points")
        
        if i < total - 1:
            time.sleep(0.5)
    
    # Convert to DataFrames
    stocks_df = pd.DataFrame(stock_data)
    currencies_df = pd.DataFrame(currency_data)
    
    # Save stock indices
    if not stocks_df.empty:
        stocks_df = stocks_df.sort_index(ascending=False)
        stocks_df.index.name = 'date'
        output_file = BASE_PATH / "stock_indices.csv"
        stocks_df.to_csv(output_file)
        print("-" * 60)
        print(f"Saved: {output_file.name}")
        print(f"  Dates: {len(stocks_df)}, Countries: {len(stocks_df.columns)}")
    
    # Save currencies
    if not currencies_df.empty:
        currencies_df = currencies_df.sort_index(ascending=False)
        currencies_df.index.name = 'date'
        output_file = BASE_PATH / "currencies.csv"
        currencies_df.to_csv(output_file)
        print(f"Saved: {output_file.name}")
        print(f"  Dates: {len(currencies_df)}, Countries: {len(currencies_df.columns)}")
    
    return stocks_df, currencies_df


# ============================================================================
# Update Mode (Incremental Updates)
# ============================================================================

def get_last_date_from_csv(csv_path: Path) -> str | None:
    """Get the most recent date from an existing CSV file."""
    if not csv_path.exists():
        return None
    
    try:
        df = pd.read_csv(csv_path, index_col='date')
        if df.empty:
            return None
        # Index is sorted descending, first row is most recent
        return df.index[0]
    except Exception as e:
        print(f"  Error reading {csv_path.name}: {e}")
        return None


def update_bond_yields():
    """Update bond yields CSV with data from last date to today."""
    print("\n" + "=" * 60)
    print("UPDATING BOND YIELDS")
    print("=" * 60)
    
    csv_path = BASE_PATH / "bond_yields_10y.csv"
    last_date = get_last_date_from_csv(csv_path)
    
    if not last_date:
        print("No existing data found. Running full fetch instead.")
        return fetch_bond_yields()
    
    # Parse last date and calculate date range
    last_date_dt = datetime.strptime(last_date, "%Y-%m-%d")
    today = datetime.now()
    
    # Start from day after last date
    date_from = last_date_dt + timedelta(days=1)
    
    if date_from.date() > today.date():
        print(f"Data is already up to date (last: {last_date})")
        return pd.read_csv(csv_path, index_col='date')
    
    date_from_str = date_from.strftime("%Y-%m-%d")
    date_to_str = today.strftime("%Y-%m-%d")
    
    print(f"Existing data up to: {last_date}")
    print(f"Fetching: {date_from_str} to {date_to_str}")
    print(f"Countries: {len(BOND_COUNTRIES)}")
    print("-" * 60)
    
    # Fetch new data
    new_data = {}
    for i, country in enumerate(BOND_COUNTRIES, 1):
        print(f"[{i}/{len(BOND_COUNTRIES)}] {country}...")
        country_data = fetch_bond_data(country, date_from_str, date_to_str)
        new_data[country] = country_data
        print(f"    Got {len(country_data)} new data points")
        
        if i < len(BOND_COUNTRIES):
            time.sleep(1.5)
    
    # Load existing data
    existing_df = pd.read_csv(csv_path, index_col='date')
    
    # Create DataFrame from new data
    new_df = pd.DataFrame(new_data)
    new_df.index.name = "date"
    
    if new_df.empty:
        print("No new data fetched.")
        return existing_df
    
    # Ensure columns match
    new_df = new_df.reindex(columns=existing_df.columns)
    
    # Combine: new data on top of existing (both sorted descending)
    combined_df = pd.concat([new_df, existing_df])
    combined_df = combined_df[~combined_df.index.duplicated(keep='first')]
    combined_df = combined_df.sort_index(ascending=False)
    
    # Save
    combined_df.to_csv(csv_path)
    
    print("-" * 60)
    print(f"Updated: {csv_path.name}")
    print(f"  Added {len(new_df)} new dates")
    print(f"  Total dates: {len(combined_df)}")
    
    return combined_df


def update_stocks_currencies():
    """Update stock indices and currencies CSVs with data from last date to today."""
    print("\n" + "=" * 60)
    print("UPDATING STOCKS & CURRENCIES")
    print("=" * 60)
    
    stocks_path = BASE_PATH / "stock_indices.csv"
    currencies_path = BASE_PATH / "currencies.csv"
    
    # Get last dates from both files
    stocks_last_date = get_last_date_from_csv(stocks_path)
    currencies_last_date = get_last_date_from_csv(currencies_path)
    
    if not stocks_last_date and not currencies_last_date:
        print("No existing data found. Running full fetch instead.")
        return fetch_stocks_currencies()
    
    # Use the older date to ensure we get all updates
    if stocks_last_date and currencies_last_date:
        last_date = min(stocks_last_date, currencies_last_date)
    else:
        last_date = stocks_last_date or currencies_last_date
    
    last_date_dt = datetime.strptime(last_date, "%Y-%m-%d")
    today = datetime.now()
    
    # Check if update is needed
    if last_date_dt.date() >= today.date():
        print(f"Data is already up to date (last: {last_date})")
        stocks_df = pd.read_csv(stocks_path, index_col='date') if stocks_last_date else pd.DataFrame()
        currencies_df = pd.read_csv(currencies_path, index_col='date') if currencies_last_date else pd.DataFrame()
        return stocks_df, currencies_df
    
    # Calculate days to fetch (from last date to today, plus buffer)
    days_to_fetch = (today - last_date_dt).days + 5  # Add buffer for weekends/holidays
    
    print(f"Existing data up to: {last_date}")
    print(f"Fetching last {days_to_fetch} days to ensure coverage")
    print("-" * 60)
    
    countries_df = load_country_tickers()
    print(f"Found {len(countries_df)} countries in tickers file")
    
    stock_data = {}
    currency_data = {}
    total = len(countries_df)
    
    for i, row in countries_df.iterrows():
        country = row['country']
        stock_ticker = row['stock_index_ticker']
        currency_ticker = row['currency_ticker']
        
        print(f"[{i+1}/{total}] {country}")
        
        # Fetch stock index
        print(f"    Stock: {stock_ticker}")
        stock_df = fetch_ticker_data(stock_ticker, period_days=days_to_fetch)
        if not stock_df.empty:
            stock_data[country] = stock_df['Close']
            print(f"    Got {len(stock_df)} stock data points")
        
        time.sleep(0.3)
        
        # Fetch currency
        print(f"    Currency: {currency_ticker}")
        currency_df = fetch_ticker_data(currency_ticker, period_days=days_to_fetch)
        if not currency_df.empty:
            currency_data[country] = currency_df['Close']
            print(f"    Got {len(currency_df)} currency data points")
        
        if i < total - 1:
            time.sleep(0.5)
    
    # Convert to DataFrames
    new_stocks_df = pd.DataFrame(stock_data)
    new_currencies_df = pd.DataFrame(currency_data)
    
    # Update stock indices
    if not new_stocks_df.empty:
        new_stocks_df.index.name = 'date'
        
        if stocks_last_date:
            existing_stocks = pd.read_csv(stocks_path, index_col='date')
            # Merge: use new data for dates that exist in both
            combined_stocks = pd.concat([new_stocks_df, existing_stocks])
            combined_stocks = combined_stocks[~combined_stocks.index.duplicated(keep='first')]
            combined_stocks = combined_stocks.sort_index(ascending=False)
        else:
            combined_stocks = new_stocks_df.sort_index(ascending=False)
        
        combined_stocks.to_csv(stocks_path)
        print("-" * 60)
        print(f"Updated: {stocks_path.name}")
        print(f"  Total dates: {len(combined_stocks)}, Countries: {len(combined_stocks.columns)}")
    
    # Update currencies
    if not new_currencies_df.empty:
        new_currencies_df.index.name = 'date'
        
        if currencies_last_date:
            existing_currencies = pd.read_csv(currencies_path, index_col='date')
            # Merge: use new data for dates that exist in both
            combined_currencies = pd.concat([new_currencies_df, existing_currencies])
            combined_currencies = combined_currencies[~combined_currencies.index.duplicated(keep='first')]
            combined_currencies = combined_currencies.sort_index(ascending=False)
        else:
            combined_currencies = new_currencies_df.sort_index(ascending=False)
        
        combined_currencies.to_csv(currencies_path)
        print(f"Updated: {currencies_path.name}")
        print(f"  Total dates: {len(combined_currencies)}, Countries: {len(combined_currencies.columns)}")
    
    return new_stocks_df, new_currencies_df


# ============================================================================
# Sentiment Data Parsing
# ============================================================================

# Map sentiment CSV country names to our standardized names
SENTIMENT_COUNTRY_MAP = {
    "Argentina": "Argentina",
    "Australia": "Australia",
    "Brazil": "Brazil",
    "Canada": "Canada",
    "China": "China",
    "Czechia": "Czech_Republic",
    "Egypt": "Egypt",
    "France": "France",
    "Germany": "Germany",
    "Hungary": "Hungary",
    "India": "India",
    "Israel": "Israel",
    "Italy": "Italy",
    "Japan": "Japan",
    "Korea, Republic of": "South_Korea",
    "Mexico": "Mexico",
    "New Zealand": "New_Zealand",
    "Nigeria": "Nigeria",
    "Pakistan": "Pakistan",
    "Philippines": "Philippines",
    "Poland": "Poland",
    "Russian Federation": "Russia",
    "Saudi Arabia": "Saudi_Arabia",
    "Singapore": "Singapore",
    "South Africa": "South_Africa",
    "Spain": "Spain",
    "Taiwan, Province of China": "Taiwan",
    "Turkey": "Turkey",
    "Ukraine": "Ukraine",
    "United Kingdom": "United_Kingdom",
    "United States": "United_States",
}


def parse_sentiment_data(csv_path: Path) -> tuple[dict, list]:
    """
    Parse sentiment_data.csv into structured data.
    Returns: (sentiment_data, topics_list)
    
    sentiment_data structure:
    {
        "topic_name": {
            "country_id": [
                {"date": "2026-01-17", "value": 0.42, "count": 12},
                ...
            ]
        }
    }
    """
    sentiment_data = {}
    topics = set()
    
    if not csv_path.exists():
        print(f"  Warning: {csv_path.name} not found")
        return {}, []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Find all country columns (ending with _sentiment)
        sentiment_cols = [col for col in reader.fieldnames if col.endswith('_sentiment')]
        
        for row in reader:
            date = row['date']
            topic = row['topic']
            topics.add(topic)
            
            if topic not in sentiment_data:
                sentiment_data[topic] = {}
            
            for col in sentiment_cols:
                # Extract country name from column (e.g., "China_sentiment" -> "China")
                csv_country = col.replace('_sentiment', '')
                
                # Map to our standardized country name
                country_id = SENTIMENT_COUNTRY_MAP.get(csv_country)
                if not country_id:
                    continue
                
                sentiment_val = row[col].strip() if row[col] else ''
                count_col = col.replace('_sentiment', '_count')
                count_val = row.get(count_col, '').strip() if row.get(count_col) else ''
                
                if sentiment_val:
                    try:
                        if country_id not in sentiment_data[topic]:
                            sentiment_data[topic][country_id] = []
                        
                        sentiment_data[topic][country_id].append({
                            'date': date,
                            'value': round(float(sentiment_val), 4),
                            'count': int(float(count_val)) if count_val else 0
                        })
                    except ValueError:
                        pass
    
    # Sort each country's data by date (ascending for charts)
    for topic in sentiment_data:
        for country in sentiment_data[topic]:
            sentiment_data[topic][country].sort(key=lambda x: x['date'])
    
    # Sort topics for consistent ordering
    topics_list = sorted(list(topics))
    
    return sentiment_data, topics_list


# ============================================================================
# JavaScript Data Generation
# ============================================================================

def parse_csv_data(csv_path: Path) -> dict:
    """Parse a CSV file into country-indexed data."""
    data = {}
    
    if not csv_path.exists():
        print(f"  Warning: {csv_path.name} not found")
        return data
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        countries = [col for col in reader.fieldnames if col != 'date']
        
        for country in countries:
            data[country] = []
        
        for row in reader:
            date = row['date']
            for country in countries:
                value = row[country].strip() if row[country] else ''
                if value:
                    try:
                        data[country].append({
                            'date': date,
                            'value': float(value)
                        })
                    except ValueError:
                        pass
    
    # Sort each country's data by date (ascending for charts)
    for country in data:
        data[country].sort(key=lambda x: x['date'])
    
    return data


def normalize_country_name(name: str) -> str:
    """Normalize country names (replace spaces with underscores)."""
    return name.replace(' ', '_')


def generate_js_data():
    """Generate JavaScript data file from all CSV sources."""
    print("\n" + "=" * 60)
    print("GENERATING JAVASCRIPT DATA FILE")
    print("=" * 60)
    
    # Parse all data sources
    bond_data = parse_csv_data(BASE_PATH / "bond_yields_10y.csv")
    currency_data = parse_csv_data(BASE_PATH / "currencies.csv")
    stock_data = parse_csv_data(BASE_PATH / "stock_indices.csv")
    
    # Parse sentiment data (both international and domestic)
    sentiment_intl, sentiment_topics_intl = parse_sentiment_data(BASE_PATH / "sentiment_data.csv")
    sentiment_domestic, sentiment_topics_domestic = parse_sentiment_data(BASE_PATH / "sentiment_data_domestic.csv")
    
    # Combine topics from both (should be the same, but union just in case)
    all_topics = sorted(set(sentiment_topics_intl) | set(sentiment_topics_domestic))
    
    # Normalize keys (replace spaces with underscores)
    currency_data = {normalize_country_name(k): v for k, v in currency_data.items()}
    stock_data = {normalize_country_name(k): v for k, v in stock_data.items()}
    
    # Combine all data
    all_data = {
        'bond_yields': bond_data,
        'currencies': currency_data,
        'stock_indices': stock_data
    }
    
    # Build country names and flags dicts
    country_names = {k: v[0] for k, v in COUNTRY_DISPLAY.items()}
    country_flags = {k: v[1] for k, v in COUNTRY_DISPLAY.items()}
    
    # Write JavaScript file
    js_path = BASE_PATH / "data.js"
    js_content = f"""// Auto-generated macro data for dashboard
// Run: python fetch_data.py generate

const ALL_DATA = {json.dumps(all_data, indent=2)};

const SENTIMENT_DATA_INTERNATIONAL = {json.dumps(sentiment_intl, indent=2)};

const SENTIMENT_DATA_DOMESTIC = {json.dumps(sentiment_domestic, indent=2)};

const SENTIMENT_TOPICS = {json.dumps(all_topics)};

const TOP_20_COUNTRIES = {json.dumps(BOND_COUNTRIES)};

const COUNTRY_NAMES = {json.dumps(country_names, indent=2)};

const COUNTRY_FLAGS = {json.dumps(country_flags, indent=2)};
"""
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Generated: {js_path.name}")
    print(f"  Bond Yields: {len(bond_data)} countries")
    print(f"  Currencies: {len(currency_data)} countries")
    print(f"  Stock Indices: {len(stock_data)} countries")
    print(f"  Sentiment Topics: {len(all_topics)}")
    print(f"  Sentiment International: {len(sentiment_intl)} topics")
    print(f"  Sentiment Domestic: {len(sentiment_domestic)} topics")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else ['all']
    
    print("=" * 60)
    print("MACRO DATA FETCHER")
    print("=" * 60)
    print(f"Command: {args[0] if args else 'all'}")
    print(f"Today: {datetime.now().strftime('%Y-%m-%d')}")
    
    if 'all' in args:
        fetch_bond_yields()
        fetch_stocks_currencies()
        generate_js_data()
    elif 'bonds' in args:
        fetch_bond_yields()
        generate_js_data()
    elif 'stocks' in args:
        fetch_stocks_currencies()
        generate_js_data()
    elif 'generate' in args:
        generate_js_data()
    elif 'update' in args:
        # Incremental update mode - only fetch new data since last date
        update_bond_yields()
        update_stocks_currencies()
        generate_js_data()
    else:
        print(f"Unknown command: {args[0]}")
        print("Usage: python fetch_data.py [all|bonds|stocks|generate|update]")
        return
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
