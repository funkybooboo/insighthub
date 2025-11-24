import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Provider } from 'react-redux';
import { store } from './store';
import './index.css';
import 'react-loading-skeleton/dist/skeleton.css';
import App from './App.tsx';
import ErrorBoundary from './components/shared/ErrorBoundary';

const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ErrorBoundary>
            <Provider store={store}>
                <QueryClientProvider client={queryClient}>
                    <App />
                </QueryClientProvider>
            </Provider>
        </ErrorBoundary>
    </StrictMode>
);
