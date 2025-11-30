"""
Data Ingestion Script for Toronto Crime API.

This script processes raw CSV and GeoJSON files from the 'data/' directory
and ingests them into a unified SQLite database 'crime_data.db'.
It also supports downloading fresh data from the Toronto Police Service Portal.
"""

import pandas as pd
import sqlite3
import glob
import json
import os
import dateutil.parser
import argparse
import requests
from datetime import datetime

DB_NAME = "crime_data.db"
DATA_DIR = "data"
METADATA_FILE = "metadata.json"

# --- Download Configuration ---

# Item IDs extracted from the portal
DATASETS = {
    "Shooting_and_Firearm_Discharges": "64ddeca12da34403869968ec725e23c4",
    "Homicides": "d96bf5b67c1c49879f354dad51cf81f9",
    "Assault": "b4d0398d37eb4aa184065ed625ddb922",
    "Auto_Theft": "95ab41aee16847dba8453bf1688249d6",
    "Bicycle_Thefts": "a89d10d5e28444ceb0c8d1d4c0ee39cc",
    "Break_and_Enter": "040ead448df2412da252cfbb532e77ac",
    "Robbery": "d0e1e98de5f945faa2fe635dee3f4062",
    "Theft_From_Motor_Vehicle": "d9303bc20f8a4351b7744a8703eecb80",
    "Theft_Over": "7530d9b637c340059ccb81a782481c04"
}

# --- Ingestion Configuration ---

# Mapping for filenames to categories if not explicit
CATEGORY_MAPPING = {
    'assault': 'Assault',
    'auto_theft': 'Auto Theft',
    'bicycle': 'Bicycle Theft',
    'break_and_enter': 'Break and Enter',
    'homicide': 'Homicide',
    'robbery': 'Robbery',
    'shooting': 'Shooting',
    'theft_from_motor_vehicle': 'Theft From Motor Vehicle',
    'theft_over': 'Theft Over',
    'hate_crime': 'Hate Crime'
}

# --- Download Functions ---

def get_service_url(item_id):
    """Fetches the Feature Service URL from the ArcGIS Item ID."""
    try:
        url = f"https://www.arcgis.com/sharing/rest/content/items/{item_id}?f=json"
        res = requests.get(url)
        data = res.json()
        return data.get("url")
    except Exception as e:
        print(f"Error fetching metadata for {item_id}: {e}")
        return None

def download_csv(name, service_url):
    """Downloads the dataset as CSV from the Feature Service using pagination."""
    if not service_url:
        return None
    
    print(f"Downloading {name} from {service_url}...")
    
    all_features = []
    offset = 0
    record_count = 2000 # Standard ArcGIS limit
    
    while True:
        # Construct query URL for GeoJSON with pagination
        query_url = f"{service_url}/0/query?where=1%3D1&outFields=*&resultOffset={offset}&resultRecordCount={record_count}&f=geojson"
        
        try:
            res = requests.get(query_url)
            if res.status_code != 200:
                print(f"Failed chunk at offset {offset}: {res.status_code}")
                break
                
            data = res.json()
            features = data.get('features', [])
            
            if not features:
                break
                
            all_features.extend(features)
            
            # Check if we've reached the end
            if len(features) < record_count:
                break
                
            offset += len(features)
            print(f"  Fetched {offset} records...")
            
        except Exception as e:
            print(f"Error downloading chunk for {name}: {e}")
            break
            
    if not all_features:
        print(f"No data found for {name}")
        return None
        
    # Convert to DataFrame
    try:
        # Extract properties from features
        rows = [f['properties'] for f in all_features]
        df = pd.DataFrame(rows)
        
        # Handle dates (ArcGIS uses milliseconds)
        for col in df.columns:
            if 'DATE' in col or 'date' in col:
                # Check if numeric
                if pd.api.types.is_numeric_dtype(df[col]):
                     df[col] = pd.to_datetime(df[col], unit='ms', errors='coerce')
        
        # Save to CSV
        file_path = os.path.join(DATA_DIR, f"{name}.csv")
        df.to_csv(file_path, index=False)
        print(f"Saved {name}.csv ({len(df)} records)")
        return file_path
        
    except Exception as e:
        print(f"Error processing data for {name}: {e}")
        return None

