from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
import json
from bson import json_util
import traceback
import os
from flask_cors import CORS  # Import CORS
# Import pandas and AI-related libraries
# import pandas as pd
# import your_ai_library  # e.g., scikit-learn, tensorflow, etc.

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
CORS(app)  # Enable CORS for all routes

@app.route("/api/test")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/benefits_and_cost_sharing", methods=["GET", "POST"])
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
                
            data = list(benefits_and_cost_sharing.data.find({"StateCode": "FL"}).limit(200))
            
            # Feed the data variable into the AI for manipulation (without the limit)
            
            
            json_data = json.loads(json_util.dumps(data))
            
            print(f"Successfully retrieved {len(json_data)} data")
            return jsonify(json_data)
        except Exception as e:
            print(f"Error querying MongoDB: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500
        
    elif request.method == "POST":
        try:
            # Get the form data from the request
            form_data = request.json
            print("Received form data:", form_data)
            
            # Get state from form data and filter plans by state if provided
            state = form_data.get('state')
            print(f"State from form data: {state}")

            # Query plans data filtered by state
            data = list(benefits_and_cost_sharing.data.find({"StateCode": state}).limit(20))
            print(f"Found {len(data)} plans for state: {state}")
            
            # Convert ObjectId to string for JSON serialization
            json_data = json.loads(json_util.dumps(data))
            print(f"Successfully retrieved {len(json_data)} data")
            
        
            # TODO: STEP 1 - Convert form_data to a pandas DataFrame
            # Example: df = pd.DataFrame([form_data]) or appropriate structure based on your data
            
            # TODO: STEP 2 - Query relevant plan data from MongoDB to compare against
            # Example: plans_df = pd.DataFrame(plans_data)
            
            # TODO: STEP 3 - Process data with your AI model
            # This could involve:
            # 1. Feature engineering/preprocessing of user input and plan data
            # 2. Running your trained model or algorithm to rank plans
            # 3. Generating explanations/justifications for each plan
            
            # TODO: STEP 4 - Format AI results into the required "plans" array structure
            # Each plan should have planId, rank, potentially isBestPlan, and justification
            
            # For testing, use filtered data if available, otherwise use hardcoded examples
            plan_list = []
            
            if json_data and len(json_data) > 0:
                # Use the first two filtered plans
                unique_plan_ids = set()
                for plan in json_data:
                    plan_id = plan.get("PlanId")
                    if plan_id and plan_id not in unique_plan_ids and len(unique_plan_ids) < 2:
                        unique_plan_ids.add(plan_id)
                        plan_list.append({
                            "planId": plan_id,
                            "rank": len(unique_plan_ids),
                            "isBestPlan": len(unique_plan_ids) == 1,
                            "justification": f"This is a plan from {state} that matches your criteria."
                        })
            
            # If no filtered plans were found, use hardcoded examples
            if not plan_list:
                plan_list = [
                    {
                        "planId": "46944AL0280001",
                        "rank": 1,
                        "isBestPlan": True,
                        "justification": "This is the best option because it balances predictable costs with solid coverage. Since isn't expecting major health issues, the set copays ($20 for primary care, $30 for specialists) are manageable and prevent surprise bills. Crucially, it covers major services like transplant and cancer treatment at no charge, which is a huge safety net. Plus, generic drugs are only $10. Imagine needs a routine checkup and a prescription; knows exactly what will pay, and if something serious happens,'s mostly covered."
                    },
                    {
                        "planId": "46944AL0370001",
                        "rank": 2,
                        "justification": "This plan offers the benefit of a copay-only system, meaning that could better budget healthcare expenses. This predictability could be more appealing to those who value financial planning. The copays are consistent, making it easy to budget, but the imaging fee is higher, which may not be ideal if needs imaging regularly. Consider this scenario: If requires imaging after an accident would have to pay $300 at an imaging facility."
                    }
                ]
            
            return jsonify({
                "status": "success",
                "message": f"Found {len(json_data)} plans for state: {state}",
                "plans": plan_list
            })
        except Exception as e:
            print(f"Error processing form data: {str(e)}")
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