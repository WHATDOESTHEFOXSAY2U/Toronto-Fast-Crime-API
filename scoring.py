"""
Scoring Logic for Toronto Crime API.

This module handles the calculation of Crime Risk Scores based on:
1. Proximity: Crimes within a 0.8km radius.
2. Severity: Weighted scores for different crime types.
3. Recency: Non-linear time decay (1 / (1 + years)).
4. Relativity: Scores are percentiles relative to city-wide distribution.
"""

import sqlite3
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import forecasting
import warnings

# Suppress statsmodels warnings for short series
warnings.filterwarnings("ignore")

DB_NAME = "crime_data.db"

# Weights for different crime categories
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
    """Establishes connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def load_benchmarks():
    """Loads pre-calculated benchmarks from JSON."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bench_path = os.path.join(base_dir, "benchmarks.json")
        with open(bench_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}

BENCHMARKS = load_benchmarks()

def percentile_to_safety_score(percentile):
    """
    Maps a percentile (0-100) to a safety score (0-100) using a non-linear curve.
    
    Rationale:
    - Crime is heavily concentrated in specific hotspots.
    - The vast majority (e.g., bottom 80%) of the city is relatively safe.
    - Being in the 50th percentile of risk in Toronto is still "Safe".
    
    Mapping:
    - 0-50th Percentile Risk  -> 90-100 Safety (Very Safe)
    - 50-80th Percentile Risk -> 70-90 Safety (Safe)
    - 80-95th Percentile Risk -> 40-70 Safety (Moderate)
    - 95-100th Percentile Risk -> 0-40 Safety (Low Safety)
    """
    if percentile <= 50:
        # 0-50 maps to 90-100
        # Formula: 100 - (percentile / 50) * 10
        return 100 - (percentile / 50) * 10
        
    elif percentile <= 80:
        # 50-80 maps to 70-90
        # Range is 30 percentile points mapping to 20 score points
        # Start at 90, go down to 70
        progress = (percentile - 50) / 30
        return 90 - (progress * 20)
        
    elif percentile <= 95:
        # 80-95 maps to 40-70
        # Range is 15 percentile points mapping to 30 score points
        progress = (percentile - 80) / 15
        return 70 - (progress * 30)
        
    else:
        # 95-100 maps to 0-40
        # Range is 5 percentile points mapping to 40 score points
        progress = (percentile - 95) / 5
        return 40 - (progress * 40)

def calculate_percentile_score(raw_score, distribution):
    """
    Calculates percentile and converts to safety score.
    Returns tuple: (safety_score, percentile)
    """
    if not distribution:
        return 50, 50  # Default if no data
        
    if raw_score <= 0:
        return 100, 0  # Zero crime = safest = 0th percentile
        
    # Find position in the distribution
    import bisect
    idx = bisect.bisect_left(distribution, raw_score)
    percentile = (idx / len(distribution)) * 100
    
    safety_score = percentile_to_safety_score(percentile)
    
    return round(safety_score, 1), round(percentile, 1)

# ... (keep calculate_forecast as is) ...

from functools import lru_cache

