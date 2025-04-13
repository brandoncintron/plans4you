import React, { useState } from "react";
import { HealthcareFormValues } from "@/schema/healthcare-form";
import PageLayout from "@/components/PageLayout";
import FormHeader from "@/components/FormHeader";
import HealthcareForm from "@/components/HealthcareForm";
import AIRecommendations from "@/components/AIRecommendations";

function HealthcareAIAssistant() {
  const [aiResponse, setAiResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  function onSubmit(data: HealthcareFormValues) {
    // Show loading state
    setIsLoading(true);

    // Remove logging of PHI data for prod
     console.log(data);

    // Simulate AI processing with a timeout
    setTimeout(() => {
      // Example AI response
      setAiResponse(
        `Based on your information, I recommend considering a PPO plan with a moderate deductible. 
        This type of plan would provide flexibility in choosing healthcare providers while maintaining reasonable costs. 
        ${
          data.dentalPlanRequired === "yes"
            ? "I've also included dental coverage options in the recommendation."
            : ""
        }
        For more specific recommendations, please consult with a healthcare advisor.`
      );
      setIsLoading(false);
    }, 1500);
  }

  return (
    <PageLayout isLoading={isLoading}>
      <FormHeader 
        title="Healthcare AI Assistant"
        description="Fill out the form below with your information. Our AI will provide personalized healthcare plan recommendations."
      />
      <HealthcareForm onFormSubmit={onSubmit} isLoading={isLoading} />
      <AIRecommendations recommendation={aiResponse} />
    </PageLayout>
  );
}

export default HealthcareAIAssistant;
