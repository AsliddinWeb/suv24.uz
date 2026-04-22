/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{vue,ts,tsx,js,jsx}"],
  safelist: [
    "badge-success",
    "badge-warning",
    "badge-danger",
    "badge-info",
    "badge-neutral",
    "badge-primary",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "'Inter Variable'",
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "'Segoe UI'",
          "Roboto",
          "sans-serif",
        ],
      },
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
          950: "#172554",
        },
      },
      boxShadow: {
        soft: "0 1px 2px 0 rgb(0 0 0 / 0.04), 0 1px 3px 0 rgb(0 0 0 / 0.06)",
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "blob-1": "blobMove 10s ease-in-out infinite",
        "blob-2": "blobMove 14s ease-in-out infinite reverse",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-12px)" },
        },
        blobMove: {
          "0%, 100%": { transform: "translate(0,0) scale(1)" },
          "50%": { transform: "translate(40px,-40px) scale(1.1)" },
        },
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
