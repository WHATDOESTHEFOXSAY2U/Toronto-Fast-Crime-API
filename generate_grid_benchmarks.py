import sqlite3
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# Configuration
DB_NAME = "crime_data.db"
GRID_RESOLUTION_KM = 0.2  # 200m grid resolution (High Granularity)
RADIUS_KM = 0.8           # 800m radius for scoring
BENCHMARK_FILE = "benchmarks.json"

# Weights (Must match scoring.py exactly)
WEIGHTS = {
    'Homicide': 100,
    'Shooting': 50,
    'Assault': 15,
    'Robbery': 10,
    'Break and Enter': 8,
    'Auto Theft': 6,
    'Theft Over': 4,
    'Theft From Motor Vehicle': 3,
    'Bicycle Theft': 2,
    'NonMCI': 2, 
    'Other': 1
}

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def calculate_raw_score(df, lat, lon, radius_km):
    """
    Calculates raw weighted risk score for a point with exponential time decay.
    """
    # Optimization: Pre-filter by bounding box (approx 1 degree lat ~ 111km)
    # 0.8km radius ~ 0.008 degrees. Let's use 0.01 for safety.
    lat_delta = 0.01
    lon_delta = 0.015 # slightly larger for longitude at this latitude
    
    # Fast filtering using numpy boolean indexing (faster than pandas query for this loop)
    # Assuming df is passed as a subset or we do it here. 
    # Actually, passing the full DF and doing boolean indexing is fast enough if we limit the scope.
    
    subset = df[
        (df['lat'] >= lat - lat_delta) & 
        (df['lat'] <= lat + lat_delta) & 
        (df['lon'] >= lon - lon_delta) & 
        (df['lon'] <= lon + lon_delta)
    ].copy()
    
    if subset.empty:
        return 0, {}

    # Haversine distance calculation
    R = 6371
    dlat = np.radians(subset['lat'] - lat)
    dlon = np.radians(subset['lon'] - lon)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat)) * np.cos(np.radians(subset['lat'])) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distances = R * c
    
    # Filter by radius
    mask = distances <= radius_km
    nearby = subset[mask].copy()
    
    if nearby.empty:
        return 0, {}
        
    # Exponential Time Decay: weight = e^(-0.15 * years)
    nearby['years_old'] = nearby['days_old'] / 365.25
    nearby['time_factor'] = np.exp(-0.15 * nearby['years_old'])
    
    # Calculate Score
    nearby['score'] = nearby['weight'] * nearby['time_factor']
    total_score = nearby['score'].sum()
    
    # Category-specific scores
    cat_scores = nearby.groupby('category')['score'].sum().to_dict()
    
    return total_score, cat_scores

def generate_benchmarks():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Benchmark Generation (High Res)...")
    
    conn = get_db_connection()
    # Load last 1 year of data for benchmarking (Requested by User)
    query = "SELECT date, category, lat, lon FROM crimes WHERE date >= date('now', '-1 year')"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("CRITICAL ERROR: No data found in database!")
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded {len(df)} crime records (Last 1 Year).")

    # Pre-process Data
    df['date'] = pd.to_datetime(df['date'], format='mixed', utc=True)
    now = pd.Timestamp.now(tz='UTC')
    df['days_old'] = (now - df['date']).dt.days
    df['weight'] = df['category'].map(WEIGHTS).fillna(1)
    
    # Define Toronto Bounding Box
    min_lat, max_lat = 43.58, 43.85
    min_lon, max_lon = -79.64, -79.12
    
    # Generate Grid Points
    lat_step = GRID_RESOLUTION_KM / 111.0
    lon_step = GRID_RESOLUTION_KM / (111.0 * np.cos(np.radians(43.7)))
    
    lats = np.arange(min_lat, max_lat, lat_step)
    lons = np.arange(min_lon, max_lon, lon_step)
    
    grid_points = [(lat, lon) for lat in lats for lon in lons]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generated {len(grid_points)} grid points (0.2km resolution).")
    
    raw_scores = []
    category_scores = {cat: [] for cat in WEIGHTS.keys()}
    
    # Calculate scores for every grid point
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Calculating risk scores for all grid points...")
    
    for i, (lat, lon) in enumerate(grid_points):
        if i > 0 and i % 500 == 0: 
            print(f"  Processed {i}/{len(grid_points)} points...")
        
        # Optimization: Pre-filter DF to bounding box of point + radius to speed up distance calc
        # (Optional but good for performance if dataset is huge)
        
        score, cat_breakdown = calculate_raw_score(df, lat, lon, RADIUS_KM)
        
        # Only include non-zero scores in the distribution? 
        # Ideally yes, because "0 crime" is a special case (100% safe).
        # But for "Safer Than X%", we need to know how many places have 0 crime too.
        # So we include ALL scores.
        raw_scores.append(score)
        
        for cat in WEIGHTS.keys():
            val = cat_breakdown.get(cat, 0)
            category_scores[cat].append(val)
                
    # Sort for percentile calculation
    raw_scores.sort()
    for cat in category_scores:
        category_scores[cat].sort()

    # Create Benchmark Object
    benchmarks = {
        "generated_at": datetime.now().isoformat(),
        "metadata": {
            "grid_resolution_km": GRID_RESOLUTION_KM,
            "radius_km": RADIUS_KM,
            "total_points": len(grid_points),
            "data_records": len(df)
        },
        "overall_distribution": raw_scores,
        "by_category": category_scores
    }
    
    # Save to JSON
    with open(BENCHMARK_FILE, 'w') as f:
        json.dump(benchmarks, f)
        
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Success! Benchmarks saved to {BENCHMARK_FILE}")
    print(f"  Min Score: {min(raw_scores):.2f}")
    print(f"  Median Score: {np.median(raw_scores):.2f}")
    print(f"  Max Score: {max(raw_scores):.2f}")

if __name__ == "__main__":
    generate_benchmarks()
