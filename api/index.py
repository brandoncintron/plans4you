from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
import json
from bson import json_util
import traceback
import os

load_dotenv()

uri = os.getenv("MONGO_URI")

if not uri:
    print("Error: MONGODB_URI environment variable not set.")
    print("Make sure you have a .env file with MONGODB_URI defined.")

# Connect to MongoDB
print("Attempting to connect to MongoDB...")
client = MongoClient(uri, tlsCAFile=certifi.where())
print("Successfully connected to MongoDB")
benefits_and_cost_sharing = client.benefits_and_cost_sharing
medicaid_and_chip_eligibility = client.medicaid_and_chip_eligibility_levels

app = Flask(__name__)

@app.route("/api/test")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/benefits_and_cost_sharing", methods=["GET"])
def get_benefits_and_cost_sharing():
    if request.method == "GET":
        try:
            print("Attempting to query data collection")
            # Check if the collection exists
            collections = benefits_and_cost_sharing.list_collection_names()
            print(f"Available collections: {collections}")
            
            if "data" not in collections:
                print("data collection not found")
                return jsonify({"error": "data collection not found"}), 404
                
            data = list(benefits_and_cost_sharing.data.find({}).limit(200))
            
            # Convert ObjectId to string for JSON serialization
            json_data = json.loads(json_util.dumps(data))
            
            print(f"Successfully retrieved {len(json_data)} data")
            return jsonify(json_data)
        except Exception as e:
            print(f"Error querying MongoDB: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500
        
@app.route("/api/medicaid_and_chip_eligibility", methods=["GET"])
def get_medicaid_and_chip_eligibility():
    if request.method == "GET":
        try:
            print("Attempting to query data collection")
            # Check if the collection exists
            collections = medicaid_and_chip_eligibility.list_collection_names()
            print(f"Available collections: {collections}")
            
            if "data" not in collections:
                print("data collection not found")
                return jsonify({"error": "data collection not found"}), 404
                
            data = list(medicaid_and_chip_eligibility.data.find({}))
            
            # Convert ObjectId to string for JSON serialization
            json_data = json.loads(json_util.dumps(data))
            
            print(f"Successfully retrieved {len(json_data)} data")
            return jsonify(json_data)
        except Exception as e:
            print(f"Error querying MongoDB: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500