@lru_cache(maxsize=1024)
def calculate_score(lat, lon, radius_km=0.8):
    """
    Calculates the crime risk score for a given coordinate using relative benchmarking.
    """
    conn = get_db_connection()
    
    # Bounding box query
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * np.cos(np.radians(lat)))
    
    min_lat, max_lat = lat - lat_delta, lat + lat_delta
    min_lon, max_lon = lon - lon_delta, lon + lon_delta
    
    # Get last 10 years for history, but we'll filter for current score
    query = f'''
        SELECT date, category, type, lat, lon, premises_type, neighbourhood
        FROM crimes
        WHERE lat BETWEEN ? AND ?
          AND lon BETWEEN ? AND ?
          AND date >= date('now', '-10 years')
    '''
    
    df = pd.read_sql_query(query, conn, params=(min_lat, max_lat, min_lon, max_lon))
    conn.close()
    
    # Base response
    response = {
        "current_score": 100,
        "overall_percentile": 0,
        "history": [],
        "category_breakdown": {},
        "insights": {},
        "temporal_breakdown": {"day_safety_score": 100, "night_safety_score": 100},
        "risk_tags": {"negative": [], "positive": []},
        "benchmark": {"status": "N/A", "city_percentile": 0, "city_average_score": 50},
        "forecast": {}
    }

    if df.empty:
        return response
        
    # Filter by exact distance
    R = 6371
    dlat = np.radians(df['lat'] - lat)
    dlon = np.radians(df['lon'] - lon)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat)) * np.cos(np.radians(df['lat'])) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    df['distance'] = R * c
    
    df = df[df['distance'] <= radius_km].copy()
    
    if df.empty:
        return response

    # Pre-processing
    df['date'] = pd.to_datetime(df['date'], format='mixed', utc=True)
    now = pd.Timestamp.now(tz='UTC')
    df['days_old'] = (now - df['date']).dt.days
    df['weight'] = df['category'].map(WEIGHTS).fillna(1)
    
    # --- 1. Current Score (Last 1 Year) ---
    # UPDATED: Using 1 year window to match benchmarks
    df_current = df[df['days_old'] <= 365].copy()
    
    if not df_current.empty:
        df_current['years_old'] = df_current['days_old'] / 365.25
        # Exponential time decay
        df_current['time_factor'] = np.exp(-0.15 * df_current['years_old'])
        df_current['score'] = df_current['weight'] * df_current['time_factor']
        
        total_raw_risk = df_current['score'].sum()
        
        # Calculate Relative Score with percentile
        overall_dist = BENCHMARKS.get("overall_distribution", [])
        safety_score, overall_percentile = calculate_percentile_score(total_raw_risk, overall_dist)
        response["current_score"] = safety_score
        response["overall_percentile"] = overall_percentile
    else:
        response["current_score"] = 100
        response["overall_percentile"] = 0

    # --- 2. History (10 Years) ---
    history = []
    current_year = now.year
    
    for i in range(10):
        start_days = i * 365
        end_days = (i + 1) * 365
        year_label = str(current_year - i)
        
        year_df = df[(df['days_old'] >= start_days) & (df['days_old'] < end_days)].copy()
        
        if year_df.empty:
            year_safety = 100
            incident_count = 0
        else:
            # For history, we calculate raw risk for that year (no time decay within the year snapshot)
            year_df['score'] = year_df['weight']
            year_raw_risk = year_df['score'].sum()
            
            # Get safety score (ignore percentile for history)
            year_safety, _ = calculate_percentile_score(year_raw_risk, BENCHMARKS.get("overall_distribution", []))
            incident_count = len(year_df)
            
        history.append({
            "year": year_label,
            "safety_score": year_safety,
            "incident_count": incident_count
        })
        
    response["history"] = history
    
    # --- 3. Forecast (Multi-Model Selection) ---
    history_chronological = sorted(history, key=lambda x: int(x['year']))
    response["forecast"] = forecasting.select_best_forecast(history_chronological)
    
    # --- 4. Category Breakdown ---
    # Using the current 2-year window data
    if not df_current.empty:
        cat_dists = BENCHMARKS.get("by_category", {})
        
        for cat in WEIGHTS.keys():
            cat_df = df_current[df_current['category'] == cat]
            count = len(cat_df)
            
            if count == 0:
                continue
                
            cat_raw_risk = cat_df['score'].sum()
            cat_dist = cat_dists.get(cat, [])
            
            # Get category-specific safety score and percentile
            cat_safety, cat_percentile = calculate_percentile_score(cat_raw_risk, cat_dist)
            
            # Calculate city average incidents for this category
            if cat_dist:
                non_zero_cat = [x for x in cat_dist if x > 0]
                city_avg_raw = np.median(non_zero_cat) if non_zero_cat else 0
                # Rough estimate: raw score / weight / avg_time_factor -> count
                avg_time_factor = 0.9  # Approximate
                city_avg_incidents = int(city_avg_raw / WEIGHTS[cat] / avg_time_factor) if WEIGHTS[cat] > 0 else 0
            else:
                city_avg_incidents = 0
            
            # Trend
            recent_mask = cat_df['days_old'] <= 365
            prev_mask = (cat_df['days_old'] > 365) & (cat_df['days_old'] <= 730)
            recent_count = len(cat_df[recent_mask])
            prev_count = len(cat_df[prev_mask])
            
            trend = "Stable"
            if prev_count == 0:
                trend = "Up" if recent_count > 0 else "Stable"
            else:
                change = (recent_count - prev_count) / prev_count
                if change > 0.2: trend = "Up"
                elif change < -0.2: trend = "Down"
                
            # Subtypes
            top_subtypes = []
            subtype_counts = cat_df['type'].value_counts().head(3)
            for subtype, st_count in subtype_counts.items():
                top_subtypes.append({"type": subtype, "count": int(st_count)})
                
            response["category_breakdown"][cat] = {
                "safety_score": cat_safety,
                "category_percentile": cat_percentile,
                "incident_count": count,
                "city_avg_incidents": city_avg_incidents,
                "trend": trend,
                "weighted_impact": round(cat_raw_risk, 1), # Using raw risk as impact
                "top_subtypes": top_subtypes
            }
            
    # --- 5. Insights ---
    if not df_current.empty:
        # Safety Clock (Hourly)
        try:
            df_current['local_date'] = df_current['date'].dt.tz_convert('America/Toronto')
            df_current['hour'] = df_current['local_date'].dt.hour
            df_current['month'] = df_current['local_date'].dt.month
            df_current['dayofweek'] = df_current['local_date'].dt.dayofweek  # 0=Monday, 6=Sunday
        except:
            df_current['hour'] = df_current['date'].dt.hour
            df_current['month'] = df_current['date'].dt.month
            df_current['dayofweek'] = df_current['date'].dt.dayofweek
            
        hourly_counts = df_current.groupby('hour')['score'].sum().reindex(range(24), fill_value=0)
        max_hourly = hourly_counts.max()
        
        # Convert to safety scores (inverse of risk)
        if max_hourly > 0:
            hourly_risk_normalized = (hourly_counts / max_hourly * 100)
            safety_clock = (100 - hourly_risk_normalized).astype(int).tolist()
        else:
            safety_clock = [100] * 24
        
        # Weekly Pattern
        weekly_scores = []
        overall_dist = BENCHMARKS.get("overall_distribution", [])
        for day in range(7):  # 0=Monday, 6=Sunday
            day_df = df_current[df_current['dayofweek'] == day]
            if day_df.empty:
                weekly_scores.append(100)
            else:
                day_raw_risk = day_df['score'].sum()
                # Normalize by multiplying by 7 (it's 1/7th of week)
                day_safety, _ = calculate_percentile_score(day_raw_risk * 7, overall_dist)
                weekly_scores.append(day_safety)
        
        # Monthly Pattern
        monthly_counts = df_current.groupby('month')['score'].sum().reindex(range(1, 13), fill_value=0)
        max_monthly = monthly_counts.max()
        
        if max_monthly > 0:
            monthly_risk_normalized = (monthly_counts / max_monthly * 100)
            monthly_pattern = (100 - monthly_risk_normalized).astype(int).tolist()
        else:
            monthly_pattern = [100] * 12
        
        # Peak Hour (single)
        peak_hour_idx = hourly_counts.idxmax()
        peak_hour_str = datetime.now().replace(hour=peak_hour_idx, minute=0).strftime("%-I%p").lower()
        
        # Peak Time Range (3-hour window with highest risk)
        min_avg_safety = float('inf')
        peak_start = 0
        for i in range(24):
            window_safety = [
                safety_clock[i],
                safety_clock[(i+1) % 24],
                safety_clock[(i+2) % 24]
            ]
            avg_safety = sum(window_safety) / 3
            if avg_safety < min_avg_safety:
                min_avg_safety = avg_safety
                peak_start = i
        
        peak_end = (peak_start + 3) % 24
        if peak_end == 0:
            peak_time_range = f"{peak_start}:00-12:00am"
        else:
            peak_time_range = f"{peak_start}:00-{peak_end}:00"
        
        # Primary Risk
        primary_risk = "None"
        max_risk = 0
        for cat, data in response["category_breakdown"].items():
            if data['weighted_impact'] > max_risk:
                max_risk = data['weighted_impact']
                primary_risk = cat
                
        response["insights"] = {
            "safety_clock": safety_clock,
            "monthly_pattern": monthly_pattern,
            "weekly_pattern": weekly_scores,
            "peak_hour": peak_hour_str,
            "peak_time_range": peak_time_range,
            "primary_risk": primary_risk,
            "neighbourhood": df_current['neighbourhood'].mode()[0] if not df_current['neighbourhood'].empty else "Unknown",
            "premises_breakdown": df_current['premises_type'].value_counts().head(5).to_dict()
        }
        
        # Temporal Breakdown
        day_mask = (df_current['hour'] >= 6) & (df_current['hour'] < 18)
        night_mask = ~day_mask
        
        day_risk = df_current[day_mask]['score'].sum()
        night_risk = df_current[night_mask]['score'].sum()
        
        # Normalize temporal risk against overall distribution
        day_safety, _ = calculate_percentile_score(day_risk * 2, BENCHMARKS.get("overall_distribution", []))
        night_safety, _ = calculate_percentile_score(night_risk * 2, BENCHMARKS.get("overall_distribution", []))
        
        response["temporal_breakdown"] = {
            "day_safety_score": day_safety,
            "night_safety_score": night_safety
        }
        
    # --- 6. Risk Tags ---
    tags = []
    current_score = response["current_score"]
    
    if current_score >= 80:
        tags.append("High Safety Area")
    elif current_score <= 40:
        tags.append("High Crime Area")
        
    if response["temporal_breakdown"]["night_safety_score"] < response["temporal_breakdown"]["day_safety_score"] - 20:
        tags.append("Nighttime Risk")
        
    # Category specific tags
    for cat, data in response["category_breakdown"].items():
        if data["safety_score"] < 50:
            tags.append(f"High {cat}")
            
    response["risk_tags"] = {
        "negative": [t for t in tags if "High" in t or "Risk" in t],
        "positive": [t for t in tags if "Safe" in t]
    }
    
    # --- 7. Benchmark ---
    percentile = 100 - current_score # Reverse safety score to get risk percentile
    
    status = "Moderate Safety"
    if current_score >= 90: status = "Very High Safety"
    elif current_score >= 80: status = "High Safety"
    elif current_score >= 60: status = "Moderate Safety"
    elif current_score >= 40: status = "Low Safety"
    else: status = "Very Low Safety"
    
    response["benchmark"] = {
        "city_percentile": int(percentile),
        "city_average_score": 50, # Median of distribution is by definition 50th percentile
        "status": status
    }
    
    return response
