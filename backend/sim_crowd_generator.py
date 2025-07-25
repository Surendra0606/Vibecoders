import time
import random
from firestore_connector import db # Import the Firestore database client
from firebase_admin import firestore # Required for firestore.SERVER_TIMESTAMP

# Define some approximate Bengaluru locations for simulation
bengaluru_locations = {
    "MG Road": {"lat": 12.9750, "lon": 77.6090},
    "Majestic Bus Stand": {"lat": 12.9774, "lon": 77.5700},
    "Koramangala 5th Block": {"lat": 12.9345, "lon": 77.6180},
    "Indiranagar 100 Feet Rd": {"lat": 12.9700, "lon": 77.6400},
    "Electronic City": {"lat": 12.8468, "lon": 77.6601},
    "Cubbon Park": {"lat": 12.9758, "lon": 77.5922}
}

def generate_single_crowd_data_point(location_name, coords):
    # Simulate density between 0.1 (low) and 1.0 (very high)
    density = round(random.uniform(0.1, 1.0), 2)
    # Add slight random variation to coordinates for visual spread on map
    lat_var = random.uniform(-0.005, 0.005)
    lon_var = random.uniform(-0.005, 0.005)

    data = {
        'timestamp': firestore.SERVER_TIMESTAMP, # Firestore sets the actual server time
        'location_name': location_name,
        'latitude': coords['lat'] + lat_var,
        'longitude': coords['lon'] + lon_var,
        'simulated_density': density
    }
    return data

def send_crowd_data_to_firestore():
    for name, coords in bengaluru_locations.items():
        data_point = generate_single_crowd_data_point(name, coords)
        try:
            # Add data to 'crowd_data' collection
            db.collection('crowd_data').add(data_point)
            print(f"Generated crowd data for {name}: Density {data_point['simulated_density']:.2f}")
        except Exception as e:
            print(f"Error sending crowd data to Firestore for {name}: {e}")

if __name__ == "__main__":
    print("Starting simulated crowd data generation...")
    while True:
        send_crowd_data_to_firestore()
        time.sleep(5) # Generate new data for all locations every 5 seconds