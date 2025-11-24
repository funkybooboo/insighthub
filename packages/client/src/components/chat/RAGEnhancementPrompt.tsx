import React from 'react';
import { Button } from '@/components/ui/button';

interface RAGEnhancementPromptProps {
    isVisible: boolean;
    onUploadDocument: () => void;
    onFetchWikipedia: (query: string) => void;
    onContinueWithoutContext: () => void;
    lastQuery?: string;
}

const RAGEnhancementPrompt: React.FC<RAGEnhancementPromptProps> = ({
    isVisible,
    onUploadDocument,
    onFetchWikipedia,
    onContinueWithoutContext,
    lastQuery,
}) => {
    if (!isVisible) return null;

    const handleFetchWikipedia = () => {
        if (lastQuery) {
            onFetchWikipedia(lastQuery);
        }
    };

    return (
        <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-4 my-4">
            <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                    <svg
                        className="h-5 w-5 text-blue-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                    >
                        <path
                            fillRule="evenodd"
                            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                            clipRule="evenodd"
                        />
                    </svg>
                </div>
                <div className="flex-1">
                    <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                        Enhance Your Query with Context
                    </h3>
                    <p className="mt-1 text-sm text-blue-700 dark:text-blue-300">
                        No relevant context was found for your query. Choose an option below to improve the response:
                    </p>
                    <div className="mt-3 flex flex-col sm:flex-row gap-2">
                        <Button
                            onClick={onUploadDocument}
                            variant="outline"
                            size="sm"
                            className="flex-1"
                        >
                            Upload Document
                        </Button>
                        <Button
                            onClick={handleFetchWikipedia}
                            variant="outline"
                            size="sm"
                            className="flex-1"
                            disabled={!lastQuery}
                        >
                            Fetch from Wikipedia
                        </Button>
                        <Button
                            onClick={onContinueWithoutContext}
                            variant="outline"
                            size="sm"
                            className="flex-1"
                        >
                            Continue Anyway
                        </Button>
                    </div>
                    {lastQuery && (
                        <p className="mt-2 text-xs text-blue-600 dark:text-blue-400">
                            Query: "{lastQuery}"
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RAGEnhancementPrompt;