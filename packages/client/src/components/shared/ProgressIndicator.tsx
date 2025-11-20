import LoadingSpinner from './LoadingSpinner';

interface ProgressIndicatorProps {
    title: string;
    description?: string;
    steps?: { label: string; completed: boolean }[];
}

export default function ProgressIndicator({ title, description, steps }: ProgressIndicatorProps) {
    return (
        <div className="flex items-start gap-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <LoadingSpinner size="md" />
            <div className="flex-1">
                <h3 className="font-medium text-blue-900 dark:text-blue-100">{title}</h3>
                {description && (
                    <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">{description}</p>
                )}
                {steps && steps.length > 0 && (
                    <ul className="mt-3 space-y-2">
                        {steps.map((step, index) => (
                            <li key={index} className="flex items-center gap-2 text-sm">
                                {step.completed ? (
                                    <svg
                                        className="h-4 w-4 text-green-600 dark:text-green-400"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                ) : (
                                    <div className="h-4 w-4 rounded-full border-2 border-blue-500 dark:border-blue-400" />
                                )}
                                <span
                                    className={
                                        step.completed
                                            ? 'text-gray-600 dark:text-gray-400'
                                            : 'text-blue-700 dark:text-blue-300 font-medium'
                                    }
                                >
                                    {step.label}
                                </span>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}
