import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/(components)/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      animation: {
        fadeIn: 'fadeIn 0.3s ease-in',
        aurora: 'auroraMove 30s ease-in-out infinite', // ✅ 여기에 추가
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        auroraMove: { // ✅ 추가
          '0%, 100%': {
            transform: 'translateX(0) scale(1)',
          },
          '50%': {
            transform: 'translateX(-10%) scale(1.1)',
          },
        },
      },
    },
  },
  plugins: [],
};

export default config;
