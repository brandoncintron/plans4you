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
db = client.sample_mflix 

app = Flask(__name__)

@app.route("/api/test")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/comments", methods=["GET"])
def get_comments():
    if request.method == "GET":
        try:
            print("Attempting to query comments collection")
            # Check if the collection exists
            collections = db.list_collection_names()
            print(f"Available collections: {collections}")
            
            if "comments" not in collections:
                print("Comments collection not found")
                return jsonify({"error": "Comments collection not found"}), 404
                
            # Get comments from the comments collection and limit to 20
            comments = list(db.comments.find({}).limit(20))
            
            # Convert ObjectId to string for JSON serialization
            json_comments = json.loads(json_util.dumps(comments))
            
            print(f"Successfully retrieved {len(json_comments)} comments")
            return jsonify(json_comments)
        except Exception as e:
            print(f"Error querying MongoDB: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500