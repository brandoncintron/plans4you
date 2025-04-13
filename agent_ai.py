import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
import json
import re

from pymongo import MongoClient
#from api_key import API_KEY

# Configure your API key using the environment variable (recommended)
genai.configure(api_key = "AIzaSyBt82sjZYHLLHNrBelLjooQPizhd8mLhaA")

# Now you can use the GenerativeModel class to interact with Gemini
GEMINI_MODEL = genai.GenerativeModel("gemini-2.0-flash") # Or your preferred model

def queryAgent(userProfile):

    prompt = """
    You are a MongoDB query generator that creates a query object to extract matching information regarding medical insurances..

    User Profile: {userProfile}

    Based on the keys and values in the user profile, construct a MongoDB query object to find matching insurance policies in the policies database.
    The has documents with the following fields (examples):
    [NEED TO ADD LIST OF COLUMN HERE]

    Return ONLY the MongoDB query object as a JSON string. Do not include any explanations or other text.
    """

    formatted_prompt = prompt.format(userProfile=userProfile)

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)

        if response.text:
            mongo_query = response.text.strip()
            return mongo_query
        else:
            print("Error: Gemini API did not return a Mongo query.")
            return None
        
    except Exception as e:
        print(f"Error during Gemini API call for Mongo generation: {e}")
        return None
    
# function to execute the query against MongoDB:
def find_matching_policies_mongodb(mongo_query, db):
    if mongo_query is None:
        return []
    policies = db.insurance_policies.find(mongo_query)
    return list(policies)

# Establish MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]

def find_matching_policies(userProfile, db):
    # Generate the MongoDB query using Gemini
    mongo_query = queryAgent(userProfile)

    if mongo_query:
        print("Generated MongoDB Query:")
        print(json.dumps(mongo_query, indent=4))

        # Use the generated query to find matching policies in MongoDB
        matching_policies = find_matching_policies_mongodb(mongo_query, db)

        if matching_policies:
            print("\nMatching Policies:")
            print(json.dumps(list(matching_policies), indent=4))
        else:
            print("\nNo matching policies found in MongoDB.")
    else:
        print("Failed to generate MongoDB query.")

    client.close()
    return matching_policies


#details can be changed
def format_plans_for_agent_prompt(plans, user_profile):
    formatted_list = []
    for plan in plans:
        formatted_list.append(json.dumps(plan, indent=2))
    return "\n---\n".join(formatted_list)


def insuranceAgent(userProfile, policies):
    prompt = """
    As a helpful insurance agent, recommend the top 5-10 policies from the following: {policies}
    Consider the user's needs: {userProfile}
    For each recommendation, concisely explain key features, benefits, and drawbacks, highlighting why it's suitable.
    Write maximum 2-3 paragarphs
    """
    ##policies = format_policies_for_prompt(policies)
    formatted_prompt = prompt.format(userProfile=userProfile,policies=policies) #

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)

        return response
            
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None

def financialAgent(userProfile, policies):

    income = userProfile.get('income')

    prompt = """
    As a financial advisor, analyze the cost-effectiveness and long-term financial implications of the following top 5-10 policies: {policies}
    Considering the user's income of ${income}, explain the value proposition of each and why one might be preferred over another.
    Write maximum 2-3 paragarphs
    """
    #policies = format_policies_for_prompt(policies)
    formatted_prompt = prompt.format(income=income,policies=policies)

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)

        return response
            
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None


def decisionAgent(userProfile, insurance_explanation, financial_analysis):
    insurance_text = insurance_explanation.text if isinstance(insurance_explanation, GenerateContentResponse) else str(insurance_explanation) if insurance_explanation else "No insurance explanation."
    financial_text = financial_analysis.text if isinstance(financial_analysis, GenerateContentResponse) else str(financial_analysis) if financial_analysis else "No financial analysis."

    # 1. Extract Unique Plan IDs
    insurance_plan_ids = set(re.findall(r"Plan ID: (\S+)", insurance_text))
    financial_plan_ids = set(re.findall(r"Plan ID: (\S+)", financial_text))
    unique_plan_ids = sorted(list(insurance_plan_ids.union(financial_plan_ids)))

    plan_analysis = {}

    # 2. Store Analysis per Unique ID (Improved Extraction)
    for plan_id in unique_plan_ids:
        insurance_matches = re.findall(rf"(?:Plan ID:\s*{re.escape(plan_id)})(.*?)(?:Plan ID:|$)", insurance_text, re.DOTALL)
        financial_matches = re.findall(rf"(?:Plan ID:\s*{re.escape(plan_id)})(.*?)(?:Plan ID:|$)", financial_text, re.DOTALL)

        insurance_info = " ".join(m.strip() for match in insurance_matches for m in match.strip().split() if match.strip())
        financial_info = " ".join(m.strip() for match in financial_matches for m in match.strip().split() if match.strip())

        plan_analysis[plan_id] = {"insurance": insurance_info, "financial": financial_info}

    prompt = f"""
    Based on the following information for {userProfile['name']} (age {userProfile['age']}, income ${userProfile['income']}, wants dental: {userProfile['wants_dental']}):

    (Note: The following plans have already been filtered based on your reported income and location.)

    **Insurance Agent Explanation:**
    {insurance_text}

    **Financial Analysis:**
    {financial_text}

    Your task is to:
    1. Identify the single best medical insurance plan for {userProfile['name']}, considering coverage and affordability.
    2. Rank the remaining mentioned plans from 2nd best to least suitable based on the same criteria.
    3. For each plan in the ranked list, provide a concise and detailed justification easily understandable (4-5 sentences) explaining its ranking based on the combined analysis from the insurance and financial perspectives.

    Present your output *EXACTLY* as a valid JSON object with the following structure, and nothing else. Do not include any introductory or concluding remarks, explanations outside the JSON, or any markdown formatting like code blocks unless they are part of the JSON string values.

    ```json
    {{
    "best_plan_id": "...",
    "ranked_plans": [
        {{
        "plan_id": "...",
        "justification": "..."
        }},
        {{
        "plan_id": "...",
        "justification": "..."
        }},
        ...
    ]
    }}
    """
    formatted_prompt = prompt

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)
        if response.text:
            try:
                json_output = json.loads(response.text)
                return json_output
            except json.JSONDecodeError:
                print("Error: Gemini output was not valid JSON. Returning raw text.")
                return {"raw_output": response.text}
        else:
            return {"error": "No response text from Gemini."}
    except Exception as e:
        print(f"Error during Gemini API call (Decision Agent): {e}")
        return {"error": str(e)}
