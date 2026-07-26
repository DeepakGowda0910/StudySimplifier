/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2f9',
          100: '#d9e2f0',
          200: '#b3c5e0',
          300: '#7f9cc7',
          400: '#4d70a3',
          500: '#2e4d7a',
          600: '#1f3a63',
          700: '#16294a',
          800: '#0f1c33',
          900: '#0a1220',
        },
        navy: {
          50: '#eef2f9',
          100: '#d9e2f0',
          200: '#b3c5e0',
          300: '#7f9cc7',
          400: '#4d70a3',
          500: '#2e4d7a',
          600: '#1f3a63',
          700: '#16294a',
          800: '#0f1c33',
          900: '#0a1220',
        },
        surface: {
          DEFAULT: '#ffffff',
          dark: '#0a1220',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(20px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
