# Plan4You Backend – AI-Powered Health Insurance Recommendation API

**Plan4You** is an AI-driven backend service that helps users discover the most suitable medical insurance plans based on:
- Age
- Income
- Household size
- State
- Dental coverage preferences

It uses real-world data from public healthcare datasets and leverages AI agents to analyze and rank plans.

---

## Features

✅ Recommends top 10 plans based on user profile  
✅ Evaluates coverage, copays, coinsurance, and eligibility  
✅ Uses AI agents (insurance, financial, decision-making) for ranking  
✅ Adds readable plan names using issuer info from dataset  
✅ API-ready: Integrate directly with frontend or mobile app  

---

## Tech Stack

| Component | Tech                        |
|----------|-----------------------------|
| Core     | Python 3.10+                |
| Logic    | `pandas`,`google-generativeai` |
| Input    | Through Webpage      |
| Output   | AI-generated plan summary & JSON response |
| Data     | Public CSVs (Benefits + Medicaid Eligibility) |


---
## Data Files/API used
- Benefits and Cost Sharing PUF from https://www.cms.gov/marketplace/resources/data/public-use-files
- Medicaid and CHIP Eligibility Level from https://data.medicaid.gov/dataset/d7e4cccb-1c56-5b5d-acce-5e7744c6d3b4#data-table
- Gemini AI API

## 📁 Folder Structure

plans4you/
├── main.py                         # Main CLI script for user interaction
├── agent_ai.py                     # AI agent logic (insurance + financial + decision)
├── benefits-and-cost-sharing-puf.csv      # Healthcare plan data
├── medicaid-and-chip-eligibility-levels.xy8t-auhk.csv  # Medicaid/CHIP income eligibility
├── requirements.txt               # Python dependencies
├── .env.example                   # Template for OpenAI or Gemini API key
└── README.md                      # This file

## Sample Response
{
  "best_plan_id": "36194FL0460001",
  "best_plan_name": "Sunshine Health Silver PPO (36194FL0460001)",
  "ranked_plans": [
    {
      "plan_id": "36194FL0460001",
      "plan_name": "Sunshine Health Silver PPO (36194FL0460001)",
      "justification": "This plan offers 0% copay for child dental and 50% adult coverage with strong accident protection."
    }
  ]
}


