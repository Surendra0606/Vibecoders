# backend/firestore_connector.py
# This script handles the connection to Google Cloud Firestore using Firebase Admin SDK.
# It's imported by other backend agents to interact with the database.

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from dotenv import load_dotenv

# Load environment variables from the .env file (e.g., FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
load_dotenv()

# Get the path to the Firebase service account key from environment variables
# This key allows your Python backend to securely interact with Firebase services.
cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")

# Initialize Firebase Admin SDK if it hasn't been initialized already.
# This check prevents re-initialization errors if the script is run multiple times
# or imported in complex ways.
if not firebase_admin._apps:
    try:
        # Use the service account key to authenticate your application
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        # Print an error message and exit if initialization fails.
        # This is critical as other scripts depend on a successful connection.
        print(f"Error initializing Firebase Admin SDK: {e}")
        print(f"Please ensure the service account key path '{cred_path}' is correct and the file exists.")
        exit() # Exit the script if Firebase initialization fails

# Get a Firestore client instance. This 'db' object will be used for all database operations.
db = firestore.client()
