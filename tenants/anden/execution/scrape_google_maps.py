#!/usr/bin/env python3
"""
Scrape business listings from Google Maps Places API.
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

def search_places(query: str, location: str, radius_miles: int = 25, max_results: int = 20) -> list:
    """
    Search Google Maps Places API for businesses.

    Args:
        query: Search query (e.g., "real estate agent", "insurance agency")
        location: City or address to center search
        radius_miles: Search radius in miles
        max_results: Maximum number of results to return

    Returns:
        List of business dictionaries
    """
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY not configured in .env"}

    # Convert location to coordinates using Geocoding API
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    geocode_params = {
        "address": location,
        "key": api_key
    }

    try:
        geo_response = requests.get(geocode_url, params=geocode_params, timeout=10)
        geo_data = geo_response.json()

        if geo_data.get("status") != "OK" or not geo_data.get("results"):
            return {"error": f"Could not geocode location: {location}"}

        lat = geo_data["results"][0]["geometry"]["location"]["lat"]
        lng = geo_data["results"][0]["geometry"]["location"]["lng"]
    except Exception as e:
        return {"error": f"Geocoding failed: {str(e)}"}

    # Search using Places API (Text Search)
    places_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    radius_meters = int(radius_miles * 1609.34)  # Convert miles to meters

    places_params = {
        "query": query,
        "location": f"{lat},{lng}",
        "radius": min(radius_meters, 50000),  # Max 50km
        "key": api_key
    }

    businesses = []
    next_page_token = None

    try:
        while len(businesses) < max_results:
            if next_page_token:
                places_params["pagetoken"] = next_page_token
                # Google requires a short delay between page requests
                import time
                time.sleep(2)

            response = requests.get(places_url, params=places_params, timeout=15)
            data = response.json()

            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                if data.get("status") == "ZERO_RESULTS":
                    break
                return {"error": f"Places API error: {data.get('status')} - {data.get('error_message', '')}"}

            for place in data.get("results", []):
                if len(businesses) >= max_results:
                    break

                business = {
                    "name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "place_id": place.get("place_id"),
                    "rating": place.get("rating"),
                    "review_count": place.get("user_ratings_total", 0),
                    "types": place.get("types", []),
                    "business_status": place.get("business_status"),
                }

                # Get additional details (phone, website) if available
                if place.get("place_id"):
                    details = get_place_details(place["place_id"], api_key)
                    if details:
                        business.update(details)

                businesses.append(business)

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

    except Exception as e:
        return {"error": f"Places search failed: {str(e)}"}

    return {
        "query": query,
        "location": location,
        "radius_miles": radius_miles,
        "count": len(businesses),
        "businesses": businesses
    }


def get_place_details(place_id: str, api_key: str) -> dict:
    """Get detailed info for a place (phone, website, hours)."""
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website,opening_hours,url",
        "key": api_key
    }

    try:
        response = requests.get(details_url, params=params, timeout=10)
        data = response.json()

        if data.get("status") == "OK" and data.get("result"):
            result = data["result"]
            return {
                "phone": result.get("formatted_phone_number"),
                "website": result.get("website"),
                "google_maps_url": result.get("url"),
                "hours": result.get("opening_hours", {}).get("weekday_text", [])
            }
    except:
        pass

    return {}


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
