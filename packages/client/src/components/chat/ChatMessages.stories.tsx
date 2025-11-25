import type { Meta, StoryObj } from '@storybook/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import statusSlice from '../../store/slices/statusSlice';
import workspaceSlice from '../../store/slices/workspaceSlice';
import ChatMessages from './ChatMessages';

// Mock types for Storybook
interface Context {
  text: string;
  score: number;
  metadata: Record<string, unknown>;
}

interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
  context?: Context[];
}

// Create a mock store for Storybook
const createMockStore = (initialState = {
  status: {
    workspaceStatuses: {},
  },
  workspace: {
    workspaces: [],
    activeWorkspaceId: 1,
  },
}) => {
  return configureStore({
    reducer: {
      status: statusSlice,
      workspace: workspaceSlice,
    },
    preloadedState: initialState,
  });
};

const meta: Meta<typeof ChatMessages> = {
  title: 'Chat/ChatMessages',
  component: ChatMessages,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Chat messages display component with typing indicators and context display.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    initialState: {
      control: { type: 'object' },
      description: 'Initial Redux state',
    },
  },
  decorators: [
    (Story, context) => {
      const store = createMockStore(context.args?.initialState || {
        status: { workspaceStatuses: {} },
        workspace: { workspaces: [], activeWorkspaceId: 1 },
      });
      return (
        <Provider store={store}>
          <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
            <Story />
          </div>
        </Provider>
      );
    },
  ],
};

export default meta;
type Story = StoryObj<typeof meta>;

const sampleMessages: Message[] = [
  {
    id: '1',
    session_id: 'session-1',
    role: 'user',
    content: 'What is RAG and how does it work?',
    created_at: new Date().toISOString(),
  },
  {
    id: '2',
    session_id: 'session-1',
    role: 'assistant',
    content: 'RAG (Retrieval-Augmented Generation) is a technique that combines the power of large language models with external knowledge retrieval. Here\'s how it works:\n\n1. **Document Ingestion**: Documents are processed, chunked, and embedded\n2. **Query Processing**: User queries are embedded and used to find relevant chunks\n3. **Context Integration**: Retrieved chunks are added to the prompt\n4. **Generation**: The LLM generates responses using both its training knowledge and retrieved context\n\nThis approach provides more accurate, up-to-date, and source-grounded answers.',
    created_at: new Date().toISOString(),
    context: [
      {
        text: 'RAG combines retrieval and generation to provide more accurate answers...',
        score: 0.95,
        metadata: { source: 'rag-overview.pdf', page: 1 },
      },
      {
        text: 'The retrieval step finds relevant documents from a knowledge base...',
        score: 0.89,
        metadata: { source: 'vector-databases.pdf', page: 3 },
      },
    ],
  },
];

export const Empty: Story = {
  args: {
    messages: [],
    error: '',
    isBotTyping: false,
    onFetchWikipedia: (query: string) => console.log('Fetch Wikipedia:', query),
    initialState: {
      status: { workspaceStatuses: {} },
      workspace: { workspaces: [], activeWorkspaceId: null },
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Empty chat messages display showing the welcome message.',
      },
    },
  },
};

export const WithMessages: Story = {
  args: {
    messages: sampleMessages,
    error: '',
    isBotTyping: false,
    onFetchWikipedia: (query: string) => console.log('Fetch Wikipedia:', query),
    initialState: {
      status: { workspaceStatuses: {} },
      workspace: { workspaces: [], activeWorkspaceId: 1 },
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Chat messages with user and assistant conversation, including context display.',
      },
    },
  },
};

export const BotTyping: Story = {
  args: {
    messages: sampleMessages,
    error: '',
    isBotTyping: true,
    onFetchWikipedia: (query: string) => console.log('Fetch Wikipedia:', query),
    initialState: {
      status: { workspaceStatuses: {} },
      workspace: { workspaces: [], activeWorkspaceId: 1 },
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows the typing indicator when the bot is generating a response.',
      },
    },
  },
};

export const WithError: Story = {
  args: {
    messages: sampleMessages,
    error: 'Failed to generate response. Please try again.',
    isBotTyping: false,
    onFetchWikipedia: (query: string) => console.log('Fetch Wikipedia:', query),
    initialState: {
      status: { workspaceStatuses: {} },
      workspace: { workspaces: [], activeWorkspaceId: 1 },
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Chat messages with an error message displayed.',
      },
    },
  },
};

export const NoContextFound: Story = {
  args: {
    messages: [
      {
        id: '1',
        session_id: 'session-1',
        role: 'user',
        content: 'What is quantum computing?',
        created_at: new Date().toISOString(),
      },
      {
        id: '2',
        session_id: 'session-1',
        role: 'assistant',
        content: 'I don\'t have specific information about quantum computing in my knowledge base.',
        created_at: new Date().toISOString(),
        context: [],
      },
    ],
    error: '',
    isBotTyping: false,
    onFetchWikipedia: (query: string) => console.log('Fetch Wikipedia:', query),
    initialState: {
      status: { workspaceStatuses: { 1: 'ready' } },
      workspace: { workspaces: [], activeWorkspaceId: 1 },
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows the Wikipedia fetch option when no context is found in documents.',
      },
    },
  },
};