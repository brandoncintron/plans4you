import pandas as pd
import json
from agent_ai import insuranceAgent, financialAgent, decisionAgent

import pandas as pd

# Load datasets
benefits_df = pd.read_csv("benefits-and-cost-sharing-puf.csv", dtype=str, low_memory=False)
eligibility_df = pd.read_csv("medicaid-and-chip-eligibility-levels.xy8t-auhk.csv", dtype=str)

# Strip whitespace
benefits_df.columns = benefits_df.columns.str.strip()
eligibility_df.columns = eligibility_df.columns.str.strip()
benefits_df['StandardComponentId'] = benefits_df['StandardComponentId'].str.strip()

# ------------------------------------
# User Input
# ------------------------------------
print("\nWelcome to Plan4You!\n")
name = input("👤 What is your name? ")
age = int(input("🎂 How old are you? "))
dependents = int(input("🏠 How many dependents live with you? "))
income = float(input("💰 What is your total annual household income (in USD)? "))
state = input("🏙️ What state do you live in? (e.g., FL): ").strip().upper()
wants_dental = input("🦷 Do you want dental coverage? (yes/no): ").strip().lower()

def getUserProfile():
    """
    Collects user profile information and stores it in a dictionary.
    """
    user_profile = {
        "name": name,
        "age": age,
        "dependents": dependents,
        "income": income,
        "state": state,
        "wants_dental": wants_dental
    }
    return user_profile
# ------------------------------------
# Household Calculations
# ------------------------------------
household_size = 1 + dependents
fpl_base = 14580
fpl_additional = 5140
fpl = fpl_base + (household_size - 1) * fpl_additional
fpl_percent = round((income / fpl) * 100, 1)

print(f"\n📊 {name}, your household size is {household_size} and your income is {fpl_percent}% of the Federal Poverty Level.\n")

# ------------------------------------
# Medicaid/CHIP Eligibility
# ------------------------------------
state_elig = eligibility_df[eligibility_df['State'].str.upper() == state]
is_medicaid_eligible = False
is_chip_eligible = False

if not state_elig.empty:
    row = state_elig.iloc[0]
    try:
        if age <= 1 and fpl_percent <= float(row['Medicaid Ages 0-1'].replace('%','').strip()):
            is_medicaid_eligible = True
        elif 1 < age <= 5 and fpl_percent <= float(row['Medicaid Ages 1-5'].replace('%','').strip()):
            is_medicaid_eligible = True
        elif 5 < age <= 18 and fpl_percent <= float(row['Medicaid Ages 6-18'].replace('%','').strip()):
            is_medicaid_eligible = True
        elif age <= 18 and fpl_percent <= float(row['Separate CHIP'].replace('%','').strip()):
            is_chip_eligible = True
    except Exception as e:
        print("Error during eligibility conversion:", e)
else:
    print("⚠️ Eligibility data not found for your state.")

if is_medicaid_eligible:
    print("✅ You may be eligible for Medicaid in your state.")
elif is_chip_eligible:
    print("✅ You may be eligible for CHIP (Children's Health Insurance Program).")
else:
    print("❌ You may not qualify for Medicaid or CHIP.")

# ------------------------------------
# Filter Plans
# ------------------------------------
state_filtered = benefits_df[benefits_df['StateCode'].str.upper() == state]

dental_benefits = [
    "Routine Dental Services (Adult)", "Dental Check-Up for Children", "Basic Dental Care - Child",
    "Orthodontia - Child", "Major Dental Care - Child", "Basic Dental Care - Adult",
    "Orthodontia - Adult", "Major Dental Care - Adult", "Accidental Dental"
]

if wants_dental == "yes":
    state_filtered = state_filtered[state_filtered['BenefitName'].isin(dental_benefits)]
else:
    state_filtered = state_filtered[~state_filtered['BenefitName'].isin(dental_benefits)]

if not (is_medicaid_eligible or is_chip_eligible):
    state_filtered = state_filtered[
        (state_filtered['IsCovered'].str.lower() == 'covered') &
        (
            state_filtered['CopayInnTier1'].notna() |
            state_filtered['CoinsInnTier1'].notna()
        )
    ]

