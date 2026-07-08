import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* This allows your local network/phone to see the dev server */
  allowedDevOrigins: ['172.20.10.5', 'localhost:3000']
  };

export default nextConfig;
