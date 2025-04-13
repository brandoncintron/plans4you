import os
import json
import traceback
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (specifically the API key)
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# --- Configure Gemini API ---
if google_api_key:
    try:
        genai.configure(api_key=google_api_key)
        # Select the Gemini model
        GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-flash-latest")
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        GEMINI_MODEL = None # Ensure model is None if config fails
else:
    print("Error: GOOGLE_API_KEY environment variable not set. AI Agent will not function.")
    GEMINI_MODEL = None

def decisionAgent(user_profile: dict, plans_data: list):
    """
    Analyzes insurance plans based on user profile using Gemini AI.

    Args:
        user_profile: A dictionary containing user information
                      (e.g., name, age, income, state, dependents, dentalPlanRequired).
        plans_data: A list of dictionaries containing the filtered insurance plan data.

    Returns:
        A dictionary containing the AI's analysis (best plan ID, ranked list with justifications)
        or an error dictionary.
    """
    if not GEMINI_MODEL:
        return {"error": "Gemini AI Model is not configured. Check API Key."}

    if not plans_data:
        return {"error": "No plan data provided to the agent."}

    # --- Prepare Data for Prompt ---
    try:
        # Filter and transform the plans data
        relevant_fields = [
            'PlanId', 'BenefitName', 'CopayInnTier1', 'CoinsInnTier1',
            'IsCovered', 'QuantLimitOnSvc', 'LimitQty', 'LimitUnit', 'Explanation',
            'IssuerId', 'StandardComponentId'
        ]
        
        filtered_plans = []
        for plan in plans_data:
            filtered_plan = {}
            for field in relevant_fields:
                if field in plan:
                    # Rename PlanId to planId for consistency
                    if field == 'PlanId':
                        filtered_plan['planId'] = plan[field]
                    else:
                        filtered_plan[field] = plan[field]
            filtered_plans.append(filtered_plan)
            
        # Convert plans to JSON string with proper formatting
        plans_json_str = json.dumps(filtered_plans, indent=2)

        # Limit the size of the plans data sent to the model if necessary
        max_chars = 15000 # Adjust based on model context window
        if len(plans_json_str) > max_chars:
             print(f"Warning: Plan data size ({len(plans_json_str)} chars) exceeds limit ({max_chars}). Truncating.")
             plans_json_str = plans_json_str[:max_chars] + "\n... (data truncated)"

    except Exception as e:
        print(f"Error preparing plan data for prompt: {e}")
        return {"error": f"Failed to process plan data for AI analysis: {e}"}

    # --- Construct the Prompt ---
    user_name = user_profile.get('name', 'the user')
    user_age = user_profile.get('age', 'unknown age')
    user_income = user_profile.get('income', 'unknown income')
    user_dependents = user_profile.get('dependents', 'unknown number of')
    user_state = user_profile.get('state', 'unknown state')
    user_dental = 'Yes' if str(user_profile.get('dentalPlanRequired', 'no')).lower() == 'yes' else 'No'

    # **Updated Prompt Instructions**
    prompt = f"""
    You are an expert AI health insurance and benefits advisor. Your goal is to analyze a list of potential health benefits in various insurance plans and recommend the best options for a specific user based on their profile and the plan details.

    **User Profile:**
    * Name: {user_name}
    * Age: {user_age}
    * Annual Income: {user_income}
    * Number of Dependents: {user_dependents}
    * State: {user_state}
    * Requires Dental Coverage: {user_dental}

    **Available Insurance Plans (filtered for the user's state and dental preference):**
    ```json
    {plans_json_str}
    ```

    **Your Task:**

    Analyze the provided insurance plans based *only* on the user's profile and the details given in the JSON above. Consider factors like coverage, cost-sharing, limitations, and overall suitability.

    **Output Requirements:**

    Provide your analysis *strictly* in the following JSON format. Use "planId" (camelCase) for the plan identifier. For the plan identified as the best, add `"isBestPlan": true`. For all other plans in the ranked list, add `"isBestPlan": false`. Do not include any introductory text, explanations outside the JSON structure, or markdown formatting (` ```json ... ```) around the final JSON output.

    ```json
    {{
        "best_plan_id": "...",
        "ranked_plans": [
            {{
                "planId": "...", // Use camelCase
                "rank": 1,
                "isBestPlan": true, // Add this boolean field
                "justification": "Concise explanation (3-5 sentences) why this plan is ranked here, referencing specific user needs and plan details (e.g., costs, coverage, limits) from the provided JSON data."
            }},
            {{
                "planId": "...", // Use camelCase
                "rank": 2,
                "isBestPlan": false, // Add this boolean field
                "justification": "Concise explanation (3-5 sentences)..."
            }}
            // Include rankings for up to the top 5-10 most suitable plans found in the data.
            // Only include plans mentioned in the input JSON data. Ensure all ranked plans have the "isBestPlan" field.
        ]
    }}
    ```

    **Instructions:**
    * Identify the single best plan and put its 'planId' in `best_plan_id`.
    * Create a ranked list (`ranked_plans`) starting with the best plan (rank 1). Include the Plan ID (`planId` - camelCase), the rank number (`rank`), the boolean `isBestPlan` field, and a `justification`.
    * Base your justifications *only* on the provided user profile and plan data JSON. Explain why the chosen plan is the best in terms of the benefits provided both medically and in an cost effective manner. Be specific.
    * Ensure the `planId` values exactly match those in the input JSON data.
    """

    # --- Call Gemini API ---
    print("Sending request to Gemini API...")
    try:
        # Set safety_settings to allow potentially sensitive content if needed, e.g., financial info
        # Be mindful of safety implications. Adjust categories and thresholds as necessary.
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        response = GEMINI_MODEL.generate_content(prompt, safety_settings=safety_settings)


        # --- Process Response ---
        if not response.candidates or not response.candidates[0].content.parts:
             # Check for safety blocks
             if response.prompt_feedback.block_reason:
                  print(f"Error: Gemini request blocked due to {response.prompt_feedback.block_reason}")
                  print(f"Safety Ratings: {response.prompt_feedback.safety_ratings}")
                  return {"error": f"AI request blocked due to safety settings ({response.prompt_feedback.block_reason})."}
             else:
                  print("Error: Gemini response is empty or malformed.")
                  print(f"Full Response: {response}")
                  return {"error": "Received an empty or invalid response from the AI model."}


        raw_text = response.text
        print(f"Raw Gemini Output:\n---\n{raw_text}\n---") # Log the raw output

        # Attempt to parse the JSON response
        try:
            # Clean potential markdown code fences
            cleaned_text = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
            json_output = json.loads(cleaned_text)

            # --- Validate JSON Structure ---
            required_top_keys = ["best_plan_id", "ranked_plans"]
            if not all(key in json_output for key in required_top_keys):
                print(f"Error: Gemini output is missing required top-level JSON keys: {required_top_keys}.")
                return {"error": "AI response missing required structure.", "raw_output": raw_text}

            if not isinstance(json_output["ranked_plans"], list):
                 print("Error: 'ranked_plans' key in Gemini output is not a list.")
                 return {"error": "AI response 'ranked_plans' is not a list.", "raw_output": raw_text}

            # Validate structure of items within ranked_plans
            required_plan_keys = ["planId", "rank", "isBestPlan", "justification"]
            for i, item in enumerate(json_output["ranked_plans"]):
                if not isinstance(item, dict):
                    print(f"Error: Item at index {i} in 'ranked_plans' is not a dictionary.")
                    return {"error": f"Invalid item type in 'ranked_plans' at index {i}.", "raw_output": raw_text}
                if not all(key in item for key in required_plan_keys):
                     missing_keys = [key for key in required_plan_keys if key not in item]
                     print(f"Warning: Ranked plan item at index {i} missing keys: {missing_keys}. Item: {item}")
                     # Return error if structure is critical
                     return {"error": f"Ranked plan item at index {i} missing required keys: {missing_keys}.", "raw_output": raw_text}
                if not isinstance(item.get("isBestPlan"), bool):
                    print(f"Warning: 'isBestPlan' in item at index {i} is not a boolean. Item: {item}")
                    # Return error or attempt to coerce/default
                    return {"error": f"'isBestPlan' field is not a boolean in ranked plan item at index {i}.", "raw_output": raw_text}


            print("Successfully parsed and validated JSON response from Gemini.")
            return json_output # Return the validated and parsed JSON

        except json.JSONDecodeError as json_err:
            print(f"Error: Failed to decode Gemini response as JSON: {json_err}")
            print(f"Problematic Text: {raw_text}") # Log the text that failed parsing
            # Return the raw text along with the error message
            return {"error": "AI response was not valid JSON.", "raw_output": raw_text}

    except Exception as e:
        # Catch potential errors from the API call itself (e.g., network issues, permission errors)
        print(f"Error during Gemini API call or processing: {e}")
        print(traceback.format_exc())
        # Check if it's a specific Google API error
        if hasattr(e, 'message'):
            error_message = e.message
        else:
            error_message = str(e)
        return {"error": f"An unexpected error occurred during AI analysis: {error_message}"}

