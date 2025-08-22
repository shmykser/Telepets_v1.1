/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0ea5e9',
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        // Токены для совместимости с UI-компонентами
        foreground: '#f8fafc',
        'primary-foreground': '#f8fafc',
        secondary: '#1f2937',
        'secondary-foreground': '#f8fafc',
        destructive: '#ef4444',
        'destructive-foreground': '#f8fafc',
        muted: '#1e293b',
        'muted-foreground': '#94a3b8',
        accent: '#334155',
        'accent-foreground': '#f8fafc',
        card: '#1e293b',
        'card-foreground': '#f8fafc',
        input: '#334155',
        pet: {
          egg: '#fef3c7',
          baby: '#fde68a',
          teen: '#fbbf24',
          adult: '#f59e0b',
          dead: '#ef4444',
        },
        health: {
          high: '#10b981',
          medium: '#f59e0b',
          low: '#ef4444',
          critical: '#dc2626',
        },
        coin: '#fbbf24',
        background: '#0f172a',
        surface: '#1e293b',
        border: '#334155',
        ring: '#0ea5e9',
      },
      fontFamily: {
        // Используем системные шрифты с fallback
        sans: [
          'Inter', 
          'Segoe UI', 
          'Roboto', 
          'Helvetica Neue', 
          'Arial', 
          'sans-serif'
        ],
        display: [
          'Poppins', 
          'Segoe UI', 
          'Roboto', 
          'Helvetica Neue', 
          'Arial', 
          'sans-serif'
        ],
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s infinite',
        'wiggle': 'wiggle 1s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'heartbeat': 'heartbeat 1.5s ease-in-out infinite',
      },
      keyframes: {
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        heartbeat: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.1)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
} 