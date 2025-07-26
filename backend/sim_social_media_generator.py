# backend/sim_social_media_generator.py
# This script simulates social media posts for various Bengaluru locations
# and continuously sends them to the 'social_media_feeds' collection in Firestore.
# Now includes latitude and longitude for each post.

import time
import random
from firestore_connector import db # Import Firestore client
from firebase_admin import firestore # Required for firestore.SERVER_TIMESTAMP

# Define some approximate Bengaluru locations with their latitude and longitude.
# This dictionary is used to get coordinates for the social media posts.
bengaluru_locations = {
    "MG Road": {"lat": 12.9750, "lon": 77.6090},
    "Majestic Bus Stand": {"lat": 12.9774, "lon": 77.5700},
    "Koramangala 5th Block": {"lat": 12.9345, "lon": 77.6180},
    "Indiranagar 100 Feet Rd": {"lat": 12.9700, "lon": 77.6400},
    "Electronic City": {"lat": 12.8468, "lon": 77.6601},
    "Cubbon Park": {"lat": 12.9758, "lon": 77.5922},
    "Marathahalli": {"lat": 12.9569, "lon": 77.7011},
    "Kr puram": {"lat": 13.0170, "lon": 77.7044},
    "Bhanashankari": {"lat": 12.9255, "lon": 77.5468},
    "yeswanthpur": {"lat": 13.0250, "lon": 77.5340}
}

# A list of mock social media post templates.
# The [LOCATION] placeholder will be replaced with a random location name.
mock_social_posts = [
    "Traffic is terrible on [LOCATION] today! Stuck for ages. 😠 #BengaluruTraffic",
    "Amazing weather in [LOCATION], perfect for a stroll! 😊 #Bengaluru",
    "Just saw a street performance at [LOCATION] - so lively! 🎶",
    "Construction noise near [LOCATION] is so annoying. Can't work. �",
    "Enjoying some great food at [LOCATION]. Highly recommend! 😋",
    "Too many people near [LOCATION] today, feels a bit overwhelming. 🚶‍♂️🚶‍♀️",
    "Peaceful morning at [LOCATION]. Feeling calm and refreshed. ✨",
    "Heard a loud commotion near [LOCATION]. Hope it's nothing serious. 🚨",
    "My favorite cafe at [LOCATION] just launched new pastries! 🍰🤤",
    "Power cut again in [LOCATION]! Frustrating! #BengaluruPower",
    "Excited for the weekend market at [LOCATION]! 🛍️",
    "Just finished a run at [LOCATION], feeling great!",
    "Heavy rains near [LOCATION], drive safe everyone! 🌧️"
]

def generate_social_media_post():
    """
    Generates a single simulated social media post with a random location, text,
    and now includes latitude and longitude.
    """
    # Randomly select a location (both name and coordinates) from the dictionary
    location_name, coords = random.choice(list(bengaluru_locations.items()))
    
    text_template = random.choice(mock_social_posts)
    text_content = text_template.replace("[LOCATION]", location_name) # Replace placeholder

    # Add slight random variation to coordinates for visual spread on the map.
    lat_var = random.uniform(-0.001, 0.001)
    lon_var = random.uniform(-0.001, 0.001)

    data = {
        'timestamp': firestore.SERVER_TIMESTAMP, # Firestore sets the actual server timestamp
        'location_name': location_name,
        'latitude': coords['lat'] + lat_var,   # Pass latitude from selected location + variation
        'longitude': coords['lon'] + lon_var, # Pass longitude from selected location + variation
        'text_content': text_content,
        'processed': False # Flag to indicate that this post needs sentiment analysis
    }
    try:
        # Add the generated post as a new document to the 'social_media_feeds' collection
        db.collection('social_media_feeds').add(data)
        print(f"Generated social post for {location_name} ({data['latitude']:.4f}, {data['longitude']:.4f}): '{text_content}'")
    except Exception as e:
        # Log any errors that occur during Firestore write operations
        print(f"Error sending social media data to Firestore for {location_name}: {e}")

# Main execution block: This runs when the script is executed directly.
if __name__ == "__main__":
    print("Starting simulated social media generation...")
    while True:
        generate_social_media_post()
        time.sleep(7) # Pause for 7 seconds before generating the next post
