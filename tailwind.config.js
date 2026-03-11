/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'logo-blue': {
          400: '#4582af',
          500: '#2D73A5',
          600: '#16639B',
        },
        'logo-red': '#D82025',
        'cwbi-sea-blue': '#69A0B1',
        'cwbi-teal': '#99CFC6',
        'cwbi-gray': '#ABABAB',
        'cwbi-navy': {
          400: '#515d77',
          500: '#3b4866',
          600: '#253455',
        },
        'cwbi-dark-teal': {
          400: '#5b9b99',
          500: '#478f8d',
          600: '#328280',
        },
        'cwbi-orange': {
          400: '#F7B535',
          500: '#F6AC1B',
          600: '#F5A302',
        },
        'cwbi-black': '#111827',
        'cwbi-indigo': '#6843FF'
      },
    },
  },
  // eslint-disable-next-line no-undef
  plugins: [require("@tailwindcss/typography"), require("@tailwindcss/forms")],
};
