import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"Times Now"', '"Times New Roman"', 'Times', 'serif'],
      },
    },
  },
  plugins: [],
};
export default config;
