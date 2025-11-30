import { root } from '@lynx-js/react';

// Polyfill queueMicrotask for Lynx.js compatibility
if (typeof globalThis.queueMicrotask === 'undefined') {
  globalThis.queueMicrotask = (callback: () => void) => {
    Promise.resolve()
      .then(callback)
      .catch((error) => {
        console.error('queueMicrotask error:', error);
        throw error;
      });
  };
}

import { App } from './App.jsx';

root.render(<App />);

if ((import.meta as any).webpackHot) {
  (import.meta as any).webpackHot.accept();
}
