import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), ''); 

  return {
    plugins: [react()],
    server: {
      proxy: {
        "/api": env.ALB_URI
          ? `http://${env.ALB_URI}`
          : "http://localhost:8000",
      },
    },
  };
});
