import { defineConfig } from '@rsbuild/core';
import { pluginReactLynx } from '@lynx-js/react-rsbuild-plugin';

import { pluginTailwindCSS } from 'rsbuild-plugin-tailwindcss';

export default defineConfig({
  plugins: [
    pluginReactLynx(),
    pluginTailwindCSS({ config: './tailwind.config.ts' }),
  ],
  html: {
    template: './src/index.html',
  },
  source: {
    entry: {
      index: './src/index.tsx',
    },
  },
});