def analyze_file(name, file_path):
    """Analyzes the CSV to extract date range and count."""
    try:
        df = pd.read_csv(file_path)
        
        # Identify date column
        date_col = None
        for col in ['OCC_DATE', 'OCC_date', 'REPORT_DATE', 'date']:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            return {
                "name": name,
                "file": os.path.basename(file_path),
                "count": len(df),
                "min_date": "Unknown",
                "max_date": "Unknown"
            }
            
        # Convert to datetime, handling errors
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        count = len(df)
        
        return {
            "name": name,
            "file": os.path.basename(file_path),
            "count": count,
            "min_date": min_date.strftime('%Y-%m-%d') if pd.notna(min_date) else "Unknown",
            "max_date": max_date.strftime('%Y-%m-%d') if pd.notna(max_date) else "Unknown"
        }
    except Exception as e:
        print(f"Error analyzing {name}: {e}")
        return None

def run_download():
    """Runs the full download process."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    metadata = {
        "last_refresh": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "datasets": []
    }
    
    global_min = None
    global_max = None
    
    for name, item_id in DATASETS.items():
        print(f"Processing {name}...")
        service_url = get_service_url(item_id)
        if service_url:
            file_path = download_csv(name, service_url)
            if file_path:
                info = analyze_file(name, file_path)
                if info:
                    metadata["datasets"].append(info)
                    
                    # Update global range
                    if info['min_date'] != 'Unknown':
                        d_min = datetime.strptime(info['min_date'], '%Y-%m-%d')
                        if global_min is None or d_min < global_min: global_min = d_min
                        
                    if info['max_date'] != 'Unknown':
                        d_max = datetime.strptime(info['max_date'], '%Y-%m-%d')
                        if global_max is None or d_max > global_max: global_max = d_max
                        
    if global_min and global_max:
        metadata["overall_range"] = {
            "start": global_min.strftime('%Y-%m-%d'),
            "end": global_max.strftime('%Y-%m-%d')
        }
        
    # Save metadata
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print("\n=== 📊 Download Summary ===")
    print(f"Last Refresh: {metadata['last_refresh']}")
    if "overall_range" in metadata:
        print(f"Overall Data Range: {metadata['overall_range']['start']} to {metadata['overall_range']['end']}")
    
    for ds in metadata["datasets"]:
        print(f"- {ds['name']}: {ds['min_date']} to {ds['max_date']} ({ds['count']} records)")

# --- Ingestion Functions ---

def get_db_connection():
    """Establishes connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def create_table(conn):
    """Creates the 'crimes' table if it does not exist."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_unique_id TEXT,
            date TEXT,
            lat REAL,
            lon REAL,
            category TEXT,
            type TEXT,
            premises_type TEXT,
            neighbourhood TEXT,
            source_file TEXT,
            UNIQUE(event_unique_id)
        )
    ''')
    
    # Create indices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lat ON crimes(lat)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lon ON crimes(lon)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON crimes(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lat_lon_date ON crimes(lat, lon, date)')
    
    conn.commit()

def parse_date(date_str):
    """Parses a date string into a datetime object."""
    try:
        return dateutil.parser.parse(date_str)
    except:
        return None

def ingest_csv(file_path, conn):
    """Reads and ingests a CSV file into the database."""
    print(f"Processing {file_path}...")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    records = []
    
    # Determine Category from filename as fallback
    base_name = os.path.basename(file_path).lower()
    file_category = "Other"
    for key, val in CATEGORY_MAPPING.items():
        if key in base_name:
            file_category = val
            break

    for _, row in df.iterrows():
        try:
            # Lat/Lon
            lat = row.get('LAT_WGS84')
            if pd.isna(lat): lat = row.get('Latitude')
            
            lon = row.get('LONG_WGS84')
            if pd.isna(lon): lon = row.get('Longitude')
            
            if pd.isna(lat) or pd.isna(lon) or lat == 0 or lon == 0:
                continue
                
            # Date
            date_str = row.get('OCC_DATE')
            if pd.isna(date_str): date_str = row.get('OCC_date')
            if pd.isna(date_str): date_str = row.get('REPORT_DATE')
            
            dt = parse_date(str(date_str))
            if dt is None:
                continue
                
            # Fix time using OCC_HOUR if available
            occ_hour = row.get('OCC_HOUR')
            if pd.notna(occ_hour):
                try:
                    dt = dt.replace(hour=int(occ_hour), minute=0, second=0)
                except:
                    pass

            # Category
            category = row.get('MCI_CATEGORY')
            if pd.isna(category) or category == 'NonMCI':
                category = file_category
                
            # Type
            crime_type = row.get('OFFENCE')
            if pd.isna(crime_type): crime_type = row.get('PRIMARY_OFFENCE')
            if pd.isna(crime_type): crime_type = category
            
            # Premises & Neighbourhood
            premises = row.get('PREMISES_TYPE')
            if pd.isna(premises): premises = "Unknown"
            
            hood = row.get('NEIGHBOURHOOD_158')
            if pd.isna(hood): hood = row.get('NEIGHBOURHOOD_140')
            if pd.isna(hood): hood = "Unknown"

            event_id = row.get('EVENT_UNIQUE_ID')
            if pd.isna(event_id): event_id = row.get('OBJECTID')

            records.append((
                str(event_id), str(dt), lat, lon, category, crime_type, 
                premises, hood, os.path.basename(file_path)
            ))
        except Exception as e:
            continue
    
    if records:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR IGNORE INTO crimes (event_unique_id, date, lat, lon, category, type, premises_type, neighbourhood, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', records)
        conn.commit()
        print(f"Inserted {len(records)} records from {file_path}")

def ingest_geojson(file_path, conn):
    """Reads and ingests a GeoJSON file into the database."""
    print(f"Processing {file_path}...")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    records = []
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        
        if geom.get('type') != 'Point':
            continue
            
        coords = geom.get('coordinates')
        if not coords or len(coords) < 2:
            continue
            
        lon, lat = coords[0], coords[1]
        
        date_str = props.get('OCC_DATE')
        dt = parse_date(str(date_str))
        
        category = props.get('HOMICIDE_TYPE')
        if not category: category = 'Homicide'
        
        crime_type = category
        event_id = props.get('EVENT_UNIQUE_ID')
        
        # GeoJSON usually lacks premises/hood in this dataset, default to Unknown
        premises = "Unknown"
        hood = props.get('NEIGHBOURHOOD_158', "Unknown")

        records.append((
            str(event_id), str(dt), lat, lon, category, crime_type, 
            premises, hood, os.path.basename(file_path)
        ))

    if records:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR IGNORE INTO crimes (event_unique_id, date, lat, lon, category, type, premises_type, neighbourhood, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', records)
        conn.commit()
        print(f"Inserted {len(records)} records from {file_path}")

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Ingest crime data into SQLite database.")
    parser.add_argument("--download", action="store_true", help="Download fresh data before ingestion")
    args = parser.parse_args()

    if args.download:
        print("🚀 Starting data download...")
        run_download()
        print("✅ Download complete.")

    conn = get_db_connection()
    create_table(conn)
    
    # Process CSVs
    for csv_file in glob.glob("data/*.csv"):
        ingest_csv(csv_file, conn)
        
    # Process GeoJSON
    for geo_file in glob.glob("data/*.geojson"):
        ingest_geojson(geo_file, conn)

    conn.close()
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
