import LoadingSpinner from './LoadingSpinner';

export type Status =
    | 'pending'
    | 'processing'
    | 'provisioning'
    | 'parsing'
    | 'chunking'
    | 'embedding'
    | 'indexing'
    | 'ready'
    | 'failed'
    | 'error'
    | 'deleting';

interface StatusBadgeProps {
    status: Status;
    message?: string;
    size?: 'sm' | 'md';
}

const statusConfig: Record<
    Status,
    {
        label: string;
        bgColor: string;
        textColor: string;
        showSpinner: boolean;
    }
> = {
    pending: {
        label: 'Pending',
        bgColor: 'bg-gray-100 dark:bg-gray-700',
        textColor: 'text-gray-700 dark:text-gray-300',
        showSpinner: false,
    },
    processing: {
        label: 'Processing',
        bgColor: 'bg-blue-100 dark:bg-blue-900/30',
        textColor: 'text-blue-700 dark:text-blue-300',
        showSpinner: true,
    },
    parsing: {
        label: 'Parsing',
        bgColor: 'bg-blue-100 dark:bg-blue-900/30',
        textColor: 'text-blue-700 dark:text-blue-300',
        showSpinner: true,
    },
    chunking: {
        label: 'Chunking',
        bgColor: 'bg-blue-100 dark:bg-blue-900/30',
        textColor: 'text-blue-700 dark:text-blue-300',
        showSpinner: true,
    },
    embedding: {
        label: 'Embedding',
        bgColor: 'bg-blue-100 dark:bg-blue-900/30',
        textColor: 'text-blue-700 dark:text-blue-300',
        showSpinner: true,
    },
    indexing: {
        label: 'Indexing',
        bgColor: 'bg-blue-100 dark:bg-blue-900/30',
        textColor: 'text-blue-700 dark:text-blue-300',
        showSpinner: true,
    },
    provisioning: {
        label: 'Provisioning',
        bgColor: 'bg-blue-100 dark:bg-blue-900/30',
        textColor: 'text-blue-700 dark:text-blue-300',
        showSpinner: true,
    },
    ready: {
        label: 'Ready',
        bgColor: 'bg-green-100 dark:bg-green-900/30',
        textColor: 'text-green-700 dark:text-green-300',
        showSpinner: false,
    },
    failed: {
        label: 'Failed',
        bgColor: 'bg-red-100 dark:bg-red-900/30',
        textColor: 'text-red-700 dark:text-red-300',
        showSpinner: false,
    },
    error: {
        label: 'Error',
        bgColor: 'bg-red-100 dark:bg-red-900/30',
        textColor: 'text-red-700 dark:text-red-300',
        showSpinner: false,
    },
    deleting: {
        label: 'Deleting',
        bgColor: 'bg-red-100 dark:bg-red-900/30',
        textColor: 'text-red-700 dark:text-red-300',
        showSpinner: true,
    },
};

export default function StatusBadge({ status, message, size = 'sm' }: StatusBadgeProps) {
    const config = statusConfig[status];
    const paddingClass = size === 'sm' ? 'px-2 py-1 text-xs' : 'px-3 py-1.5 text-sm';

    return (
        <div className="inline-flex flex-col gap-1">
            <span
                className={`inline-flex items-center gap-1.5 rounded-full font-medium ${config.bgColor} ${config.textColor} ${paddingClass}`}
            >
                {config.showSpinner && <LoadingSpinner size="sm" className="h-3 w-3" />}
                {config.label}
            </span>
            {message && (
                <span className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{message}</span>
            )}
        </div>
    );
}
