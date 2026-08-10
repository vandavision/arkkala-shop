import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: ['nginx', 'localhost', '127.0.0.1', true],
    hmr: {
      clientPort: 3000,
    },
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://django:8000',
        changeOrigin: false,
        secure: false,
      },
      '/media': {
        target: 'http://django:8000',
        changeOrigin: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['swiper', 'chart.js', 'rc-slider'],
          'utils-vendor': ['axios', 'react-helmet-async']
        }
      }
    }
  },
});