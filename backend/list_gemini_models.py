# backend/list_gemini_models.py
# This script lists all Gemini models available for your API key
# and their supported methods (like generateContent).

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY"),
    transport="rest",
    # Keep the client_options for now, as it might be relevant to what's available
    client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # You can try commenting out client_options for a moment too, to see default list
)

print("Listing available Gemini models and their supported methods:")
try:
    for m in genai.list_models():
        # We are interested in models that support 'generateContent'
        if 'generateContent' in m.supported_generation_methods:
            print(f"  Model Name: {m.name}")
            print(f"    Supported Methods: {m.supported_generation_methods}")
            print(f"    Description: {m.description}")
            print("-" * 30)
except Exception as e:
    print(f"Error listing models: {e}")
    print("Please ensure your GEMINI_API_KEY is correct and has access.")

print("\nAttempting with default endpoint (if previous failed):")
try:
    genai.configure(
        api_key=os.getenv("GEMINI_API_KEY"),
        transport="rest",
        # No explicit client_options here to use default endpoint
    )
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  Model Name (default endpoint): {m.name}")
            print(f"    Supported Methods: {m.supported_generation_methods}")
            print(f"    Description: {m.description}")
            print("-" * 30)
except Exception as e:
    print(f"Error listing models with default endpoint: {e}")
