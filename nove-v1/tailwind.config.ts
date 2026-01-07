import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"TimesNow"', '"Cormorant"', '"Times New Roman"', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
};
export default config;
