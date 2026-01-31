import { type Config } from 'tailwindcss';

export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        primary: {
          DEFAULT: '#2B2D42', // Couleur principale de la maquette
          light: '#8D99AE',
          dark: '#1A1B26',
        },
        accent: {
          DEFAULT: '#EF233C',
        },
        background: {
          DEFAULT: '#F8F9FB',
        },
      },
      borderRadius: {
        xl: '1rem',
      },
    },
  },
  plugins: [],
} satisfies Config;
