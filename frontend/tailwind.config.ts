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
        // Orange/coral palette inspired by RoboPick design
        primary: {
          50: '#FFF7ED',  // Very light cream/orange
          100: '#FFEDD5', // Light cream
          200: '#FED7AA', // Light orange
          300: '#FDBA74', // Medium orange
          400: '#FB923C', // Standard orange (main brand)
          500: '#F97316', // Vibrant orange (Get Started button)
          600: '#EA580C', // Darker orange
          700: '#C2410C', // Deep orange
          800: '#9A3412', // Very deep orange
          900: '#7C2D12', // Dark brown-orange
        },
        secondary: {
          50: '#F0FDF4',  // Very light green (for success states)
          100: '#DCFCE7', // Light green
          200: '#BBF7D0', // Medium light green
          300: '#86EFAC', // Medium green
          400: '#4ADE80', // Standard green
          500: '#22C55E', // Vibrant green
          600: '#16A34A', // Darker green
          700: '#15803D', // Deep green
          800: '#166534', // Very deep green
          900: '#14532D', // Dark green
        },
        surface: {
          50: '#FAFAF9',  // Almost white
          100: '#F5F5F4', // Very light gray
          200: '#E7E5E4', // Light gray
          300: '#D6D3D1', // Medium light gray
          400: '#A8A29E', // Medium gray
          500: '#78716C', // Standard gray
          600: '#57534E', // Darker gray
          700: '#44403C', // Deep gray
          800: '#292524', // Very deep gray
          900: '#1C1917', // Almost black
        }
      },
      backgroundImage: {
        'gradient-hero': 'linear-gradient(135deg, #FFF7ED 0%, #FED7AA 50%, #FB923C 100%)',
        'gradient-primary': 'linear-gradient(135deg, #FB923C 0%, #F97316 100%)',
        'gradient-mesh': 'radial-gradient(circle at 20% 50%, #FFF7ED 0%, transparent 50%), radial-gradient(circle at 80% 20%, #FED7AA 0%, transparent 50%), radial-gradient(circle at 40% 80%, #FB923C 0%, transparent 50%)',
        'gradient-card': 'linear-gradient(135deg, #FFFFFF 0%, #FFF7ED 100%)',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(251, 146, 60, 0.4)',
        'large': '0 25px 50px -12px rgba(251, 146, 60, 0.25)',
        'medium': '0 10px 15px -3px rgba(251, 146, 60, 0.1)',
        'soft': '0 4px 20px rgba(0, 0, 0, 0.08)',
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