/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: "#6366f1",
        surface: "#0f1117",
        card: "#161b27",
        border: "#1e2d40",
        muted: "#64748b",
      },
    },
  },
  plugins: [],
};
