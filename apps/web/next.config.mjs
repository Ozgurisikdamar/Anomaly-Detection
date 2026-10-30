/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow importing the shared contracts package from outside apps/web.
  experimental: {
    externalDir: true,
  },
};

export default nextConfig;
