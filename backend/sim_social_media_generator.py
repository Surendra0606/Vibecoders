import time
import random
from firestore_connector import db # Import Firestore client
from firebase_admin import firestore # Required for firestore.SERVER_TIMESTAMP

# Re-using locations from crowd generator for consistency
bengaluru_locations_list = list({
    "MG Road": {"lat": 12.9750, "lon": 77.6090},
    "Majestic Bus Stand": {"lat": 12.9774, "lon": 77.5700},
    "Koramangala 5th Block": {"lat": 12.9345, "lon": 77.6180},
    "Indiranagar 100 Feet Rd": {"lat": 12.9700, "lon": 77.6400},
    "Electronic City": {"lat": 12.8468, "lon": 77.6601},
    "Cubbon Park": {"lat": 12.9758, "lon": 77.5922}
}.keys()) # Just getting location names

mock_social_posts = [
    "Traffic is terrible on [LOCATION] today! Stuck for ages. 😠 #BengaluruTraffic",
    "Amazing weather in [LOCATION], perfect for a stroll! 😊 #Bengaluru",
    "Just saw a street performance at [LOCATION] - so lively! 🎶",
    "Construction noise near [LOCATION] is so annoying. Can't work. 😫",
    "Enjoying some great food at [LOCATION]. Highly recommend! 😋",
    "Too many people near [LOCATION] today, feels a bit overwhelming. 🚶‍♂️🚶‍♀️",
    "Peaceful morning at [LOCATION]. Feeling calm and refreshed. ✨",
    "Heard a loud commotion near [LOCATION]. Hope it's nothing serious. 🚨",
    "My favorite cafe at [LOCATION] just launched new pastries! 🍰🤤",
    "Power cut again in [LOCATION]! Frustrating! #BengaluruPower"
]

def generate_social_media_post():
    location_name = random.choice(bengaluru_locations_list)
    text_template = random.choice(mock_social_posts)
    text_content = text_template.replace("[LOCATION]", location_name)

    data = {
        'timestamp': firestore.SERVER_TIMESTAMP,
        'location_name': location_name,
        'text_content': text_content,
        'processed': False # Flag to indicate if sentiment has been analyzed
    }
    try:
        db.collection('social_media_feeds').add(data)
        print(f"Generated social post for {location_name}: '{text_content}'")
    except Exception as e:
        print(f"Error sending social media data to Firestore for {location_name}: {e}")

if __name__ == "__main__":
    print("Starting simulated social media generation...")
    while True:
        generate_social_media_post()
        time.sleep(7) # Generate a new post every 7 seconds