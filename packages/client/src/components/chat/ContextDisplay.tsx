import React, { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/20/solid';
import { type Context } from '../../types/chat';

interface ContextDisplayProps {
    context: Context[];
}

const ContextDisplay: React.FC<ContextDisplayProps> = ({ context }) => {
    const [expanded, setExpanded] = useState(false);

    if (!context || context.length === 0) {
        return null;
    }

    return (
        <div className="mt-2 text-sm text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-2">
            <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center justify-between w-full text-left focus:outline-none"
            >
                <span className="font-medium">
                    {context.length} relevant context snippets
                </span>
                {expanded ? (
                    <ChevronUpIcon className="h-5 w-5" />
                ) : (
                    <ChevronDownIcon className="h-5 w-5" />
                )}
            </button>

            {expanded && (
                <div className="mt-2 space-y-3">
                    {context.map((item, index) => (
                        <div
                            key={index}
                            className="bg-gray-50 dark:bg-gray-700 p-3 rounded-md shadow-sm"
                        >
                            <p className="font-semibold text-gray-800 dark:text-gray-200">
                                Source: {item.metadata.filename || 'Unknown'} (Score: {item.score.toFixed(2)})
                            </p>
                            <p className="mt-1 text-gray-700 dark:text-gray-300 line-clamp-3">
                                {item.text}
                            </p>
                            {/* Optionally add a button to view full context */}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ContextDisplay;
