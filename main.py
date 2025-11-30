"""
Toronto Crime API Server.

This FastAPI application provides endpoints to query crime risk scores
for Toronto postal codes.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pgeocode
import scoring
import uvicorn

app = FastAPI(
    title="Toronto Crime API",
    description="API for calculating crime risk scores based on Toronto Police data.",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nomi = pgeocode.Nominatim('ca')

@app.get("/")
def read_root():
    """Root endpoint providing basic usage information."""
    return {"message": "Welcome to the Toronto Crime API. Use /score?pincode=M5V2T6 to get a crime score."}

@app.get("/score")
def get_score(pincode: str = Query(..., description="Toronto Postal Code (e.g., M5V2T6)")):
    """
    Calculate the crime risk score for a given postal code.

    Args:
        pincode (str): Canadian postal code (e.g., 'M5V 2T6').

    Returns:
        dict: JSON response containing coordinates, total score, trend, and breakdown.

    Raises:
        HTTPException: If the postal code is invalid or coordinates cannot be found.
    """
    # Validate and get coordinates
    pincode = pincode.replace(" ", "").upper()
    
    # pgeocode requires first 3 chars for Canada usually, but let's see if it handles full 6 chars
    # pgeocode 'ca' dataset is indexed by FSA (first 3 chars) usually.
    # Let's try with full pincode, if nan, try first 3.
    
    info = nomi.query_postal_code(pincode)
    
    if str(info.latitude) == 'nan':
        # Try FSA
        if len(pincode) > 3:
             info = nomi.query_postal_code(pincode[:3])
    
    if str(info.latitude) == 'nan':
        raise HTTPException(status_code=400, detail="Invalid postal code or coordinates not found.")
        
    lat = info.latitude
    lon = info.longitude
    
    # Calculate score
    result = scoring.calculate_score(lat, lon)
    
    # Merge result into response
    response = {
        "pincode": pincode,
        "coordinates": {"lat": lat, "lon": lon},
    }
    response.update(result)
    
    return response

@app.get("/score/coords")
def get_score_by_coords(
    lat: float = Query(..., description="Latitude (e.g., 43.6532)"),
    lon: float = Query(..., description="Longitude (e.g., -79.3832)")
):
    """
    Calculate the crime risk score for given latitude and longitude.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.

    Returns:
        dict: JSON response containing coordinates, total score, trend, and breakdown.
    """
    # Calculate score
    result = scoring.calculate_score(lat, lon)
    
    # Merge result into response
    response = {
        "pincode": "N/A", # No pincode for coord query
        "coordinates": {"lat": lat, "lon": lon},
    }
    response.update(result)
    
    return response

@app.get("/heatmap")
def get_heatmap():
    """
    Get crime data for heatmap visualization.
    Returns:
        list: List of [lat, lon, intensity]
    """
    data = scoring.get_heatmap_data()
    return data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