# De-duplicate
state_filtered = state_filtered.drop_duplicates(subset=['StandardComponentId', 'BenefitName'])

# ------------------------------------
# Scoring Logic
# ------------------------------------
def score_plan(df):
    score = 0
    for _, row in df.iterrows():
        if row['IsCovered'].strip().lower() == 'covered':
            score += 2
            if str(row['CopayInnTier1']).strip() in ['No Charge', '$0.00', '0.00']:
                score += 2
            elif pd.notna(row['CopayInnTier1']):
                score += 1
            if str(row['CoinsInnTier1']).strip() in ['0.00%', '0.00% Coinsurance after deductible', '0.00%']:
                score += 2
            elif pd.notna(row['CoinsInnTier1']):
                score += 1
    return score

# Score each plan
top_scores = []
for plan_id in state_filtered['StandardComponentId'].unique():
    plan_data = state_filtered[state_filtered['StandardComponentId'] == plan_id]
    score = score_plan(plan_data)
    top_scores.append((plan_id, score))

top_scores.sort(key=lambda x: x[1], reverse=True)
top_10 = top_scores[:10]

# ------------------------------------
# Display Top 10 Plans
# ------------------------------------
print(f"\n📦 Top 10 Plans Matching Your Criteria:\n")
for plan_id, score in top_10:
    plan_data = state_filtered[state_filtered['StandardComponentId'] == plan_id]
    print(f"\n==============================\nPlan ID: {plan_id} (Score: {score})")
    for _, row in plan_data.iterrows():
        print(f"- Benefit: {row['BenefitName']}")
        print(f"  Covered: {row['IsCovered']}")
        print(f"  Copay Tier 1: {row['CopayInnTier1']}")
        print(f"  Coinsurance Tier 1: {row['CoinsInnTier1']}\n")

print(f"\n🎯 Displayed Top {len(top_10)} Plans.")

def format_plans_for_ai(df):
    plans_list = []
    for pid in df['StandardComponentId'].dropna().unique():
        plan_df = df[df['StandardComponentId'] == pid]
        benefits = []
        plan_info = {"Plan ID": pid, "benefits": []}
        for _, row in plan_df.iterrows():
            benefit = {
                "BenefitName": row['BenefitName'],
                "IsCovered": row['IsCovered'],
                "CopayInnTier1": row['CopayInnTier1'],
                "CoinsInnTier1": row['CoinsInnTier1']
            }
            plan_info["benefits"].append(benefit)
        plans_list.append(plan_info)
    return plans_list

filtered_plans_list = format_plans_for_ai(state_filtered)

# ------------------------------------
# Agent Explanations (Using Filtered List)
# ------------------------------------
def format_plans_for_agent_prompt(plans, user_profile):
    formatted_list = []
    for plan in plans:
        formatted_list.append(json.dumps(plan, indent=2))
    return "\n---\n".join(formatted_list)
    
if filtered_plans_list:
    user_profile = getUserProfile()  # Call getUserProfile here to get the user data
    formatted_plans_prompt = format_plans_for_agent_prompt(filtered_plans_list, user_profile)
    insurance_recommendation = insuranceAgent(user_profile, formatted_plans_prompt)
    financial_analysis = financialAgent(user_profile, formatted_plans_prompt)

    decision_result = decisionAgent(
        user_profile,
        insurance_recommendation.text if insurance_recommendation else "No insurance explanation.",
        financial_analysis.text if financial_analysis else "No financial analysis."
    )

    if "raw_output" in decision_result:
        print("\n\n**Decision Agent - Raw Output (Invalid JSON):**\n", decision_result["raw_output"])
    elif "error" in decision_result:
        print("\n\n**Decision Agent - Error:**\n", decision_result["error"])
    else:
        print("\n\n**Decision Agent - JSON Output:**\n", json.dumps(decision_result, indent=4))
        # Here you would typically pass the decision_result dictionary to your Flask app

else:
    print("\nNo matching plans found based on your criteria.")