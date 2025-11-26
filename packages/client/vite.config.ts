import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
    plugins: [react(), tailwindcss()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        proxy: {
            '/api': 'http://localhost:3000',
        },
    },
    build: {
        rollupOptions: {
            output: {
                manualChunks: (id) => {
                    // Handle node_modules separately - split into small chunks
                    if (id.includes('node_modules')) {
                        // Markdown and syntax highlighting (lazy loaded)
                        if (id.includes('react-markdown')) {
                            return 'vendor-react-markdown';
                        }
                        if (id.includes('react-syntax-highlighter')) {
                            return 'vendor-syntax-highlighter';
                        }
                        // React core - split separately
                        if (id.includes('/react/')) {
                            return 'vendor-react';
                        }
                        if (id.includes('react-dom')) {
                            return 'vendor-react-dom';
                        }
                        if (id.includes('scheduler')) {
                            return 'vendor-scheduler';
                        }
                        // React Router - split into smaller chunks
                        if (id.includes('react-router-dom')) {
                            return 'vendor-react-router-dom';
                        }
                        if (id.includes('react-router')) {
                            return 'vendor-react-router';
                        }
                        if (id.includes('@remix-run/router')) {
                            return 'vendor-remix-router';
                        }
                        // Redux - split separately
                        if (id.includes('@reduxjs/toolkit')) {
                            return 'vendor-redux-toolkit';
                        }
                        if (id.includes('react-redux')) {
                            return 'vendor-react-redux';
                        }
                        if (id.includes('/redux') && !id.includes('react-redux')) {
                            return 'vendor-redux';
                        }
                        if (id.includes('immer')) {
                            return 'vendor-immer';
                        }
                        if (id.includes('reselect')) {
                            return 'vendor-reselect';
                        }
                        // React Query
                        if (id.includes('@tanstack/react-query')) {
                            return 'vendor-react-query';
                        }
                        if (id.includes('@tanstack/query-core')) {
                            return 'vendor-query-core';
                        }
                        // React Hook Form
                        if (id.includes('react-hook-form')) {
                            return 'vendor-hook-form';
                        }
                        // Icon libraries - split separately (both are large)
                        if (id.includes('react-icons')) {
                            return 'vendor-react-icons';
                        }
                        if (id.includes('lucide-react')) {
                            return 'vendor-lucide';
                        }
                        // Other UI libraries
                        if (id.includes('react-loading-skeleton')) {
                            return 'vendor-skeleton';
                        }
                        // Socket.IO - split components
                        if (id.includes('socket.io-client')) {
                            return 'vendor-socketio-client';
                        }
                        if (id.includes('engine.io-client')) {
                            return 'vendor-engineio';
                        }
                        if (id.includes('socket.io-parser')) {
                            return 'vendor-socketio-parser';
                        }
                        // Axios
                        if (id.includes('axios')) {
                            return 'vendor-axios';
                        }
                        // Radix UI components - each separate
                        if (id.includes('@radix-ui/react-slot')) {
                            return 'vendor-radix-slot';
                        }
                        if (id.includes('@radix-ui')) {
                            const match = id.match(/@radix-ui\/([^/]+)/);
                            if (match) {
                                return `vendor-radix-${match[1]}`;
                            }
                        }
                        // Tailwind/CSS utilities
                        if (id.includes('tailwindcss')) {
                            return 'vendor-tailwind';
                        }
                        if (id.includes('clsx')) {
                            return 'vendor-clsx';
                        }
                        if (id.includes('class-variance-authority')) {
                            return 'vendor-cva';
                        }
                        if (id.includes('tailwind-merge')) {
                            return 'vendor-tailwind-merge';
                        }
                        // Markdown-related dependencies
                        if (
                            id.includes('remark') ||
                            id.includes('micromark') ||
                            id.includes('mdast')
                        ) {
                            return 'vendor-markdown-deps';
                        }
                        // Syntax highlighter dependencies
                        if (id.includes('refractor') || id.includes('prismjs')) {
                            return 'vendor-highlighter-deps';
                        }
                        // Other scoped packages
                        if (id.includes('node_modules/@')) {
                            const match = id.match(/node_modules\/@([^/]+)\/([^/]+)/);
                            if (match) {
                                return `vendor-${match[1]}-${match[2]}`;
                            }
                        }
                        // Individual packages for remaining dependencies
                        const match = id.match(/node_modules\/([^/]+)/);
                        if (match) {
                            const packageName = match[1];
                            return `vendor-${packageName}`;
                        }
                    }
                },
            },
        },
        chunkSizeWarningLimit: 600,
    },
});
