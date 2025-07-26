import time
from firestore_connector import db # Import Firestore client
from firebase_admin import firestore # Required for firestore.SERVER_TIMESTAMP
from google.cloud.firestore import FieldFilter # To filter documents

from twilio.rest import Client # For sending SMS alerts
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

# Twilio credentials from .env
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
recipient_phone_number = os.getenv("RECIPIENT_PHONE_NUMBER")

# Initialize Twilio client (only if credentials are found)
twilio_client = None
if account_sid and auth_token:
    try:
        twilio_client = Client(account_sid, auth_token)
        print("Twilio client initialized.")
    except Exception as e:
        print(f"Error initializing Twilio client: {e}. SMS alerts disabled.")
else:
    print("Twilio credentials not found in .env. SMS alerts disabled.")


# Simple thresholds for crowd density alerts
DENSITY_THRESHOLD_HIGH = 0.8 # High density, critical alert
DENSITY_THRESHOLD_MEDIUM = 0.6 # Medium density, warning

ALERT_COOLDOWN_SECONDS = 60 * 2 # Don't send alerts for the same location too often (2 minutes)

# Dictionary to keep track of the last time an alert was sent for a location
last_alert_time = {}

def send_sms_alert(to_number, from_number, message_body):
    if not twilio_client:
        print("Twilio client not initialized. Cannot send SMS.")
        return

    try:
        message = twilio_client.messages.create(
            to=to_number,
            from_=from_number,
            body=message_body
        )
        print(f"SMS alert sent successfully: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS alert: {e}")
        print("Ensure Twilio Account SID, Auth Token, and phone numbers are correct.")

def check_for_threats():
    # Get the latest crowd data for each location
    # For simplicity, we'll fetch the last 20 data points and find the latest for each unique location
    # A more robust solution might query specific locations or use Firestore triggers
    docs = db.collection('crowd_data').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(20).stream()

    latest_data_by_location = {}
    for doc in docs:
        data = doc.to_dict()
        loc_name = data.get('location_name')
        if loc_name and loc_name not in latest_data_by_location:
            latest_data_by_location[loc_name] = data

    for loc_name, data in latest_data_by_location.items():
        density = data.get('simulated_density', 0)
        current_unix_time = time.time() # Current time in seconds since epoch

        # Check if this location is in cooldown period
        if loc_name in last_alert_time and (current_unix_time - last_alert_time[loc_name]) < ALERT_COOLDOWN_SECONDS:
            print(f"Location {loc_name} is in cooldown. Skipping alert check.")
            continue # Skip if an alert was recently sent for this location

        threat_level = "LOW"
        alert_details = f"Simulated density at {loc_name} is {density:.2f}."

        if density >= DENSITY_THRESHOLD_HIGH:
            threat_level = "HIGH"
            alert_details += " This indicates a critical crowd density."
        elif density >= DENSITY_THRESHOLD_MEDIUM:
            threat_level = "MEDIUM"
            alert_details += " This indicates a moderate crowd density."

        # If a threat level is detected (Medium or High)
        if threat_level != "LOW":
            alert_data = {
                'timestamp': firestore.SERVER_TIMESTAMP,
                'location_name': loc_name,
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'threat_type': 'Crowd Density Alert',
                'threat_level': threat_level,
                'details': alert_details
            }
            try:
                db.collection('threat_alerts').add(alert_data)
                print(f"🚨 ALERT for {loc_name}: {threat_level} - Density: {density:.2f}")
                last_alert_time[loc_name] = current_unix_time # Update last alert time for this location

                # Send SMS for HIGH level threats
                if threat_level == "HIGH" and recipient_phone_number and twilio_phone_number:
                    sms_message = f"URGENT City Alert: {alert_data['threat_type']} at {loc_name}. Level: {threat_level}. Details: {alert_data['details']}"
                    send_sms_alert(recipient_phone_number, twilio_phone_number, sms_message)

            except Exception as e:
                print(f"Error adding threat alert to Firestore for {loc_name}: {e}")

if __name__ == "__main__":
    print("Starting threat detection agent...")
    while True:
        check_for_threats()
        time.sleep(5) # Check for threats every 5 seconds