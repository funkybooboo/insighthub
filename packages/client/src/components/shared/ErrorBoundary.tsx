import React, { Component, ReactNode } from 'react';
import { Button } from '@/components/ui/button';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                    <div className="max-w-md w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
                        <div className="flex items-center mb-4">
                            <div className="flex-shrink-0">
                                <svg
                                    className="h-8 w-8 text-red-400"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                                    />
                                </svg>
                            </div>
                            <div className="ml-3">
                                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                                    Something went wrong
                                </h3>
                            </div>
                        </div>
                        <div className="mb-4">
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                An unexpected error occurred. Please try refreshing the page.
                            </p>
                            {process.env.NODE_ENV === 'development' && this.state.error && (
                                <details className="mt-2">
                                    <summary className="cursor-pointer text-sm text-red-600 dark:text-red-400">
                                        Error details (development only)
                                    </summary>
                                    <pre className="mt-2 text-xs bg-gray-100 dark:bg-gray-700 p-2 rounded overflow-auto">
                                        {this.state.error.message}
                                        {this.state.error.stack}
                                    </pre>
                                </details>
                            )}
                        </div>
                        <div className="flex space-x-3">
                            <Button onClick={() => window.location.reload()} className="flex-1">
                                Refresh Page
                            </Button>
                            <Button
                                variant="outline"
                                onClick={() => this.setState({ hasError: false, error: undefined })}
                                className="flex-1"
                            >
                                Try Again
                            </Button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
