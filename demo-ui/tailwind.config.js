/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'edc-blue': '#1a365d',
        'edc-green': '#22543d',
        'edc-orange': '#c05621',
      }
    },
  },
  plugins: [],
}
