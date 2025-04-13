import React, { ReactNode } from "react";
import Loading from "@/components/Loading";

interface PageLayoutProps {
  children: ReactNode;
  isLoading: boolean;
}

const PageLayout: React.FC<PageLayoutProps> = ({ children, isLoading }) => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <Loading isLoading={isLoading} />
      <div className="max-w-3xl mx-auto bg-white p-8 rounded-lg shadow-md">
        {children}
      </div>
    </div>
  );
};

export default PageLayout; 