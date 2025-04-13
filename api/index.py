import os
import json
import traceback
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import certifi
from bson import json_util
from dotenv import load_dotenv

# Import the agent function
from agent import decisionAgent

# Load environment variables from .env file
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

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- API Routes ---

@app.route("/api/test")
def hello_world():
    """A simple test route."""
    return "<p>Hello, World!</p>"

@app.route("/api/benefits_and_cost_sharing", methods=["GET", "POST"])
def handle_benefits_and_cost_sharing():
    """
    Handles GET requests to fetch plan data and POST requests
    to process user data and get AI recommendations.
    """
    if request.method == "POST":
        return process_user_request()
    elif request.method == "GET":
        return get_filtered_benefits()

def process_user_request():
    """Processes POST request with user data to get AI plan recommendations."""
    try:
        form_data = request.json
        if not form_data:
            return jsonify({"error": "No JSON data received"}), 400
        print("Received form data:", form_data)

        # --- Validate Input Data ---
        required_fields = ['name', 'age', 'state', 'income', 'dentalPlanRequired', 'consentGiven']
        missing_fields = [field for field in required_fields if field not in form_data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        state = form_data.get('state')
        dental_required = str(form_data.get('dentalPlanRequired', 'no')).lower() # Ensure lowercase 'yes'/'no'

        # --- Query MongoDB ---
        query = {"StateCode": state}
        # Define dental benefit names consistently
        dental_benefits = [
            "Routine Dental Services (Adult)", "Dental Check-Up for Children",
            "Basic Dental Care - Child", "Orthodontia - Child", "Major Dental Care - Child",
            "Basic Dental Care - Adult", "Orthodontia - Adult", "Major Dental Care - Adult",
            "Accidental Dental"
        ]
        if dental_required == 'yes':
            query['BenefitName'] = {'$in': dental_benefits}
            print(f"Querying for plans in {state} INCLUDING dental benefits.")
        elif dental_required == 'no':
             # If dental is not required, we don't need to filter based on BenefitName,
             # as we want plans regardless of their dental coverage.
             # query['BenefitName'] = {'$nin': dental_benefits} # This would EXCLUDE plans with ONLY dental
             print(f"Querying for all plans in {state} (dental not required).")
        else:
             # Handle cases where dentalPlanRequired is neither 'yes' nor 'no' if necessary
             print(f"Querying for all plans in {state} (dental requirement unclear: '{dental_required}').")


        # Fetch data - consider adding a limit if datasets are huge
        # Limit added for safety, adjust as needed
        plan_data_cursor = benefits_collection.find(query).limit(500)
        plan_data_list = list(plan_data_cursor)

        # Convert MongoDB BSON/ObjectId to JSON serializable format
        json_serializable_data = json.loads(json_util.dumps(plan_data_list))

        if not json_serializable_data:
            print(f"No plans found for state: {state} with dental preference: {dental_required}")
            return jsonify({
                "status": "info",
                "message": f"No matching plans found for state {state} based on your criteria.",
                "plans": []
            }), 200 # Return 200 OK, but with info message

        print(f"Found {len(json_serializable_data)} plan entries for state: {state} matching criteria.")

        # --- Convert to Pandas DataFrame ---
        # Important: Ensure ObjectId '_id' is handled if needed downstream,
        # otherwise it might be better to exclude it or convert it to string earlier.
        # For AI analysis, ObjectId is likely not needed.
        plans_df = pd.DataFrame(json_serializable_data)
        # Drop MongoDB ObjectId if not needed for analysis
        if '_id' in plans_df.columns:
             plans_df = plans_df.drop(columns=['_id'])


        # --- Call AI Agent ---
        print("Calling AI Agent for analysis...")
        # Pass the DataFrame directly
        ai_response = decisionAgent(form_data, plans_df)

        if not ai_response or "error" in ai_response:
            print(f"AI Agent error: {ai_response.get('error', 'Unknown error')}")
            # Return raw output if available and it was a JSON decode error
            if "raw_output" in ai_response:
                 return jsonify({
                    "status": "error",
                    "message": "AI analysis failed to produce valid JSON.",
                    "raw_agent_output": ai_response["raw_output"]
                 }), 500
            return jsonify({
                "status": "error",
                "message": f"AI analysis failed: {ai_response.get('error', 'Unknown error')}"
            }), 500

        print("AI Agent analysis complete.")
        # --- Return Response ---
        return jsonify({
            "status": "success",
            "message": f"Processed {len(json_serializable_data)} plan entries for state: {state}. AI analysis complete.",
            "analysis": ai_response # Return the structured JSON from the agent
        })

    except Exception as e:
        print(f"Error processing form data: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

def get_filtered_benefits():
    """Handles GET request to fetch plan data based on query parameters."""
    try:
        print("Attempting to query data collection (GET)")
        query = {}
        # --- Extract Query Parameters ---
        state_code = request.args.get('state')
        # Add other potential filters from your original GET logic if needed
        # plan_type = request.args.get('planType')
        # min_premium = request.args.get('minPremium', type=float)
        # max_premium = request.args.get('maxPremium', type=float)
        dental_required = request.args.get('dentalRequired')

        if state_code:
            query["StateCode"] = state_code
        # Add logic for other filters like plan_type, premium range etc. here

        # Handle dental filter for GET request (similar to POST)
        if dental_required:
            dental_benefits = [
                "Routine Dental Services (Adult)", "Dental Check-Up for Children",
                "Basic Dental Care - Child", "Orthodontia - Child", "Major Dental Care - Child",
                "Basic Dental Care - Adult", "Orthodontia - Adult", "Major Dental Care - Adult",
                "Accidental Dental"
            ]
            if dental_required.lower() == 'yes':
                query['BenefitName'] = {'$in': dental_benefits}
            elif dental_required.lower() == 'no':
                # Decide if 'no' means exclude dental-only plans or include all
                 pass # Currently includes all if 'no'

        print("Executing query (GET):", query)
        # Add a limit to prevent overwhelming responses
        data = list(benefits_collection.find(query).limit(200))
        # Convert BSON/ObjectId to JSON serializable format
        json_data = json.loads(json_util.dumps(data))
        print(f"Successfully retrieved {len(json_data)} records (GET)")
        return jsonify(json_data)

    except Exception as e:
        print(f"Error querying MongoDB (GET): {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "Failed to retrieve data.", "details": str(e)}), 500


@app.route("/api/medicaid_and_chip_eligibility", methods=["GET"])
def get_medicaid_and_chip_eligibility():
    """Fetches Medicaid/CHIP eligibility data based on state."""
    # This route remains largely the same as your original code
    try:
        print("Attempting to query Medicaid/CHIP data")
        query = {}
        state_code = request.args.get('state')

        if state_code:
            # Ensure the field name matches your MongoDB collection
            query["State"] = state_code # Or "StateCode" if that's the field name

        data = list(eligibility_collection.find(query))
        json_data = json.loads(json_util.dumps(data))
        print(f"Successfully retrieved {len(json_data)} Medicaid/CHIP data")
        return jsonify(json_data)
    except Exception as e:
        print(f"Error querying Medicaid/CHIP data: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "Failed to retrieve eligibility data.", "details": str(e)}), 500
