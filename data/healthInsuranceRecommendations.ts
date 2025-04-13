// Example data for the AI recommendation
import { HealthcareFormValues } from "@/schema/healthcare-form";
import axios from 'axios';

export interface PlanRecommendation {
  planId: string;
  rank: number;
  isBestPlan?: boolean;
  justification: string;
}

export interface HealthInsuranceRecommendation {
  plans: PlanRecommendation[];
}

// Function to fetch recommendations from the API
export const fetchRecommendationsFromAPI = async (formValues: HealthcareFormValues): Promise<HealthInsuranceRecommendation> => {
  try {
    const response = await axios.post('/api/benefits_and_cost_sharing', formValues);
    return {
      plans: response.data.plans
    };
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    return { plans: [] };
  }
};

// Function to generate recommendations based on form values
export const generateRecommendation = async (formValues: HealthcareFormValues): Promise<HealthInsuranceRecommendation> => {
  // Use the API endpoint to get recommendations
  return fetchRecommendationsFromAPI(formValues);
};