import os
import json
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import certifi
from bson import json_util
from dotenv import load_dotenv

# Import the agent function
from agent import decisionAgent

load_dotenv()

# --- MongoDB Connection ---
uri = os.getenv("MONGO_URI")
google_api_key = os.getenv("GOOGLE_API_KEY") # Ensure you have GOOGLE_API_KEY in your .env

if not uri:
    print("Error: MONGO_URI environment variable not set.")
    # Consider raising an exception or exiting if the DB connection is critical
    exit("MongoDB URI not found. Please set MONGO_URI in your .env file.")
if not google_api_key:
    print("Warning: GOOGLE_API_KEY environment variable not set.")
    # Decide if the app can run without the API key or exit
    # exit("Google API Key not found. Please set GOOGLE_API_KEY in your .env file.")

try:
    print("Attempting to connect to MongoDB...")
    client = MongoClient(uri, tlsCAFile=certifi.where())
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("Successfully connected to MongoDB")
    db = client.benefits_and_cost_sharing # Use your actual database name
    benefits_collection = db.data # Use your actual collection name for benefits
    eligibility_collection = client.medicaid_and_chip_eligibility_levels.data # Use your actual eligibility DB/collection
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    print(traceback.format_exc())
    # Exit if DB connection fails
    exit(f"Failed to connect to MongoDB: {e}")


app = Flask(__name__)
CORS(app)

@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"

