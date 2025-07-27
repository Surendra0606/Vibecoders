# backend/sim_camera_feed_updater.py
# This script now dynamically generates camera feed images using Imagen 3.0
# based on the latest HIGH alerts in Firestore, or a default "normal" scene.

import time
import random
import base64
import requests # Needed for direct Imagen API calls
from firestore_connector import db # Import Firestore client
from firebase_admin import firestore # Required for firestore.SERVER_TIMESTAMP
from google.cloud import storage # For uploading images to Firebase Storage

# --- NEW/UPDATED IMPORTS FOR CREDENTIALS ---
from google.oauth2 import service_account # For explicitly loading service account credentials
# --- END NEW/UPDATED IMPORTS ---

import google.generativeai as genai # For configuring API key for Imagen
import os
from dotenv import load_dotenv

load_dotenv()

# --- Load Google Cloud Storage Credentials Explicitly ---
# This is the most robust way to authenticate google-cloud-storage when running locally.
storage_credentials = None
cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")

if cred_path and os.path.exists(cred_path):
    try:
        # Load credentials directly from the service account key file
        storage_credentials = service_account.Credentials.from_service_account_file(cred_path)
        print("Storage credentials loaded successfully from service account file.")
    except Exception as e:
        print(f"Error loading storage credentials from '{cred_path}': {e}. Storage operations might fail.")
else:
    print(f"FIREBASE_SERVICE_ACCOUNT_KEY_PATH '{cred_path}' not found or invalid. Storage operations will be disabled.")
# --- END CREDENTIALS LOAD ---


# Google Cloud Storage (Firebase Storage) setup
# CRITICAL: Pass the loaded credentials directly to the storage.Client()
storage_client = None
if storage_credentials:
    try:
        storage_client = storage.Client(credentials=storage_credentials)
        print("storage.Client initialized with explicit credentials.")
    except Exception as e:
        print(f"Error initializing storage.Client with explicit credentials: {e}. Storage operations disabled.")
else:
    print("Storage credentials not available. storage.Client() not initialized.")


FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")
bucket = None
if storage_client and FIREBASE_STORAGE_BUCKET:
    try:
        bucket = storage_client.bucket(FIREBASE_STORAGE_BUCKET)
        print(f"Firebase Storage bucket '{FIREBASE_STORAGE_BUCKET}' accessed successfully.")
    except Exception as e:
        print(f"Error accessing Firebase Storage bucket '{FIREBASE_STORAGE_BUCKET}': {e}. Image generation/upload disabled.")
else:
    print("Firebase Storage bucket name not configured or storage client invalid. Image generation/upload disabled.")


# Gemini API for Image Generation (Imagen 3.0)
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY"),
    transport="rest",
    client_options={"api_endpoint": "https://generativelanguage.googleapis.com"} # Default endpoint for Imagen
)
IMAGEN_MODEL = "imagen-3.0-generate-002" # Imagen 3.0 model name

# Fixed document ID for the main camera feed that frontend listens to
CAMERA_FEED_DOC_ID = "main_alert_camera_feed" 

# Cooldown to prevent rapid image generation (Imagen can be slower and costlier)
IMAGE_GEN_COOLDOWN_SECONDS = 60 * 1 # Generate new image every 1 minute (reduced for hackathon demo)

last_image_gen_time = 0

def upload_image_to_storage(image_bytes, destination_blob_name):
    """Uploads a base64 decoded image to Firebase Storage."""
    if not bucket:
        print("Firebase Storage bucket not configured or invalid. Cannot upload image.")
        return None
    try:
        blob = bucket.blob(destination_blob_name)
        # Set content type to ensure it's served correctly by browser
        blob.upload_from_string(image_bytes, content_type='image/png') 
        blob.make_public() # Make the image publicly accessible
        print(f"Image uploaded to: {blob.public_url}")
        return blob.public_url
    except Exception as e:
        print(f"Error uploading image to Storage: {e}")
        return None

