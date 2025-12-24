import type { Config } from 'tailwindcss';

import preset from '@lynx-js/tailwind-preset-canary';

export default {
  content: ['./src/**/*.{ts,tsx}'],
  presets: [preset],
  theme: {
    extend: {
      colors: {
        // Apple-inspired design tokens
        background: 'var(--color-background)',
        foreground: 'var(--color-foreground)',
        card: 'var(--color-card)',
        'card-foreground': 'var(--color-card-foreground)',
        primary: 'var(--color-primary)',
        'primary-foreground': 'var(--color-primary-foreground)',
        secondary: 'var(--color-secondary)',
        'secondary-foreground': 'var(--color-secondary-foreground)',
        muted: 'var(--color-muted)',
        'muted-foreground': 'var(--color-muted-foreground)',
        accent: 'var(--color-accent)',
        'accent-foreground': 'var(--color-accent-foreground)',
        border: 'var(--color-border)',
        // Soft wedding colors
        blush: '#FAF0ED',
        champagne: '#F9F2E9',
        ivory: '#FDFCFB',
        gold: '#E6B88A',
        rose: '#F4D9D0',
      },
      borderRadius: {
        lg: 'var(--radius-lg)',
        md: 'var(--radius-md)',
        sm: 'var(--radius-sm)',
        xl: 'var(--radius-xl)',
        '2xl': '24px',
        '3xl': '28px',
      },
      boxShadow: {
        xs: 'var(--shadow-sm)',
        sm: 'var(--shadow-sm)',
        DEFAULT: 'var(--shadow-md)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        xl: 'var(--shadow-xl)',
      },
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
      },
    },
  },
} satisfies Config;
