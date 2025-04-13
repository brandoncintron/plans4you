import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  rewrites: async () => {
    return process.env.NODE_ENV === 'development' 
      ? [
          {
            source: '/api/:path*',
            destination: 'http://127.0.0.1:5328/api/:path*',
          },
        ]
      : [] // In production, use Vercel's routing configuration from vercel.json
  },
}

export default nextConfig;
