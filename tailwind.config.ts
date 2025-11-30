import type { Config } from 'tailwindcss';

import preset from '@lynx-js/tailwind-preset-canary';

export default {
  content: ['./src/**/*.{ts,tsx}'],
  presets: [preset],
  theme: {
    extend: {
      colors: {
        // Wedding-themed colors
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
        // Wedding-specific colors
        blush: '#F8E8E8',
        champagne: '#F7E7CE',
        ivory: '#FFFFF0',
        gold: '#D4AF37',
        rose: '#E8B4B8',
      },
      borderRadius: {
        lg: 'var(--radius-lg)',
        md: 'var(--radius-md)',
        sm: 'var(--radius-sm)',
        xl: 'var(--radius-xl)',
      },
      boxShadow: {
        xs: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
      },
    },
  },
} satisfies Config;