def generate_scene_image(prompt_text, location_name="Bengaluru"):
    """Generates an image using Imagen 3.0 based on a prompt and uploads it."""
    global last_image_gen_time
    current_time = time.time()

    if (current_time - last_image_gen_time) < IMAGE_GEN_COOLDOWN_SECONDS:
        print(f"Image generation is in cooldown. Next generation in {int(IMAGE_GEN_COOLDOWN_SECONDS - (current_time - last_image_gen_time))} seconds.")
        return None # Skip generation if in cooldown

    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not found. Skipping image generation.")
        return None
    
    print(f"Generating image for: '{prompt_text}'...")
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        # The Imagen API endpoint is different from the text models sometimes
        # Use the endpoint suggested in the initial instructions for Imagen 3.0
        imagen_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGEN_MODEL}:predict?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {"instances": [{"prompt": prompt_text}], "parameters": {"sampleCount": 1}}

        response = requests.post(imagen_api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        
        result = response.json()
        
        if result.get("predictions") and result["predictions"][0].get("bytesBase64Encoded"):
            base64_image = result["predictions"][0]["bytesBase64Encoded"]
            image_bytes = base64.b64decode(base64_image)
            
            blob_name = f"camera_feeds/{location_name.replace(' ', '_').lower()}_{int(time.time())}.png"
            public_url = upload_image_to_storage(image_bytes, blob_name)
            last_image_gen_time = current_time # Update last generation time
            return public_url
        else:
            print("No image data found in Imagen API response.")
            print(f"Imagen API Response: {result}") # Log full response for debugging
            return None
    except requests.exceptions.RequestException as req_err:
        print(f"HTTP Request Error calling Imagen API: {req_err}")
        print(f"Response content: {req_err.response.text if req_err.response else 'N/A'}")
        return None
    except Exception as e:
        print(f"Error generating or uploading image: {e}")
        return None

def update_camera_feed_based_on_alerts():
    """
    Checks for the latest HIGH alert. If found, generates an image reflecting the alert.
    If no HIGH alert, generates a default "normal city" image.
    """
    latest_high_alert = None
    try:
        # Fetch the very latest HIGH alert
        # The UserWarning "Detected filter using positional arguments" is harmless but can be removed
        # by using the 'filter' keyword argument as suggested by the warning.
        # Example: .where(filter=FieldFilter('threat_level', '==', 'HIGH'))
        docs = db.collection('threat_alerts').where('threat_level', '==', 'HIGH').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
        for doc in docs:
            latest_high_alert = doc.to_dict()
            break # Get only the first (latest) one
        
        # Check if the latest high alert is still "active" (e.g., within the last 5 minutes)
        if latest_high_alert and (time.time() - latest_high_alert['timestamp'].timestamp()) < (60 * 5): # Alert is less than 5 mins old
            prompt_for_image = f"A very crowded street scene in Bengaluru near {latest_high_alert['location_name']}, showing signs of high density, realistic photo, urban environment, daytime."
            if latest_high_alert.get('details') and "extremely dense" in latest_high_alert['details']:
                prompt_for_image = f"An extremely dense crowd forming in Bengaluru near {latest_high_alert['location_name']}, people looking anxious or confused, realistic photo, urban environment, daytime, wide angle."
            
            print(f"Detected HIGH alert at {latest_high_alert['location_name']}. Triggering image generation...")
            image_url = generate_scene_image(prompt_for_image, latest_high_alert['location_name'])
            
            if image_url:
                # Update a fixed camera feed document that frontend listens to
                camera_feed_data = {
                    'timestamp': firestore.SERVER_TIMESTAMP,
                    'image_url': image_url,
                    'location_name': latest_high_alert['location_name'],
                    'alert_level': latest_high_alert['threat_level'],
                    'details': latest_high_alert['details']
                }
                db.collection('camera_feeds').document(CAMERA_FEED_DOC_ID).set(camera_feed_data, merge=True)
                print(f"Updated camera feed with AI-generated image for HIGH alert at {latest_high_alert['location_name']}.")
            else:
                print(f"Failed to generate or upload image for {latest_high_alert['location_name']}.")
        else:
            # No recent HIGH alert, generate a normal scene
            print("No recent HIGH alerts. Generating a default 'normal' city scene.")
            default_prompt = "A normal, moderately busy street scene in Bengaluru, sunny day, people walking casually, urban environment, daytime."
            image_url = generate_scene_image(default_prompt, "Bengaluru City")
            if image_url:
                camera_feed_data = {
                    'timestamp': firestore.SERVER_TIMESTAMP,
                    'image_url': image_url,
                    'location_name': "Bengaluru City (Normal)",
                    'alert_level': "LOW",
                    'details': "Normal city activity."
                }
                db.collection('camera_feeds').document(CAMERA_FEED_DOC_ID).set(camera_feed_data, merge=True)
                print("Updated camera feed with default 'normal' scene.")
            else:
                print("Failed to generate or upload default 'normal' scene image.")

    except Exception as e:
        print(f"Error in camera feed updater: {e}")

# Main execution block
if __name__ == "__main__":
    print("Starting Camera Feed Updater Agent...")
    try:
        # Ensure 'requests' and 'google-cloud-storage' libraries are installed
        import requests
        from google.cloud import storage # Explicitly import to check
        from google.oauth2 import service_account # Explicitly import for credentials
    except ImportError as ie:
        print(f"Missing library: {ie}. Please install it: pip install requests google-cloud-storage google-auth-oauthlib") # Added google-auth-oauthlib
        exit()
    
    while True:
        update_camera_feed_based_on_alerts()
        time.sleep(60 * 1) # Check and update camera feed every 1 minute
