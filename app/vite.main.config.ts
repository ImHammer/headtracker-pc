import { defineConfig } from 'vite';

// https://vitejs.dev/config
export default defineConfig({
  optimizeDeps: {
    exclude: ["ws"],
  },
  build: {
    rollupOptions: {
      external: ["ws"],
    },
  },
});
