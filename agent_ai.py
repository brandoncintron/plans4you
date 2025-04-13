import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
import json
import re

from pymongo import MongoClient
#from api_key import API_KEY

# Configure your API key using the environment variable (recommended)
genai.configure(api_key = "AIzaSyCYZh91HS2a5fCiojtoVWsPbpBwnrmZLL4")

# Now you can use the GenerativeModel class to interact with Gemini
GEMINI_MODEL = genai.GenerativeModel("gemini-2.0-flash") # Or your preferred model

def format_plans_for_agent_prompt(plans, user_profile):
    formatted_list = []
    for plan in plans:
        formatted_list.append(json.dumps(plan, indent=2))
    return "\n---\n".join(formatted_list)


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
    As a helpful insurance agent, recommend the top 5-10 policies from the following: {policies}
    Consider the user's needs: {userProfile}
    For each recommendation, concisely explain key features, benefits, and drawbacks, highlighting why it's suitable.
    Write maximum 2-3 paragraphs.
    """
    formatted_prompt = prompt.format(userProfile=userProfile, policies=policies)

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)
        return response
    except Exception as e:
        print(f"Error during Gemini API call (Insurance Agent): {e}")
        return None

def financialAgent(userProfile, policies):
    income = userProfile.get('income')

    prompt = """
    As a financial advisor, analyze the cost-effectiveness and long-term financial implications of the following top 5-10 policies: {policies}
    Considering the user's income of ${income}, explain the value proposition of each and why one might be preferred over another.
    Write maximum 2-3 paragraphs.
    """
    formatted_prompt = prompt.format(income=income, policies=policies)

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)
        return response
    except Exception as e:
        print(f"Error during Gemini API call (Financial Agent): {e}")
        return None


def decisionAgent(userProfile, insurance_explanation, financial_analysis, all_plans):
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
    Based on the following information for {userProfile['name']} (age {userProfile['age']}, income ${userProfile['income']}, wants dental: {userProfile.get('dentalPlanRequired', 'no') if userProfile.get('dentalPlanRequired') else 'no'}):

    (Note: The following plans have already been filtered based on your reported income and location.)

    **Insurance Agent Explanation:**
    {insurance_text}

    **Financial Analysis:**
    {financial_text}

    **Available Plans:**
    {format_plans_for_agent_prompt(all_plans, userProfile)}

    Your task is to:
    1. Identify the single best medical insurance plan for {userProfile['name']}, considering coverage and affordability.
    2. Rank the remaining mentioned plans from 2nd best to least suitable based on the same criteria.
    3. For each plan in the ranked list, provide a concise and detailed justification easily understandable (4-5 sentences) explaining its ranking based on the combined analysis from the insurance and financial perspectives, referencing details from the 'Available Plans' where necessary.

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
    ```
    """
    formatted_prompt = prompt

    try:
        response = GEMINI_MODEL.generate_content(formatted_prompt)
        if response.text:
            try:
                json_output = json.loads(response.text)
                return {"ranked_plans": json_output["ranked_plans"], "best_plan_id": json_output.get("best_plan_id")} # Ensure consistent output structure
            except json.JSONDecodeError:
                print("Error: Gemini output was not valid JSON. Returning raw text.")
                return {"raw_output": response.text}
        else:
            return {"error": "No response text from Gemini."}
    except Exception as e:
        print(f"Error during Gemini API call (Decision Agent): {e}")
        return {"error": str(e)}
