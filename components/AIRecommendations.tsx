import React from "react";

interface AIRecommendationProps {
  recommendation: string;
}

const AIRecommendations: React.FC<AIRecommendationProps> = ({ recommendation }) => {
  if (!recommendation) return null;
  
  return (
    <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
      <h2 className="text-lg font-semibold text-blue-700 mb-2">AI Recommendations</h2>
      <p className="text-gray-800">{recommendation}</p>
    </div>
  );
};

export default AIRecommendations; 