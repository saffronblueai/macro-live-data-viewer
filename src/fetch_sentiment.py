"""
Sentiment Data Fetcher for Macro Dashboard.

Fetches regional macro sentiment data from Permutable AI API.

API Details:
  - Paginated results using next_token
  - Returns sentiment scores per country/topic/date
  
Output:
  - sentiment_data.csv: INTERNATIONAL index wide-format CSV
  - sentiment_data_domestic.csv: DOMESTIC index wide-format CSV
    Structure: date, topic, country1_avg, country1_count, country2_avg, country2_count, ...
    
Usage:
  python fetch_sentiment.py                              # Full fetch INTERNATIONAL (default)
  python fetch_sentiment.py --index-type DOMESTIC        # Full fetch DOMESTIC data
  python fetch_sentiment.py --start 2025-11-01           # Custom start date
  python fetch_sentiment.py --end 2026-01-19             # Custom end date
  python fetch_sentiment.py --start 2026-01-15 --end 2026-01-19  # Date range
  python fetch_sentiment.py --limit 500                  # Custom records per page
  python fetch_sentiment.py --max-pages 50               # Limit to 50 pages max
  
  # Update modes (incremental) - automatically uses date range:
  python fetch_sentiment.py --update                     # Update INTERNATIONAL to today
  python fetch_sentiment.py --update --index-type DOMESTIC  # Update DOMESTIC to today
  python fetch_sentiment.py --update-all                 # Update BOTH files to today
"""

import sys
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
import time


# ============================================================================
# Configuration
# ============================================================================

BASE_PATH = Path(__file__).parent

# Permutable AI API Configuration
PERMUTABLE_API_KEY = "IjIO9k01nS4nJnTJBBya5at22joflSxV8xJQ6KOG"
PERMUTABLE_BASE_URL = "https://copilot-api.permutable.ai/v1/macro/historical/regional/macro_1"

DEFAULT_START_DATE = "2025-11-01"
DEFAULT_LIMIT = 1000
DEFAULT_MAX_PAGES = None  # No limit by default, set to integer to limit
DEFAULT_INDEX_TYPE = "INTERNATIONAL"  # INTERNATIONAL or DOMESTIC


# ============================================================================
# API Fetching
# ============================================================================

