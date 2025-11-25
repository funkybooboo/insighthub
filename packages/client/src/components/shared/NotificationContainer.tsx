import React from 'react';
import { X, CheckCircle, XCircle, Info, AlertTriangle } from 'lucide-react';

// Mock notification type for Storybook
interface Notification {
    id: string;
    type: 'success' | 'error' | 'info' | 'warning';
    title: string;
    message: string;
    timestamp: Date;
    duration?: number;
    persistent?: boolean;
}

const NotificationItem: React.FC<{ notification: Notification; onClose: (id: string) => void }> = ({
    notification,
    onClose,
}) => {
    const getIcon = () => {
        switch (notification.type) {
            case 'success':
                return <CheckCircle className="w-5 h-5 text-green-500" />;
            case 'error':
                return <XCircle className="w-5 h-5 text-red-500" />;
            case 'warning':
                return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
            case 'info':
            default:
                return <Info className="w-5 h-5 text-blue-500" />;
        }
    };

    const getBackgroundColor = () => {
        switch (notification.type) {
            case 'success':
                return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
            case 'error':
                return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
            case 'warning':
                return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
            case 'info':
            default:
                return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
        }
    };

    return (
        <div
            className={`max-w-sm w-full p-4 rounded-lg border shadow-lg transition-all duration-300 ease-in-out relative ${getBackgroundColor()}`}
            role="alert"
        >
            {/* Close button in top right corner */}
            <button
                onClick={() => onClose(notification.id)}
                className="absolute top-2 right-2 p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors z-10"
                aria-label="Close notification"
            >
                <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </button>

            <div className="flex items-start gap-3 pr-8">
                <div className="flex-shrink-0 mt-0.5">{getIcon()}</div>
                <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
                        {notification.title}
                    </h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                        {notification.message}
                    </p>
                </div>
            </div>
        </div>
    );
};

// Mock container for Storybook - in real app this uses context
const MockNotificationContainer: React.FC<{
    notifications: Notification[];
    onClose: (id: string) => void;
}> = ({ notifications, onClose }) => {
    if (notifications.length === 0) {
        return null;
    }

    return (
        <div className="fixed bottom-4 left-4 z-[9999] space-y-2 pointer-events-none">
            {notifications.map((notification) => (
                <div key={notification.id} className="pointer-events-auto">
                    <NotificationItem notification={notification} onClose={onClose} />
                </div>
            ))}
        </div>
    );
};

// Real container for production use
const NotificationContainer: React.FC = () => {
    // This would use the real context in production
    return null;
};

export default NotificationContainer;
export { MockNotificationContainer };
