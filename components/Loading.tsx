import React from 'react';
import { LogosGoogleGemini } from './icons/GeminiIcon';

interface LoadingProps {
  isLoading: boolean;
}

const Loading: React.FC<LoadingProps> = ({ isLoading }) => {
  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 backdrop-blur-sm bg-white/30 flex items-center justify-center z-50">
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
      `}</style>
      <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
        <div className="flex items-center justify-center mb-4">
          Plans4You
        </div>
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-3"></div>
        <p className="text-gray-700 font-medium mb-2" style={{ fontFamily: '"Google Sans", sans-serif' }}>Generating recommendations...</p>
        <p className="text-xs text-gray-500 flex items-center" style={{ fontFamily: '"Google Sans", sans-serif' }}><LogosGoogleGemini className="h-4 w-4 mr-2" /> Powered by Google Gemini AI</p>
      </div>
    </div>
  );
};

export default Loading;
