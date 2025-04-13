import google.generativeai as genai
import json

from pymongo import MongoClient
from api_key import API_KEY

# Configure your API key using the environment variable (recommended)
genai.configure(API_KEY)

# Now you can use the GenerativeModel class to interact with Gemini
GEMINI_MODEL = genai.GenerativeModel("gemini-2.0-flash") # Or your preferred model

def queryAgent(userProfile):

    prompt = """
    You are a MongoDB query generator that creates a query object to extract matching information regarding medical insurances..

    User Profile: {userProfie}

    Based on the keys and values in the user profile, construct a MongoDB query object to find matching insurance policies in the policies database.
    The has documents with the following fields (examples):
    [NEED TO ADD LIST OF COLUMN HERE]

    Return ONLY the MongoDB query object as a JSON string. Do not include any explanations or other text.
    """

    formatted_prompt = prompt.format(userProfie=userProfile)

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
def format_policies_for_prompt(policies):
    policies_list = []
    for policy in policies:
        plan_data = {"Plan ID": policy.get("Plan ID", "N/A"), "benefits": []}
        for benefit_item in policy.get("benefits", []):
            benefit_data = {
                "Benefit": benefit_item.get("Benefit", "N/A"),
                "Covered": benefit_item.get("Covered", "N/A"),
                "Copay Tier 1": benefit_item.get("Copay Tier 1", "N/A"),
                "Coinsurance Tier 1": benefit_item.get("Coinsurance Tier 1", "N/A"),
                # Add other relevant benefit details if present
            }
            plan_data["benefits"].append(benefit_data)
        policies_list.append(plan_data)
    return json.dumps(policies_list, indent=2) # indent for readability (optional)


def insuranceAgent(userProfile, policies):
    prompt = """
    You are a knowledgeable and friendly medical insurance agent who has reccomends the best policy by explaining it out.

    You main goals is to assists clients in selecting insurance policies that best meets their needs, preferences and budgets
    
    Based on the following insurance policies:
      {policies} 
    and the user's needs:
      {userProfile}
      
    Explain the key features, benefits, and drawbacks of each policy in a clear and concise manner. 
    Highlight the policies that seem most suitable and explain why. Give top 5-10 policies. 
    """
    ##policies = format_policies_for_prompt(policies)
    formatted_prompt = prompt.format(userProfie=userProfile,policies=policies) #

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)

        return response
            
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None

def financialAgent(userProfile, policies):

    income = userProfile.get('income')

    prompt = """
    You are a qualified financial advisor. 
    Considering the user's financial situation whose income is ${income} from user data and insurance needs, analyze the cost effectiveness of the recommended policies {policies}. 
    Discuss the long term financial implications of each option and help user understand the value proposition and why they should prefer one policy over another. 
    """
    #policies = format_policies_for_prompt(policies)
    formatted_prompt = prompt.format(income=income,policies=policies)

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)

        return response
            
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None

def legalAgent(policies):
    prompt = """"
    You are an expert in insurance regulations and compliance. 
    Review the following recommended policies {policies} and ensure they align with standard industry practices and legal requirements. 
    Highlight any potential red flags or important legal considerations the user should be aware of (e.g., exclusions, waiting periods).
    """
    
    #policies = format_policies_for_prompt(policies)
    formatted_prompt = prompt.format(policies)

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)

        return response
            
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None


