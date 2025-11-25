import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { Notification, NotificationContextType } from '../types/notification';

interface NotificationState {
    notifications: Notification[];
}

type NotificationAction =
    | { type: 'ADD_NOTIFICATION'; payload: Notification }
    | { type: 'REMOVE_NOTIFICATION'; payload: string }
    | { type: 'CLEAR_ALL' };

const notificationReducer = (
    state: NotificationState,
    action: NotificationAction
): NotificationState => {
    switch (action.type) {
        case 'ADD_NOTIFICATION':
            return {
                ...state,
                notifications: [action.payload, ...state.notifications].slice(0, 5), // Keep max 5 notifications
            };
        case 'REMOVE_NOTIFICATION':
            return {
                ...state,
                notifications: state.notifications.filter((n) => n.id !== action.payload),
            };
        case 'CLEAR_ALL':
            return {
                ...state,
                notifications: [],
            };
        default:
            return state;
    }
};

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// eslint-disable-next-line react-refresh/only-export-components
export const useNotifications = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotifications must be used within a NotificationProvider');
    }
    return context;
};

interface NotificationProviderProps {
    children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
    const [state, dispatch] = useReducer(notificationReducer, { notifications: [] });

    const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp'>) => {
        const newNotification: Notification = {
            ...notification,
            id: `notification-${Date.now()}-${Math.random().toString(36).substring(7)}`,
            timestamp: new Date(),
        };

        dispatch({ type: 'ADD_NOTIFICATION', payload: newNotification });

        // Auto-remove after duration if specified
        if (newNotification.duration && !newNotification.persistent) {
            setTimeout(() => {
                dispatch({ type: 'REMOVE_NOTIFICATION', payload: newNotification.id });
            }, newNotification.duration);
        }
    }, []);

    const removeNotification = useCallback((id: string) => {
        dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
    }, []);

    const clearAll = useCallback(() => {
        dispatch({ type: 'CLEAR_ALL' });
    }, []);

    const value: NotificationContextType = {
        notifications: state.notifications,
        addNotification,
        removeNotification,
        clearAll,
    };

    return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
};
