import os
import googlemaps
import requests
from pprint import pprint

# --- Agent Definitions ---

class LocationAgent:
    """
    A specialized agent that converts a street address or city name to geographical
    coordinates using the Google Maps Geocoding API.
    """
    def __init__(self, name="Location Agent"):
        self.name = name
        # Paste your Google Maps API key here
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "key")
        
        if self.api_key == "YOUR_GOOGLE_MAPS_API_KEY_HERE" or not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not set. Please paste your key in the code.")
            
        self.gmaps = googlemaps.Client(key=self.api_key)
        print(f"{self.name} initialized.")

    def get_coordinates(self, address):
        """
        Geocodes a street address or city to get its latitude and longitude.
        
        Args:
            address (str): The location to geocode.
            
        Returns:
            dict: A dictionary with 'lat' and 'lng' of the location, or None.
        """
        print(f"\n{self.name}: Received request to geocode location: '{address}'.")
        try:
            geocode_result = self.gmaps.geocode(address)
            
            if not geocode_result:
                print(f"{self.name}: No location found for that address.")
                return None
            
            location = geocode_result[0]['geometry']['location']
            print(f"{self.name}: Found coordinates: {location['lat']}, {location['lng']}.")
            return location
            
        except Exception as e:
            print(f"An error occurred in LocationAgent: {e}")
            return None


class AttractionsAgent:
    """
    A specialized agent that finds nearby points of interest for a traveler
    using the Google Places API.
    """
    def __init__(self, name="Attractions Agent"):
        self.name = name
        # This agent uses the same Google Maps API key as the Location Agent.
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "key")
        
        if self.api_key == "YOUR_GOOGLE_MAPS_API_KEY_HERE" or not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not set. Please paste your key in the code.")
            
        self.gmaps = googlemaps.Client(key=self.api_key)
        print(f"{self.name} initialized.")
    
    def find_nearby_places(self, location, place_type, radius=5000):
        """
        Finds places of a specific type within a given radius of a location.
        
        Args:
            location (dict): A dictionary with 'lat' and 'lng' keys.
            place_type (str): The type of place to search for (e.g., 'museum', 'restaurant').
            radius (int): The search radius in meters.
            
        Returns:
            list: A list of nearby places with their names and addresses.
        """
        print(f"\n{self.name}: Received request to find nearby '{place_type}' at {location}.")
        
        try:
            places_result = self.gmaps.places(
                query=place_type,
                location=location,
                radius=radius
            )
            
            if not places_result or not places_result.get('results'):
                print(f"{self.name}: No {place_type} found in the area.")
                return []
            
            amenities = []
            for place in places_result['results']:
                amenities.append({
                    "name": place.get('name'),
                    "address": place.get('vicinity', place.get('formatted_address'))
                })
            
            print(f"{self.name}: Found {len(amenities)} nearby {place_type}(s).")
            return amenities
            
        except Exception as e:
            print(f"An error occurred in AttractionsAgent: {e}")
            return []


class WeatherAgent:
    """
    A specialized agent that gets the weather forecast for a given location
    using the free wttr.in service.
    """
    def __init__(self, name="Weather Agent"):
        self.name = name
        self.base_url = "https://wttr.in/"
        print(f"{self.name} initialized.")
        
    def get_weather(self, location):
        """
        Gets the current weather for a location based on lat/lng coordinates.
        
        Args:
            location (dict): A dictionary with 'lat' and 'lng' keys.
            
        Returns:
            dict: The weather data, or None.
        """
        print(f"\n{self.name}: Received request for weather at {location['lat']}, {location['lng']}.")
        try:
            # We'll use the latitude and longitude to get the weather forecast in JSON format
            response = requests.get(f"{self.base_url}{location['lat']},{location['lng']}?format=j1")
            response.raise_for_status() # Raise an exception for bad status codes
            
            weather_data = response.json()
            current_condition = weather_data['current_condition'][0]
            
            weather_report = {
                "description": current_condition['weatherDesc'][0]['value'],
                "temperature": f"{current_condition['temp_C']} °C",
                "feels_like": f"{current_condition['FeelsLikeC']} °C",
                "humidity": f"{current_condition['humidity']}%",
                "wind_speed": f"{current_condition['windspeedKmph']} km/h"
            }
            print(f"{self.name}: Successfully retrieved weather data.")
            return weather_report
            
        except Exception as e:
            print(f"An error occurred in WeatherAgent: {e}")
            return None


# --- A2A Orchestrator ---

def plan_trip(city):
    """
    Orchestrates the A2A communication between multiple agents to create a
    comprehensive travel plan.
    """
    print(f"--- Starting Trip Plan for {city} ---")
    
    try:
        # Initialize the agents
        location_agent = LocationAgent()
        attractions_agent = AttractionsAgent()
        weather_agent = WeatherAgent()
    except ValueError as e:
        print(f"Initialization failed: {e}")
        return

    # Step 1: Orchestrator -> Location Agent
    # The orchestrator asks the LocationAgent for coordinates.
    coordinates = location_agent.get_coordinates(city)
    
    if not coordinates:
        print("\nCould not find coordinates for the city. Planning failed.")
        return

    # Step 2: Orchestrator passes the output of the first agent to the others.
    # It communicates with the WeatherAgent and AttractionsAgent in parallel.
    weather_data = weather_agent.get_weather(coordinates)
    nearby_attractions = attractions_agent.find_nearby_places(coordinates, "tourist_attraction")
    nearby_restaurants = attractions_agent.find_nearby_places(coordinates, "restaurant")
    
    # Step 3: Orchestrator processes and presents the final, integrated result.
    print(f"\n--- Trip Plan for {city} Complete ---")
    print("\nWeather Forecast:")
    pprint(weather_data)
    
    print("\nNearby Attractions:")
    pprint(nearby_attractions)
    
    print("\nNearby Restaurants:")
    pprint(nearby_restaurants)

# --- Main Execution ---
if __name__ == "__main__":
    # To run this, you need to paste your Google Maps API key in the code above.
    user_input = input("enter the city you esnt to go:").strip()
    plan_trip(user_input)
    
   
