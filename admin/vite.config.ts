import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const devApiTarget = process.env.VITE_DEV_API_TARGET || "http://localhost:8017";

export default defineConfig({
  server: {
    host: "0.0.0.0",
    port: 8020,
    strictPort: true,
    watch: {
      usePolling: !!process.env.VITE_USE_POLLING,
    },
    proxy: {
      "/api": {
        target: devApiTarget,
        changeOrigin: true,
      },
      "/media": {
        target: devApiTarget,
        changeOrigin: true,
      },
    },
  },
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
});
