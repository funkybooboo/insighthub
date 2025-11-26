import type { Meta, StoryObj } from '@storybook/react-vite';
import MockChatMessages from './MockChatMessages';

// Sample messages for stories
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
        content:
            "RAG (Retrieval-Augmented Generation) is a technique that combines the power of large language models with external knowledge retrieval. Here's how it works:\n\n1. **Document Ingestion**: Documents are processed, chunked, and embedded\n2. **Query Processing**: User queries are embedded and used to find relevant chunks\n3. **Context Integration**: Retrieved chunks are added to the prompt\n4. **Generation**: The LLM generates responses using both its training knowledge and retrieved context\n\nThis approach provides more accurate, up-to-date, and source-grounded answers.",
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

const meta: Meta<typeof MockChatMessages> = {
    title: 'Chat/ChatMessages',
    component: MockChatMessages,
    parameters: {
        layout: 'fullscreen',
        docs: {
            description: {
                component:
                    'Chat messages display component with typing indicators and context display. (Mock implementation for Storybook)',
            },
        },
    },
    tags: ['autodocs'],
    argTypes: {
        messages: {
            control: 'object',
            description: 'Array of chats messages',
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

export const Empty: Story = {
    args: {
        messages: [],
        error: '',
        isBotTyping: false,
    },
    parameters: {
        docs: {
            description: {
                story: 'Empty chats messages display showing the welcome message.',
            },
        },
    },
};

export const WithConversation: Story = {
    args: {
        messages: sampleMessages,
        error: '',
        isBotTyping: false,
    },
    parameters: {
        docs: {
            description: {
                story: 'Chat messages with users and assistant conversation, including context display.',
            },
        },
    },
};

export const WithTypingIndicator: Story = {
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

export const ErrorState: Story = {
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

export const NoDocumentContext: Story = {
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
                content:
                    "I don't have specific information about quantum computing in my knowledge base.",
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

export const LongConversation: Story = {
    args: {
        messages: [
            ...sampleMessages,
            {
                id: '3',
                session_id: 'session-1',
                role: 'user',
                content: 'Can you explain vector embeddings in more detail?',
                created_at: new Date().toISOString(),
            },
            {
                id: '4',
                session_id: 'session-1',
                role: 'assistant',
                content:
                    'Vector embeddings are numerical representations of text that capture semantic meaning. When you convert words, sentences, or documents into vectors, similar concepts end up with similar vector representations.\n\n**How it works:**\n1. Text is tokenized into smaller units\n2. A neural network processes these tokens\n3. Outputs a high-dimensional vector (typically 384-4096 dimensions)\n4. Similar meanings result in similar vectors\n\nThis allows for mathematical operations like finding nearest neighbors, which powers semantic search in RAG systems.',
                created_at: new Date().toISOString(),
                context: [
                    {
                        text: 'Vector embeddings transform text into numerical vectors that capture semantic relationships...',
                        score: 0.92,
                        metadata: { source: 'embeddings-guide.pdf', page: 5 },
                    },
                ],
            },
            {
                id: '5',
                session_id: 'session-1',
                role: 'user',
                content: 'What are some popular embedding models?',
                created_at: new Date().toISOString(),
            },
        ],
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
                story: 'A longer conversation showing multiple exchanges with context and typing indicator.',
            },
        },
    },
};

export const ErrorStates: Story = {
    args: {
        messages: sampleMessages,
        error: 'Connection lost. Please check your internet connection and try again.',
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
                story: 'Shows how errors are displayed in the chats interface.',
            },
        },
    },
};

export const WorkspaceProcessing: Story = {
    args: {
        messages: [
            {
                id: '1',
                session_id: 'session-1',
                role: 'user',
                content: 'Tell me about machine learning',
                created_at: new Date().toISOString(),
            },
            {
                id: '2',
                session_id: 'session-1',
                role: 'assistant',
                content: "I'm currently processing your documents. This may take a moment...",
                created_at: new Date().toISOString(),
                context: [],
            },
        ],
        error: '',
        isBotTyping: false,
        onFetchWikipedia: (query: string) => console.log('Fetch Wikipedia:', query),
        initialState: {
            status: { workspaceStatuses: { 1: 'processing' } },
            workspace: { workspaces: [], activeWorkspaceId: 1 },
        },
    },
    parameters: {
        docs: {
            description: {
                story: 'Shows behavior when workspace is processing documents.',
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
                story: 'Chat messages with users and assistant conversation, including context display.',
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
                content:
                    "I don't have specific information about quantum computing in my knowledge base.",
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
