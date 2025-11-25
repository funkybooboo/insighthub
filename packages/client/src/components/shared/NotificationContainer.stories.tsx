import type { Meta, StoryObj } from '@storybook/react';
import { useEffect } from 'react';
import { NotificationProvider, useNotifications } from '../../contexts/NotificationContext';
import NotificationContainer from './NotificationContainer';

// Mock component to trigger notifications for demo
const NotificationDemo: React.FC = () => {
  const { addNotification } = useNotifications();

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
  }, [addNotification]);

  return (
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
  render: () => (
    <NotificationProvider>
      <NotificationDemo />
      <NotificationContainer />
    </NotificationProvider>
  ),
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
    <NotificationProvider>
      <div className="p-8 text-center">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          No Notifications
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          The notification container is empty when there are no active notifications.
        </p>
      </div>
      <NotificationContainer />
    </NotificationProvider>
  ),
};