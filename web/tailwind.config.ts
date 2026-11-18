import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: ['class', '[data-theme="night"]'],
  theme: {
    extend: {
      colors: {
        // Surfaces & grounds from tokens.css
        bg: '#EEF1EA',
        card: 'rgba(255, 255, 255, 0.9)',
        'card-solid': '#FFFFFF',
        'hero-ground': '#54705C',
        'panel-dark': '#263A30',

        // Text & neutrals
        ink: {
          DEFAULT: '#1B2A22',
          2: '#3F4F45',
          soft: '#5A6A60',
          muted: '#5A6A60',
        },
        primary: {
          DEFAULT: '#3E6B53',
          strong: '#2C5140',
        },
        tint: {
          DEFAULT: '#DDE9E0',
          nav: '#E1ECE4',
        },
        line: '#C5D0C7',
        divider: '#DCE3DA',
        soft: '#E6EBE4',

        // Habit categories
        recovery: {
          DEFAULT: '#6E4A8E',
          tint: '#EDE6F3',
        },
        movement: {
          DEFAULT: '#3E6B53',
          tint: '#DDE9E0',
        },
        sleep: {
          DEFAULT: '#3F4FA8',
          tint: '#E2E5F5',
        },
        meals: {
          DEFAULT: '#8A4B0F',
          tint: '#F6E9DC',
        },
        ramadan: {
          DEFAULT: '#2E2563',
          tint: '#EAE6F7',
        },
        danger: {
          DEFAULT: '#A02A1C',
          tint: '#FDE8E4',
        },

        // Decorative motifs
        calligraphy: '#4F7A62',
        stitch: '#2F5A44',

        // Compatibility aliases mapped directly to new tokens
        sand: {
          50: '#EEF1EA',
          100: '#FFFFFF',
          200: '#E6EBE4',
          300: '#C5D0C7',
          400: '#C5D0C7',
        },
        teal: {
          300: '#DDE9E0',
          600: '#3E6B53',
          700: '#2C5140',
        },
        apricot: {
          DEFAULT: '#8A4B0F',
          tint: '#F6E9DC',
        },
        coral: '#A02A1C',
        sage: '#3E6B53',
        dusk: '#3F4FA8',
        night: '#141F19',
      },
      fontFamily: {
        display: ['"Bricolage Grotesque"', '"Plus Jakarta Sans"', 'sans-serif'],
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        body: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        arabic: ['"Aref Ruqaa"', 'serif'],
      },
      fontSize: {
        'display-xl': ['44px', { lineHeight: '50px', letterSpacing: '-0.02em', fontWeight: '600' }],
        'h1': ['28px', { lineHeight: '34px', letterSpacing: '-0.02em', fontWeight: '600' }],
        'h2': ['22px', { lineHeight: '28px', letterSpacing: '-0.02em', fontWeight: '600' }],
        'title': ['17px', { lineHeight: '24px', fontWeight: '600' }],
        'body': ['15px', { lineHeight: '22px', fontWeight: '400' }],
        'small': ['14px', { lineHeight: '20px', fontWeight: '400' }],
        'caption': ['12px', { lineHeight: '16px', fontWeight: '400' }],
      },
      borderRadius: {
        card: '20px',
        button: '14px',
        cta: '16px',
        pill: '999px',
        '2xl': '20px',
        '3xl': '22px',
      },
      boxShadow: {
        card: '0 1px 2px rgba(38, 58, 48, .06), 0 10px 28px -14px rgba(38, 58, 48, .22)',
        button: '0 8px 18px -10px rgba(38, 70, 52, .65)',
        'card-hover': '0 2px 4px rgba(38, 58, 48, .08), 0 14px 32px -12px rgba(38, 58, 48, .28)',
        'teal-glow': '0 0 24px rgba(62, 107, 83, .25)',
      },
      maxWidth: {
        app: '640px',
      },
    },
  },
  plugins: [],
} satisfies Config
