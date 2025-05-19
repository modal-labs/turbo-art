import defaultTheme from "tailwindcss/defaultTheme";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{html,js,svelte,ts}"],
  theme: {
    extend: {
      screens: {
        md: "840px",
        xl: "1200px",
      },
      colors: {
        // Theme colors
        primary: "#7FEE64",
        "light-green": "#DDFFDC",
        "muted-yellow": "#FFEA71",
      },
      fontFamily: {
        mono: ["Fira Mono", ...defaultTheme.fontFamily.mono],
        sans: ["Inter Variable", ...defaultTheme.fontFamily.sans],
        inter: ["Inter Variable", ...defaultTheme.fontFamily.sans],
        tosh: ["Tosh Modal", ...defaultTheme.fontFamily.sans],
        degular: ["degular", ...defaultTheme.fontFamily.sans],
      },

      // Global font modifications
      fontSize: {
        sm: [
          "0.875rem",
          {
            lineHeight: "1.25rem",
            letterSpacing: "0.01em",
          },
        ],
      },
    },
  },
  plugins: [],
};
