# backend/sentiment_agent.py
# This script continuously monitors new social media posts in Firestore,
# uses the Google Gemini API to analyze their sentiment, and then
# updates the original post and adds a new entry to 'sentiment_data' collection.
# Now includes latitude and longitude in the sentiment_data.

import time
import google.generativeai as genai # Import the Gemini API library
from firestore_connector import db # Import the Firestore database client
from firebase_admin import firestore # Required for firestore.SERVER_TIMESTAMP
from google.cloud.firestore import FieldFilter # For filtering documents in queries
import os
from dotenv import load_dotenv # For loading API keys from .env

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

# Configure the Gemini API (using the model that was confirmed to be available)
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY"),
    transport="rest" 
    # client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"} # This was removed as the default endpoint worked
)

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text using the Gemini API.
    Returns 'POSITIVE', 'NEGATIVE', 'NEUTRAL', or 'ERROR' if something goes wrong.
    """
    try:
        # Using models/gemini-2.0-flash as it was listed as available
        model = genai.GenerativeModel('gemini-2.0-flash') 
        # Craft a specific prompt to instruct Gemini on the desired output format
        prompt = f"Analyze the sentiment of the following text and return ONLY one word: 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'. Text: '{text}'"
        
        # Generate content using the prompt
        response = model.generate_content(prompt)
        
        # Extract and clean the sentiment from Gemini's response
        sentiment = response.text.strip().upper()
        
        # Validate the sentiment to ensure it's one of the expected values
        if sentiment not in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
            sentiment = 'NEUTRAL' # Default to NEUTRAL for unexpected responses
        return sentiment
    except Exception as e:
        # Log errors during API call and return 'ERROR'
        print(f"Error calling Gemini API for text '{text[:50]}...': {e}")
        # Print the full error for debugging
        print(f"Full Gemini API Error: {e}") 
        return "ERROR"

def process_social_media_for_sentiment():
    """
    Queries Firestore for unprocessed social media posts, analyzes their sentiment,
    and updates/adds data to Firestore.
    """
    # Query for social media posts where the 'processed' field is False.
    # We limit to 5 documents per batch to avoid processing too many at once.
    docs_to_process = db.collection('social_media_feeds').where(filter=FieldFilter("processed", "==", False)).limit(5).stream()
    
    found_unprocessed = False # Flag to check if any documents were found
    for doc in docs_to_process:
        found_unprocessed = True
        data = doc.to_dict() # Convert Firestore document to a Python dictionary
        text = data.get('text_content', '') # Get the text content of the post
        
        if text: # Only process if text content exists
            sentiment_result = analyze_sentiment(text) # Call Gemini API for sentiment
            
            # Update the original social media document to mark it as processed
            # and store the raw sentiment result from Gemini.
            doc.reference.update({'processed': True, 'sentiment_score_raw': sentiment_result})
            
            # Create a new entry in the 'sentiment_data' collection.
            # Now including latitude and longitude from the original social_media_feeds document.
            sentiment_data_entry = {
                'timestamp': data.get('timestamp', firestore.SERVER_TIMESTAMP),
                'location_name': data.get('location_name', 'Unknown'),
                'latitude': data.get('latitude'),   # ADDED: Pass latitude
                'longitude': data.get('longitude'), # ADDED: Pass longitude
                'text_content': text,
                'sentiment_score': sentiment_result
            }
            try:
                db.collection('sentiment_data').add(sentiment_data_entry)
                print(f"Processed sentiment for post ID {doc.id} ('{text[:50]}...'): {sentiment_result}")
            except Exception as e:
                print(f"Error adding sentiment data to Firestore: {e}")
        time.sleep(0.3) # Small delay to avoid hitting API rate limits too quickly, especially for Gemini

    if not found_unprocessed:
        print("No new social media posts to process for sentiment.")

# Main execution block: This runs when the script is executed directly.
if __name__ == "__main__":
    print("Starting sentiment analysis agent...")
    while True:
        process_social_media_for_sentiment()
        time.sleep(10) # Check for new posts every 10 seconds
