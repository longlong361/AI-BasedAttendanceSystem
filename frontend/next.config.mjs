/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  allowedDevOrigins: ['26.204.47.196', 'localhost', '127.0.0.1', '26.197.253.166'],
}

export default nextConfig
