import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Exact colors from your palette image: D8F3DC, B7E4C7, 95D5B2, 74C69D, 3DAC78
        primary: {
          50: '#D8F3DC',  // Lightest green from image
          100: '#B7E4C7', // Second lightest from image
          200: '#95D5B2', // Middle green from image
          300: '#74C69D', // Second darkest from image
          400: '#3DAC78', // Darkest green from image
          500: '#2D8F61', // Additional darker shade
          600: '#236748', // Even darker
          700: '#1A4F36', // Very dark
          800: '#123629', // Almost black
          900: '#052E16', // Black green
        },
        surface: {
          50: '#D8F3DC',  // Same as primary-50
          100: '#B7E4C7', // Same as primary-100
          200: '#95D5B2', // Same as primary-200
          300: '#74C69D', // Same as primary-300
          400: '#3DAC78', // Same as primary-400
          500: '#2D8F61', // Darker surface
          600: '#236748', // Dark surface
          700: '#1A4F36', // Very dark surface
          800: '#123629', // Almost black surface
          900: '#052E16', // Black surface
        }
      },
      backgroundImage: {
        'gradient-hero': 'linear-gradient(135deg, #D8F3DC 0%, #95D5B2 50%, #74C69D 100%)',
        'gradient-primary': 'linear-gradient(135deg, #74C69D 0%, #3DAC78 100%)',
        'gradient-mesh': 'radial-gradient(circle at 20% 50%, #D8F3DC 0%, transparent 50%), radial-gradient(circle at 80% 20%, #95D5B2 0%, transparent 50%), radial-gradient(circle at 40% 80%, #74C69D 0%, transparent 50%)',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(116, 198, 157, 0.4)',
        'large': '0 25px 50px -12px rgba(116, 198, 157, 0.25)',
        'medium': '0 10px 15px -3px rgba(116, 198, 157, 0.1)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(116, 198, 157, 0.4)' },
          '50%': { boxShadow: '0 0 40px rgba(116, 198, 157, 0.6)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;