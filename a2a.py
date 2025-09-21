import os
import googlemaps
from pprint import pprint

# --- Agent Definitions ---

class LocationAgent:
    """
    A specialized agent that converts a street address to geographical coordinates
    using the Google Maps Geocoding API.
    """
    def __init__(self, name="Location Agent"):
        self.name = name
        # IMPORTANT: Paste your Google Maps API key directly here.
        # This is a fallback in case the environment variable is not set.
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "key")
        
        if self.api_key == "YOUR_API_KEY_HERE" or not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not set. Please paste your key in the code.")
            
        self.gmaps = googlemaps.Client(key=self.api_key)
        print(f"{self.name} initialized.")

    def get_coordinates(self, address):
        """
        Geocodes a street address to get its latitude and longitude.
        
        Args:
            address (str): The street address to geocode.
            
        Returns:
            dict: A dictionary with 'lat' and 'lng' of the location, or None.
        """
        print(f"\n{self.name}: Received request to geocode address: '{address}'.")
        try:
            # Geocoding the address
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


class AmenitiesAgent:
    """
    A specialized agent that finds nearby points of interest using the
    Google Places API.
    """
    def __init__(self, name="Amenities Agent"):
        self.name = name
        # IMPORTANT: This agent uses the same API key as the Location Agent.
        # The key is fetched from the environment variable or the fallback value.
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "key")
        
        if self.api_key == "YOUR_API_KEY_HERE" or not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not set. Please paste your key in the code.")
            
        self.gmaps = googlemaps.Client(key=self.api_key)
        print(f"{self.name} initialized.")
    
    def find_nearby_places(self, location, place_type, radius=5000):
        """
        Finds places of a specific type within a given radius of a location.
        
        Args:
            location (dict): A dictionary with 'lat' and 'lng' keys.
            place_type (str): The type of place to search for (e.g., 'school', 'park').
            radius (int): The search radius in meters.
            
        Returns:
            list: A list of nearby places with their names and addresses.
        """
        print(f"\n{self.name}: Received request to find nearby '{place_type}' at {location}.")
        
        try:
            # Search for nearby places using the Places API
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
            print(f"An error occurred in AmenitiesAgent: {e}")
            return []


# --- A2A Orchestrator ---

def analyze_property(address):
    """
    Orchestrates the A2A communication between the location and amenities agents.
    """
    print("--- Starting Property Analysis ---")
    
    try:
        # Initialize the agents
        location_agent = LocationAgent()
        amenities_agent = AmenitiesAgent()
    except ValueError as e:
        print(f"Initialization failed: {e}")
        return

    # Step 1: Agent-to-Agent communication (Orchestrator -> Location Agent)
    # The orchestrator asks the LocationAgent for coordinates.
    coordinates = location_agent.get_coordinates(address)
    
    if not coordinates:
        print("\nCould not find coordinates for the address. Analysis failed.")
        return

    # Step 2: The orchestrator passes the output of the first agent
    # to the second agent.
    nearby_schools = amenities_agent.find_nearby_places(coordinates, "school")
    nearby_parks = amenities_agent.find_nearby_places(coordinates, "park")
    nearby_groceries = amenities_agent.find_nearby_places(coordinates, "grocery store")
    
    # Step 3: Orchestrator processes and presents the final, integrated result.
    print("\n--- Property Analysis Complete ---")
    print(f"Analysis for: {address}")
    print("\nNearby Schools:")
    pprint(nearby_schools)
    print("\nNearby Parks:")
    pprint(nearby_parks)
    print("\nNearby Grocery Stores:")
    pprint(nearby_groceries)

# --- Main Execution ---
if __name__ == "__main__":
    # To run this, you need to set your Google Maps API key as an environment variable:
    # GOOGLE_MAPS_API_KEY="your_google_maps_key"
    
    # Example 1: Analyze the Googleplex
    user_Address = input("Enter the address to analyze (or press Enter to use default): ")
    analyze_property("1600 Amphitheatre Parkway, Mountain View, CA" if not user_Address else user_Address)
    
    
