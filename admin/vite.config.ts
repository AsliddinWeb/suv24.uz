import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  server: {
    host: "0.0.0.0",
    port: 8020,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://localhost:8017",
        changeOrigin: true,
      },
      "/media": {
        target: "http://localhost:8017",
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
