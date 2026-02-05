/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'racing-black': '#111112',
        'racing-lime': '#D2FF00',
        'papaya': '#FF8000',
        'racing-gray': '#1a1a1a',
        'racing-dark': '#0a0a0a',
      },
      fontFamily: {
        'racing': ['Space Grotesk', 'sans-serif'],
        'display': ['Orbitron', 'monospace'],
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'spin-slow': 'spin 20s linear infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 20px #D2FF00' },
          '100%': { boxShadow: '0 0 40px #D2FF00, 0 0 60px #D2FF00' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
      },
    },
  },
  plugins: [],
}