/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: "#10242E",
        surface: "#F7F9F9",
        card: "#FFFFFF",
        border: "#E2E8E6",
        teal: {
          DEFAULT: "#0F766E",
          dark: "#0B5750",
          light: "#CCFBF1",
        },
        coral: {
          DEFAULT: "#C2410C",
          light: "#FFEDD5",
        },
        sage: {
          DEFAULT: "#4D7C63",
          light: "#DCFCE7",
        },
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
