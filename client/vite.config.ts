import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import dotenv from "dotenv";

dotenv.config();

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": process.env.ALB_URI
        ? `http://${process.env.ALB_URI}`
        : "http://localhost:8000",
    },
  },
});
