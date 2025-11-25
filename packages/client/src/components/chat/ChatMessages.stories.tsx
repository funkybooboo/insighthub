import type { Meta, StoryObj } from '@storybook/react';

// Mock ChatMessages component for Storybook to avoid shared package import issues
const MockChatMessages = ({ messages, error, isBotTyping }: any) => {
  return (
    <div className="flex-1 relative overflow-hidden">
      <div className="h-full overflow-y-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-3xl mx-auto space-y-5">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center">
              <div className="w-14 h-14 mb-5 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <svg
                  className="w-7 h-7 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
                Start a conversation
              </h2>
              <p className="text-gray-500 dark:text-gray-400 max-w-sm text-sm leading-relaxed">
                Ask questions about your documents and get insights powered by AI
              </p>
            </div>
          ) : (
            <>
              {messages.map((message: any, index: number) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-md'
                        : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 rounded-bl-md shadow-sm border border-gray-100 dark:border-gray-700/50'
                    }`}
                  >
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      {message.content}
                    </div>
                    {message.role === 'assistant' && message.context && message.context.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Context from documents ({message.context.length} sources)
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </>
          )}
          {isBotTyping && (
            <div className="flex justify-start">
              <div className="bg-white dark:bg-gray-800 rounded-2xl px-4 py-3 shadow-sm border border-gray-100 dark:border-gray-700/50">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          {error && (
            <div className="flex justify-center">
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800/50 text-red-700 dark:text-red-300 px-4 py-3 rounded-xl max-w-md text-sm">
                {error}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const meta: Meta<typeof MockChatMessages> = {
  title: 'Chat/ChatMessages',
  component: MockChatMessages,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Chat messages display component with typing indicators and context display. (Mock implementation for Storybook)',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    messages: {
      control: 'object',
      description: 'Array of chat messages',
    },
    error: {
      control: 'text',
      description: 'Error message to display',
    },
    isBotTyping: {
      control: 'boolean',
      description: 'Whether the bot is currently typing',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

const sampleMessages = [
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
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows the assistant response when no context is found in documents.',
      },
    },
  },
};