#!/usr/bin/env python3
"""
Scrape business listings from Google Maps Places API (New).
Used for ICP prospecting to find potential customers.
"""
import sys
import json
import os
import requests
from pathlib import Path

def load_env():
    """Load .env file from current directory."""
    env_path = Path.cwd() / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def search_places(query: str, location: str, radius_miles: int = 25, max_results: int = 20) -> dict:
    """
    Search Google Maps Places API (New) for businesses.

    Args:
        query: Search query (e.g., "real estate agent", "insurance agency")
        location: City or address to center search
        radius_miles: Search radius in miles
        max_results: Maximum number of results to return

    Returns:
        Dictionary with businesses list
    """
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY not configured in .env"}

    # Step 1: Geocode the location to get coordinates
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    geocode_params = {
        "address": location,
        "key": api_key
    }

    try:
        geo_response = requests.get(geocode_url, params=geocode_params, timeout=10)
        geo_data = geo_response.json()

        if geo_data.get("status") != "OK" or not geo_data.get("results"):
            return {"error": f"Could not geocode location: {location}. Status: {geo_data.get('status')}"}

        lat = geo_data["results"][0]["geometry"]["location"]["lat"]
        lng = geo_data["results"][0]["geometry"]["location"]["lng"]
    except Exception as e:
        return {"error": f"Geocoding failed: {str(e)}"}

    # Step 2: Search using Places API (New) - Text Search
    places_url = "https://places.googleapis.com/v1/places:searchText"
    radius_meters = int(radius_miles * 1609.34)

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.types,places.businessStatus,places.googleMapsUri"
    }

    request_body = {
        "textQuery": query,
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lng
                },
                "radius": min(radius_meters, 50000.0)  # Max 50km
            }
        },
        "maxResultCount": min(max_results, 20)  # API max is 20 per request
    }

    businesses = []

    try:
        response = requests.post(places_url, headers=headers, json=request_body, timeout=15)

        if response.status_code != 200:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", response.text)
            return {"error": f"Places API error ({response.status_code}): {error_msg}"}

        data = response.json()

        for place in data.get("places", []):
            business = {
                "name": place.get("displayName", {}).get("text"),
                "address": place.get("formattedAddress"),
                "place_id": place.get("id"),
                "phone": place.get("nationalPhoneNumber"),
                "website": place.get("websiteUri"),
                "rating": place.get("rating"),
                "review_count": place.get("userRatingCount", 0),
                "types": place.get("types", []),
                "business_status": place.get("businessStatus"),
                "google_maps_url": place.get("googleMapsUri"),
            }
            businesses.append(business)

    except Exception as e:
        return {"error": f"Places search failed: {str(e)}"}

    return {
        "query": query,
        "location": location,
        "coordinates": {"lat": lat, "lng": lng},
        "radius_miles": radius_miles,
        "count": len(businesses),
        "businesses": businesses
    }


def main():
    load_env()

    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        input_data = {}

    query = input_data.get("query", "real estate agent")
    location = input_data.get("location", "Salt Lake City, UT")
    radius_miles = input_data.get("radius_miles", 25)
    max_results = input_data.get("max_results", 20)

    result = search_places(query, location, radius_miles, max_results)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
