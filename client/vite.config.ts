import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://chunkwise-alb-1341063601.us-east-1.elb.amazonaws.com",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
