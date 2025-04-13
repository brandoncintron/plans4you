import React from "react";
import { HealthInsuranceRecommendation, PlanRecommendation } from "@/data/healthInsuranceRecommendations";

// Define interface for API response structure
interface ApiResponse {
  status?: string;
  message?: string;
  analysis?: {
    best_plan_id?: string;
    ranked_plans?: PlanRecommendation[];
  };
  ranked_plans?: PlanRecommendation[];
}

// Add plans property to HealthInsuranceRecommendation if it doesn't have it
interface ExtendedHealthInsuranceRecommendation extends HealthInsuranceRecommendation {
  plans: PlanRecommendation[];
}

interface AIRecommendationProps {
  recommendation: string | ExtendedHealthInsuranceRecommendation | ApiResponse;
}

const AIRecommendations: React.FC<AIRecommendationProps> = ({ recommendation }) => {
  if (!recommendation) return null;
  
  // Check if recommendation is a string (legacy format) or structured data
  if (typeof recommendation === "string") {
    return (
      <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
        <h2 className="text-lg font-semibold text-blue-700 mb-2">AI Recommendations</h2>
        <p className="text-gray-800">{recommendation}</p>
      </div>
    );
  }
  
  // Extract plans from the recommendation based on its structure
  let plansList: PlanRecommendation[] = [];
  
  // Check if it has direct plans property (HealthInsuranceRecommendation)
  if ('plans' in recommendation && Array.isArray(recommendation.plans)) {
    plansList = recommendation.plans;
  } 
  // Check if it has analysis with ranked_plans (ApiResponse)
  else if ('analysis' in recommendation && 
           recommendation.analysis && 
           'ranked_plans' in recommendation.analysis && 
           Array.isArray(recommendation.analysis.ranked_plans)) {
    plansList = recommendation.analysis.ranked_plans;
  }
  // Check if it has direct ranked_plans (ApiResponse)
  else if ('ranked_plans' in recommendation && 
           Array.isArray(recommendation.ranked_plans)) {
    plansList = recommendation.ranked_plans;
  }
  
  return (
    <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-100">
      <h2 className="text-xl font-semibold text-blue-700 mb-4">Insurance Plan Recommendations</h2>
      
      {/* Plan Recommendations */}
      <div>
        <h3 className="text-lg font-medium text-blue-700 mb-3">Recommended Plans</h3>
        {plansList.length > 0 ? (
          plansList.map((plan: PlanRecommendation) => (
            <div key={plan.planId} className="mb-4 p-4 bg-white rounded-md border-l-4 border-blue-500">
              <div className="flex justify-between items-center">
                <h4 className="text-md font-semibold">
                  {plan.isBestPlan && (
                    <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded mr-2">
                      BEST MATCH
                    </span>
                  )}
                  Plan ID: {plan.planId}
                </h4>
                <span className="text-sm bg-gray-100 px-2 py-1 rounded">Rank: {plan.rank}</span>
              </div>
              <p className="mt-2 text-gray-700 text-sm">{plan.justification}</p>
            </div>
          ))
        ) : (
          <p className="text-gray-600">No plan recommendations available.</p>
        )}
      </div>
    </div>
  );
};

export default AIRecommendations; 