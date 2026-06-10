/** @type {import('tailwindcss').Config} */
/** Build config for ckanext-cwbi-theme.
    Derived from the CWBI Hub Tailwind configuration; CJS syntax for Tailwind CLI.
    Content paths updated to scan CKAN templates. */
module.exports = {
  content: ['./ckanext/cwbi_theme/templates/**/*.html'],
  safelist: [
    'account',
    'account-masthead',
    'header-search',
    'main-navbar',
    'masthead',
    'nav',
    'navbar',
    'navbar-nav',
    'navigation',
    'nav-pills',
    'search-input-group',
    'section',
    'site-footer',
    'site-title',
    'cwbi-content-section',
    'cwbi-content-inner',
  ],
  corePlugins: {
    preflight: false,  // Bootstrap handles base resets; Tailwind preflight conflicts
  },
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
        'cwbi-indigo': '#6843FF',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    // @tailwindcss/forms omitted because resets conflict with Bootstrap form styling
  ],
};