def fetch_sentiment_page(start_date: str, end_date: str = None, limit: int = DEFAULT_LIMIT, next_token: str = None, index_type: str = DEFAULT_INDEX_TYPE) -> dict:
    """
    Fetch a single page of sentiment data from Permutable API.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format (optional, defaults to today if not specified)
        limit: Number of records per page
        next_token: Pagination token for subsequent requests
        index_type: Index type - INTERNATIONAL or DOMESTIC
        
    Returns:
        API response as dictionary
    """
    params = {
        "topic_preset": "ALL",
        "index_type": index_type,
        "limit": limit,
        "country_preset": "ALL",
        "language_preset": "ALL",
        "source_country_preset": "ALL",
        "source_preset": "ALL",
        "start_date": start_date,
        "api-key": PERMUTABLE_API_KEY
    }
    
    # Add end_date if specified
    if end_date:
        params["end_date"] = end_date
    
    if next_token:
        params["next_token"] = next_token
    
    headers = {
        "x-api-key": PERMUTABLE_API_KEY,
    }
    
    max_retries = 5
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                PERMUTABLE_BASE_URL, 
                params=params, 
                headers=headers, 
                timeout=120
            )
            
            if response.status_code == 429:
                wait_time = retry_delay * (attempt + 1)
                print(f"\n    Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            if response.status_code == 403:
                # Sometimes 403 is returned due to rate limiting
                wait_time = retry_delay * (attempt + 1)
                if attempt < max_retries - 1:
                    print(f"\n    Got 403, waiting {wait_time}s and retrying...")
                    time.sleep(wait_time)
                    continue
                print(f"\n    Error 403: Access forbidden after retries")
                return {}
            
            if response.status_code != 200:
                print(f"\n    Error {response.status_code}: {response.text[:200]}")
                return {}
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"\n    Request error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return {}
    
    return {}


def fetch_all_sentiment_data(start_date: str = DEFAULT_START_DATE, end_date: str = None, limit: int = DEFAULT_LIMIT, max_pages: int = None, index_type: str = DEFAULT_INDEX_TYPE) -> list:
    """
    Fetch all sentiment data with pagination.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format (optional)
        limit: Records per page
        max_pages: Maximum number of pages to fetch (None for unlimited)
        index_type: Index type - INTERNATIONAL or DOMESTIC
        
    Returns:
        List of all data records
    """
    print("\n" + "=" * 60)
    print("FETCHING SENTIMENT DATA")
    print("=" * 60)
    print(f"Index type: {index_type}")
    print(f"Start date: {start_date}")
    print(f"End date: {end_date if end_date else 'not specified'}")
    print(f"Limit per page: {limit}")
    print(f"Max pages: {max_pages if max_pages else 'unlimited'}")
    print(f"API: Permutable AI Macro Regional")
    print("-" * 60)
    
    all_data = []
    next_token = None
    page_num = 0
    
    while True:
        page_num += 1
        
        # Check max pages limit
        if max_pages and page_num > max_pages:
            print(f"Reached max pages limit ({max_pages}). Stopping.")
            break
        
        token_preview = f" (token: {next_token[:30]}...)" if next_token else ""
        print(f"Page {page_num}{token_preview}...", end=" ", flush=True)
        
        response = fetch_sentiment_page(start_date, end_date, limit, next_token, index_type)
        
        if not response:
            print("Failed")
            break
        
        # Extract data from response
        data = response.get("data", [])
        records_count = len(data)
        all_data.extend(data)
        
        has_more = response.get("has_more", False)
        print(f"Got {records_count} records (total: {len(all_data)}, more: {has_more})")
        
        # Check for next page
        next_token = response.get("next_token")
        
        if not next_token or not has_more:
            print("Pagination complete.")
            break
        
        # Delay between requests to avoid rate limiting
        time.sleep(1.5)
    
    print("-" * 60)
    print(f"Total records fetched: {len(all_data)}")
    
    return all_data


# ============================================================================
# Data Processing
# ============================================================================

def get_output_file(index_type: str) -> Path:
    """Get the output file path for the given index type."""
    if index_type == "DOMESTIC":
        return BASE_PATH / "sentiment_data_domestic.csv"
    return BASE_PATH / "sentiment_data.csv"


def get_latest_date_from_csv(index_type: str) -> str | None:
    """
    Read existing CSV and return the latest date.
    
    Args:
        index_type: Index type - INTERNATIONAL or DOMESTIC
        
    Returns:
        Latest date as string (YYYY-MM-DD) or None if file doesn't exist
    """
    output_file = get_output_file(index_type)
    
    if not output_file.exists():
        return None
    
    try:
        df = pd.read_csv(output_file, usecols=['date'], nrows=100)
        if df.empty:
            return None
        return df['date'].max()
    except Exception as e:
        print(f"Error reading {output_file}: {e}")
        return None


def load_existing_data(index_type: str) -> pd.DataFrame:
    """
    Load existing sentiment data from CSV.
    
    Args:
        index_type: Index type - INTERNATIONAL or DOMESTIC
        
    Returns:
        DataFrame with existing data, or empty DataFrame if file doesn't exist
    """
    output_file = get_output_file(index_type)
    
    if not output_file.exists():
        return pd.DataFrame()
    
    try:
        return pd.read_csv(output_file)
    except Exception as e:
        print(f"Error reading {output_file}: {e}")
        return pd.DataFrame()


def merge_sentiment_data(existing_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge new sentiment data with existing data, replacing overlapping date+topic combinations.
    
    Args:
        existing_df: Existing DataFrame from CSV
        new_df: New DataFrame from API
        
    Returns:
        Merged DataFrame with new data taking precedence for duplicates
    """
    if existing_df.empty:
        return new_df
    if new_df.empty:
        return existing_df
    
    # Get the minimum date from new data - we'll replace all data from that date forward
    new_min_date = new_df['date'].min()
    
    # Keep existing data that is BEFORE the new data's min date
    existing_before = existing_df[existing_df['date'] < new_min_date].copy()
    
    print(f"  Keeping {len(existing_before)} existing rows (before {new_min_date})")
    print(f"  Adding {len(new_df)} new rows (from {new_min_date})")
    
    # Combine: old data + new data
    combined = pd.concat([existing_before, new_df], ignore_index=True)
    
    # Sort by date (descending) then topic
    combined = combined.sort_values(['date', 'topic'], ascending=[False, True])
    
    return combined


def process_sentiment_data(raw_data: list) -> pd.DataFrame:
    """
    Process raw sentiment data into efficient wide-format DataFrame.
    
    Structure: Rows = date + topic, Columns = countries (with _avg and _count suffixes)
    This is efficient because topics are the same across all countries.
    
    Args:
        raw_data: List of records from API
        
    Returns:
        Processed DataFrame
    """
    print("\n" + "=" * 60)
    print("PROCESSING DATA")
    print("=" * 60)
    
    if not raw_data:
        print("No data to process")
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(raw_data)
    
    print(f"Raw records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Extract date from publication_time
    df['date'] = pd.to_datetime(df['publication_time']).dt.strftime('%Y-%m-%d')
    
    # Get unique values
    countries = sorted(df['country'].unique())
    topics = sorted(df['topic_name'].unique())
    dates = sorted(df['date'].unique())
    
    print(f"Countries: {len(countries)}")
    print(f"Topics: {len(topics)} - {topics}")
    print(f"Date range: {dates[0]} to {dates[-1]} ({len(dates)} dates)")
    
    # Create pivot tables for sentiment_avg and headline_count
    # This creates an efficient structure: rows = date+topic, columns = countries
    
    pivot_avg = df.pivot_table(
        index=['date', 'topic_name'],
        columns='country',
        values='sentiment_avg',
        aggfunc='mean'
    )
    
    pivot_count = df.pivot_table(
        index=['date', 'topic_name'],
        columns='country',
        values='headline_count',
        aggfunc='sum'
    )
    
    # Rename columns with suffixes
    pivot_avg.columns = [f"{col}_sentiment" for col in pivot_avg.columns]
    pivot_count.columns = [f"{col}_count" for col in pivot_count.columns]
    
    # Combine the two pivot tables
    combined = pd.concat([pivot_avg, pivot_count], axis=1)
    
    # Sort columns: group by country (sentiment, count for each)
    country_cols = []
    for country in countries:
        sent_col = f"{country}_sentiment"
        count_col = f"{country}_count"
        if sent_col in combined.columns:
            country_cols.append(sent_col)
        if count_col in combined.columns:
            country_cols.append(count_col)
    
    combined = combined[country_cols]
    
    # Reset index to make date and topic regular columns
    combined = combined.reset_index()
    combined = combined.rename(columns={'topic_name': 'topic'})
    
    # Sort by date (descending) then topic
    combined = combined.sort_values(['date', 'topic'], ascending=[False, True])
    
    print(f"Processed DataFrame: {len(combined)} rows x {len(combined.columns)} columns")
    
    return combined


def save_sentiment_data(df: pd.DataFrame, index_type: str = DEFAULT_INDEX_TYPE) -> Path:
    """
    Save processed sentiment data to CSV.
    
    Args:
        df: Processed DataFrame
        index_type: Index type - determines output filename
        
    Returns:
        Path to saved file
    """
    output_file = get_output_file(index_type)
    
    if df.empty:
        print("No data to save")
        return output_file
    
    # Round numeric columns for cleaner output
    numeric_cols = df.select_dtypes(include=['float64']).columns
    df[numeric_cols] = df[numeric_cols].round(4)
    
    df.to_csv(output_file, index=False)
    
    print("\n" + "=" * 60)
    print("SAVED OUTPUT")
    print("=" * 60)
    print(f"File: {output_file.name}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    
    # Show structure info
    print("\nCSV Structure:")
    print("  - Rows: date + topic combinations")
    print("  - Columns: country_sentiment and country_count for each country")
    
    # Preview columns
    cols = list(df.columns)
    print(f"\nFirst 6 columns: {cols[:6]}")
    if len(cols) > 10:
        print(f"... and {len(cols) - 6} more country columns")
    
    return output_file


# ============================================================================
# Update Functions
# ============================================================================

def update_sentiment_file(index_type: str, limit: int = DEFAULT_LIMIT) -> bool:
    """
    Incrementally update a sentiment data file to today.
    
    Args:
        index_type: Index type - INTERNATIONAL or DOMESTIC
        limit: Records per API page
        
    Returns:
        True if update was successful
    """
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = get_output_file(index_type)
    
    print("\n" + "=" * 60)
    print(f"UPDATING {index_type} SENTIMENT DATA")
    print("=" * 60)
    print(f"Output file: {output_file.name}")
    print(f"Target date: {today}")
    
    # Get latest date from existing file
    latest_date = get_latest_date_from_csv(index_type)
    
    if latest_date is None:
        print(f"No existing data found. Will do full fetch from {DEFAULT_START_DATE}")
        start_date = DEFAULT_START_DATE
    elif latest_date >= today:
        print(f"Data is already up to date (latest: {latest_date})")
        return True
    else:
        # Start from the latest date to ensure we get any updates for that day too
        start_date = latest_date
        print(f"Existing data up to: {latest_date}")
        print(f"Fetching from: {start_date} to {today}")
    
    # Fetch new data with explicit date range (start_date to today)
    raw_data = fetch_all_sentiment_data(start_date, end_date=today, limit=limit, max_pages=None, index_type=index_type)
    
    if not raw_data:
        print("\nNo new data retrieved.")
        return False
    
    # Process new data
    new_df = process_sentiment_data(raw_data)
    
    if new_df.empty:
        print("No new data to add.")
        return True
    
    # Load existing data and merge
    existing_df = load_existing_data(index_type)
    
    print("\n" + "-" * 60)
    print("MERGING DATA")
    print("-" * 60)
    
    merged_df = merge_sentiment_data(existing_df, new_df)
    
    # Save merged data
    save_sentiment_data(merged_df, index_type)
    
    return True


def update_all_sentiment_files(limit: int = DEFAULT_LIMIT):
    """
    Update both INTERNATIONAL and DOMESTIC sentiment files to today.
    
    Args:
        limit: Records per API page
    """
    print("=" * 60)
    print("UPDATING ALL SENTIMENT DATA FILES")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Update INTERNATIONAL
    success_intl = update_sentiment_file("INTERNATIONAL", limit)
    
    # Update DOMESTIC
    success_dom = update_sentiment_file("DOMESTIC", limit)
    
    print("\n" + "=" * 60)
    print("UPDATE SUMMARY")
    print("=" * 60)
    print(f"INTERNATIONAL: {'Success' if success_intl else 'Failed'}")
    print(f"DOMESTIC: {'Success' if success_dom else 'Failed'}")
    print("=" * 60)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point."""
    # Parse command line arguments
    start_date = DEFAULT_START_DATE
    end_date = None  # None means no end date restriction
    limit = DEFAULT_LIMIT
    max_pages = DEFAULT_MAX_PAGES
    index_type = DEFAULT_INDEX_TYPE
    update_mode = False
    update_all_mode = False
    
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--start" and i + 1 < len(args):
            start_date = args[i + 1]
        elif arg == "--end" and i + 1 < len(args):
            end_date = args[i + 1]
        elif arg == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
        elif arg == "--max-pages" and i + 1 < len(args):
            max_pages = int(args[i + 1])
        elif arg == "--index-type" and i + 1 < len(args):
            index_type = args[i + 1].upper()
        elif arg == "--update":
            update_mode = True
        elif arg == "--update-all":
            update_all_mode = True
    
    # Handle update modes
    if update_all_mode:
        update_all_sentiment_files(limit)
        print("\n" + "=" * 60)
        print("DONE!")
        print("=" * 60)
        return
    
    if update_mode:
        update_sentiment_file(index_type, limit)
        print("\n" + "=" * 60)
        print("DONE!")
        print("=" * 60)
        return
    
    # Full fetch mode (original behavior)
    print("=" * 60)
    print("SENTIMENT DATA FETCHER")
    print("=" * 60)
    print(f"Index Type: {index_type}")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date if end_date else 'not specified'}")
    print(f"Page Limit: {limit}")
    print(f"Max Pages: {max_pages if max_pages else 'unlimited'}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fetch all data with pagination
    raw_data = fetch_all_sentiment_data(start_date, end_date, limit, max_pages, index_type)
    
    if not raw_data:
        print("\nNo data retrieved. Exiting.")
        return
    
    # Process into efficient format
    processed_df = process_sentiment_data(raw_data)
    
    # Save to CSV
    save_sentiment_data(processed_df, index_type)
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
