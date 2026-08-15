import path from "node:path";
import { fileURLToPath } from "node:url";

/** @type {import('next').NextConfig} */
// Proxy /api/* to the FastAPI backend so the browser never hits CORS and the
// Python API stays untouched. Override the backend URL with API_URL.
const API = process.env.API_URL || "http://localhost:8000";

const projectRoot = path.dirname(fileURLToPath(import.meta.url));

const nextConfig = {
  // Pin the project root. Next.js otherwise infers it by walking up looking for
  // a lockfile, and there is a stray package-lock.json in the Windows home
  // directory — so it picked C:\Users\Dione as the root. Tailwind v4 discovers
  // utility classes by scanning from that root, found none, and emitted an
  // essentially empty stylesheet: the console rendered as unstyled HTML.
  outputFileTracingRoot: projectRoot,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API}/:path*` }];
  },
};

export default nextConfig;
