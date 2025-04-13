import React from "react";

interface FormHeaderProps {
  title: string;
  description: string;
}

const FormHeader: React.FC<FormHeaderProps> = ({ title, description }) => {
  return (
    <>
      <h1 className="text-2xl font-bold text-center mb-3 text-blue-600">
        {title}
      </h1>
      <p className="text-gray-600 mb-6 text-center">
        {description}
      </p>
    </>
  );
};

export default FormHeader; 