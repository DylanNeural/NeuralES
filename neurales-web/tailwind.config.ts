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
          DEFAULT: '#6366F1',
          light: '#94A3B8',
          dark: '#0F172A',
          muted: '#EEF2FF',
          ring: '#C7D2FE',
        },
        accent: {
          DEFAULT: '#EF4444',
        },
        background: {
          DEFAULT: '#F8FAFC',
        },
      },
      borderRadius: {
        xl: '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0,0,0,0.05), 0 1px 2px -1px rgba(0,0,0,0.03)',
        elevated: '0 4px 24px -4px rgba(0,0,0,0.12), 0 2px 8px -4px rgba(0,0,0,0.08)',
      },
    },
  },
  plugins: [],
} satisfies Config;
