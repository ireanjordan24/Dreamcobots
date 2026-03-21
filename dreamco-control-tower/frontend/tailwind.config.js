/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        dreamco: {
          50: "#f0f4ff",
          100: "#dce8ff",
          200: "#b9d1ff",
          300: "#8ab5ff",
          400: "#5490ff",
          500: "#2563eb",
          600: "#1d4ed8",
          700: "#1e40af",
          800: "#1e3a8a",
          900: "#1e3462",
        },
      },
    },
  },
  plugins: [],
};
