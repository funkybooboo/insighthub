import type { Meta, StoryObj } from '@storybook/react';
import { useEffect, useState } from 'react';
import NotificationContainer, { MockNotificationContainer } from './NotificationContainer';

// Mock notification type
interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  timestamp: Date;
  duration?: number;
  persistent?: boolean;
}

// Mock component to trigger notifications for demo
const NotificationDemo: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `notification-${Date.now()}-${Math.random().toString(36).substring(7)}`,
      timestamp: new Date(),
    };

    setNotifications(prev => [newNotification, ...prev].slice(0, 5));

    // Auto-remove after duration if specified
    if (newNotification.duration && !newNotification.persistent) {
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== newNotification.id));
      }, newNotification.duration);
    }
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  useEffect(() => {
    // Add some demo notifications
    const timer1 = setTimeout(() => {
      addNotification({
        type: 'success',
        title: 'Document Processed',
        message: 'Your research paper has been successfully processed and is ready for queries.',
        duration: 5000,
      });
    }, 1000);

    const timer2 = setTimeout(() => {
      addNotification({
        type: 'info',
        title: 'Workspace Setup',
        message: 'Setting up your new workspace with RAG configuration...',
        duration: 4000,
      });
    }, 2000);

    const timer3 = setTimeout(() => {
      addNotification({
        type: 'warning',
        title: 'Wikipedia Fetch',
        message: 'Could not find relevant Wikipedia content for your query.',
        duration: 6000,
      });
    }, 3000);

    const timer4 = setTimeout(() => {
      addNotification({
        type: 'error',
        title: 'Processing Failed',
        message: 'Document processing failed due to unsupported file format.',
        persistent: true,
      });
    }, 4000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, []);

  return (
    <>
      <div className="p-8 text-center">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Notification Demo
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Watch notifications appear in the bottom left corner as events are triggered.
        </p>
        <div className="bg-gray-100 dark:bg-gray-800 p-6 rounded-lg">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Notifications will appear automatically based on socket events from the server.
          </p>
        </div>
      </div>
      <MockNotificationContainer notifications={notifications} onClose={removeNotification} />
    </>
  );
};

const meta: Meta<typeof NotificationContainer> = {
  title: 'Shared/NotificationContainer',
  component: NotificationContainer,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Notification container that displays real-time updates from server events in the bottom left corner.',
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => <NotificationDemo />,
  parameters: {
    docs: {
      description: {
        story: 'Shows various types of notifications appearing in the bottom left corner with auto-dismiss and manual close options.',
      },
    },
  },
};

export const Empty: Story = {
  render: () => (
    <div className="p-8 text-center">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
        No Notifications
      </h2>
      <p className="text-gray-600 dark:text-gray-400">
        The notification container is empty when there are no active notifications.
      </p>
    </div>
  ),
};

export const ConnectionStatus: Story = {
  render: () => {
    const [notifications, setNotifications] = useState<Notification[]>([]);

    const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
      const newNotification: Notification = {
        ...notification,
        id: `notification-${Date.now()}-${Math.random().toString(36).substring(7)}`,
        timestamp: new Date(),
      };

      setNotifications(prev => [newNotification, ...prev].slice(0, 5));

      // Auto-remove after duration if specified
      if (newNotification.duration && !newNotification.persistent) {
        setTimeout(() => {
          setNotifications(prev => prev.filter(n => n.id !== newNotification.id));
        }, newNotification.duration);
      }
    };

    const removeNotification = (id: string) => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    };

    useEffect(() => {
      // Simulate connection events
      const timer1 = setTimeout(() => {
        addNotification({
          type: 'error',
          title: 'Connection Lost',
          message: 'Lost connection to the server. Attempting to reconnect...',
          persistent: true,
        });
      }, 1000);

      const timer2 = setTimeout(() => {
        addNotification({
          type: 'success',
          title: 'Connected',
          message: 'Successfully connected to the server.',
          duration: 3000,
        });
      }, 3000);

      return () => {
        clearTimeout(timer1);
        clearTimeout(timer2);
      };
    }, []);

    return (
      <>
        <div className="p-8 text-center">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Connection Status Notifications
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Shows notifications for server connection status changes.
          </p>
          <div className="bg-gray-100 dark:bg-gray-800 p-6 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Connection status notifications appear automatically when the client connects or disconnects from the server.
            </p>
          </div>
        </div>
        <MockNotificationContainer notifications={notifications} onClose={removeNotification} />
      </>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Demonstrates connection status notifications that appear when the client connects or disconnects from the server.',
      },
    },
  },
};