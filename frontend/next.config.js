/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', // Optimized for Railway deployment
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || process.env.RAILWAY_PUBLIC_DOMAIN || 'http://localhost:8000',
  },
}

module.exports = nextConfig

