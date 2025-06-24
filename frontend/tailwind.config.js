/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      keyframes: {
        dropIn: {
          '0%': { opacity: 0, transform: 'translateY(-10px) scale(0.95)' },
          '100%': { opacity: 1, transform: 'translateY(0) scale(1)' },
        },
      },
      animation: {
        dropIn: 'dropIn 0.4s ease-out forwards',
      },
    },
  },

  plugins: [],
}

