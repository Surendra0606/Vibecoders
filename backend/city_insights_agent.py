# backend/city_insights_agent.py
# This AI agent reads recent crowd density, sentiment, and threat alert data from Firestore,
# uses the Google Gemini API to generate actionable insights and recommendations,
# and then stores these insights in a new 'city_insights' collection in Firestore.

import time
import google.generativeai as genai
from firestore_connector import db # Import Firestore client
from firebase_admin import firestore # Required for firestore.SERVER_TIMESTAMP
from google.cloud.firestore import FieldFilter
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API (using the model that was confirmed to be available)
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY"),
    transport="rest" 
)

# Define the Gemini model to use for insights generation
GEMINI_INSIGHTS_MODEL = 'gemini-2.0-flash' # Use the flash model for speed and cost-efficiency

def get_recent_data(collection_name, limit=20, time_window_minutes=60):
    """
    Fetches recent data from a specified Firestore collection within a time window.
    """
    # Calculate the timestamp for the start of the time window
    cutoff_timestamp = firestore.SERVER_TIMESTAMP # Placeholder, will be replaced by actual timestamp when querying
    
    # For filtering by time, we need a specific timestamp.
    # Firestore queries on SERVER_TIMESTAMP are tricky for range queries.
    # For hackathon simplicity, we'll just fetch a limit and assume it's recent enough.
    # A more robust solution would involve client-side timestamps or server-side functions.
    
    docs = db.collection(collection_name).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
    recent_data = []
    for doc in docs:
        data = doc.to_dict()
        # Basic check for data freshness (optional, but good practice)
        if data.get('timestamp') and (time.time() - data['timestamp'].timestamp()) / 60 < time_window_minutes:
            recent_data.append(data)
    return recent_data

def generate_city_insights():
    """
    Collects recent city data, generates insights using Gemini, and saves them.
    """
    print("Generating new city insights...")
    
    # Fetch recent data from various collections
    recent_crowd = get_recent_data('crowd_data', limit=50)
    recent_sentiment = get_recent_data('sentiment_data', limit=50)
    recent_alerts = get_recent_data('threat_alerts', limit=10)

    # Prepare data for Gemini prompt
    crowd_summary = "\n".join([f"- {d['location_name']}: Density {d['simulated_density']:.2f} at {d['timestamp'].strftime('%H:%M')}" for d in recent_crowd]) if recent_crowd else "No recent crowd data."
    sentiment_summary = "\n".join([f"- {d['location_name']}: {d['sentiment_score']} ('{d['text_content'][:50]}...') at {d['timestamp'].strftime('%H:%M')}" for d in recent_sentiment]) if recent_sentiment else "No recent sentiment data."
    alerts_summary = "\n".join([f"- {d['threat_type']} at {d['location_name']} (Level: {d['threat_level']}): {d['details']}" for d in recent_alerts]) if recent_alerts else "No recent alerts."

    # Construct the prompt for Gemini
    prompt = f"""
    Analyze the following recent city data from Bengaluru and provide actionable insights and recommendations for city authorities.
    Focus on:
    1. Summarizing key trends (crowd density, sentiment).
    2. Identifying potential issues or areas needing attention.
    3. Suggesting proactive measures or resource allocation.
    
    Recent Crowd Data (latest first):
    {crowd_summary}

    Recent Sentiment Data (latest first):
    {sentiment_summary}

    Recent Alerts (latest first):
    {alerts_summary}

    Provide the insights in a concise paragraph followed by 2-3 bullet-point recommendations.
    """

    try:
        model = genai.GenerativeModel(GEMINI_INSIGHTS_MODEL)
        response = model.generate_content(prompt)
        insight_text = response.text.strip()
        
        # Store the generated insight in Firestore
        insight_data = {
            'timestamp': firestore.SERVER_TIMESTAMP,
            'insight_summary': insight_text,
            'generated_by_agent': 'City Insights Agent',
            'model_used': GEMINI_INSIGHTS_MODEL
        }
        db.collection('city_insights').add(insight_data)
        print(f"Generated and stored new city insight:\n{insight_text[:200]}...") # Print first 200 chars
    except Exception as e:
        print(f"Error generating or storing city insights: {e}")
        print(f"Full Gemini API Error for insights: {e}")

# Main execution block
if __name__ == "__main__":
    print("Starting City Insights Agent...")
    while True:
        generate_city_insights()
        time.sleep(60 * 2) # Generate insights every 5 minutes (adjust as needed for hackathon demo)
