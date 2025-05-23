import React, { useState } from "react";
import { HealthcareFormValues } from "@/schema/healthcare-form";
import PageLayout from "@/components/PageLayout";
import FormHeader from "@/components/FormHeader";
import HealthcareForm from "@/components/HealthcareForm";
import AIRecommendations from "@/components/AIRecommendations";
import { HealthInsuranceRecommendation } from "@/data/healthInsuranceRecommendations";
import axios from "axios";

function HealthcareAIAssistant() {
  const [aiResponse, setAiResponse] = useState<
    string | HealthInsuranceRecommendation
  >("");
  const [isLoading, setIsLoading] = useState(false);

  async function onSubmit(data: HealthcareFormValues) {
    // Show loading state
    setIsLoading(true);

    try {
      const response = await axios.post(
        "http://localhost:5328/api/benefits_and_cost_sharing",
        data,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const recommendationData = response.data;
      setAiResponse(recommendationData);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      setAiResponse("Sorry, we encountered an error processing your request.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <PageLayout isLoading={isLoading}>
      <FormHeader
        title="Plans4You - A Healthcare AI Assistant"
        description="Please fill out the form below with your information. Our AI will provide personalized healthcare plan recommendations."
      />
      <HealthcareForm onFormSubmit={onSubmit} isLoading={isLoading} />
      <AIRecommendations recommendation={aiResponse} />
    </PageLayout>
  );
}

export default HealthcareAIAssistant;
