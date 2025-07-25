import time
import google.generativeai as genai
from firestore_connector import db # Import Firestore client
from google.cloud.firestore_v1.query import FieldFilter # To filter documents
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_sentiment(text):
    try:
        model = genai.GenerativeModel('gemini-pro')
        # Simple prompt to get POSITIVE/NEGATIVE/NEUTRAL
        prompt = f"Analyze the sentiment of the following text and return ONLY one word: 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'. Text: '{text}'"
        response = model.generate_content(prompt)
        sentiment = response.text.strip().upper()
        if sentiment not in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
            sentiment = 'NEUTRAL' # Default for unexpected responses from Gemini
        return sentiment
    except Exception as e:
        print(f"Error calling Gemini API for text '{text[:30]}...': {e}")
        return "ERROR" # Return ERROR if something goes wrong with API call

def process_social_media_for_sentiment():
    # Query for social media posts that haven't been processed yet
    docs_to_process = db.collection('social_media_feeds').where(filter=FieldFilter("processed", "==", False)).limit(5).stream() # Process 5 at a time

    found_unprocessed = False
    for doc in docs_to_process:
        found_unprocessed = True
        data = doc.to_dict()
        text = data.get('text_content', '')

        if text:
            sentiment_result = analyze_sentiment(text)

            # Update the original social media document as processed
            doc.reference.update({'processed': True, 'sentiment_score_raw': sentiment_result})

            # Add a new entry to sentiment_data collection for the frontend
            sentiment_data_entry = {
                'timestamp': data.get('timestamp', firestore.SERVER_TIMESTAMP),
                'location_name': data.get('location_name', 'Unknown'),
                'text_content': text, # Storing original text for context
                'sentiment_score': sentiment_result # The analyzed sentiment (POSITIVE/NEGATIVE/NEUTRAL)
            }
            db.collection('sentiment_data').add(sentiment_data_entry)
            print(f"Processed sentiment for post ID {doc.id} ('{text[:50]}...'): {sentiment_result}")
        time.sleep(0.3) # Small delay to avoid hitting API limits too quickly

    if not found_unprocessed:
        print("No new social media posts to process for sentiment.")

if __name__ == "__main__":
    print("Starting sentiment analysis agent...")
    while True:
        process_social_media_for_sentiment()
        time.sleep(10) # Check for new posts every 10 seconds