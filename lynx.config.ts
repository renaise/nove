import { pluginQRCode } from '@lynx-js/qrcode-rsbuild-plugin';
import { pluginReactLynx } from '@lynx-js/react-rsbuild-plugin';
import { defineConfig } from '@lynx-js/rspeedy';
import { pluginSass } from '@rsbuild/plugin-sass';
import { pluginTypeCheck } from '@rsbuild/plugin-type-check';

export default defineConfig({
  source: {
    entry: {
      index: './src/index.tsx',
    },
  },
  server: {
    port: 8081,
    host: '0.0.0.0', // Allow connections from any IP
  },
  dev: {
    writeToDisk: false,
    hmr: true,
    liveReload: true,
  },
  plugins: [
    pluginQRCode({
      schema(url) {
        // Replace 0.0.0.0 with actual machine IP for phone access
        const phoneUrl = url.replace('0.0.0.0', '192.168.1.100');
        // We use `?fullscreen=true` to open the page in LynxExplorer in full screen mode
        return `${phoneUrl}?fullscreen=true`;
      },
    }),
    pluginReactLynx(),
    pluginSass({}),
    pluginTypeCheck(),
  ],
  output: {
    // In production, resolve assets via Lynx native resource loader.
    // In dev, force absolute asset URLs to localhost to avoid 0.0.0.0.
    assetPrefix:
      process.env.NODE_ENV === 'production'
        ? 'lynx://'
        : 'http://localhost:8081/',
  },
});
