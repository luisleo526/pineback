/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#f0f1f5',
          100: '#d4d6e0',
          200: '#a8adbe',
          300: '#7c839d',
          400: '#636980',
          500: '#434860',
          600: '#343849',
          700: '#262936',
          800: '#1a1e2e',
          900: '#0e1120',
          950: '#080a16',
        },
        accent: {
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
        },
      },
    },
  },
  plugins: [],
}
