import type { Meta, StoryObj } from '@storybook/react-vite';

// Mock MarkdownRenderer component for Storybook to avoid Redux dependencies
const MockMarkdownRenderer = ({
    content,
    isUser = false,
}: {
    content: string;
    isUser?: boolean;
}) => {
    // Simple mock implementation that renders basic markdown-like content
    const renderContent = (text: string) => {
        // Basic markdown parsing for demo
        return text.split('\n').map((line, index) => {
            if (line.startsWith('# ')) {
                return (
                    <h1 key={index} className="text-2xl font-bold mb-2">
                        {line.slice(2)}
                    </h1>
                );
            }
            if (line.startsWith('## ')) {
                return (
                    <h2 key={index} className="text-xl font-semibold mb-2">
                        {line.slice(3)}
                    </h2>
                );
            }
            if (line.startsWith('- ')) {
                return (
                    <li key={index} className="ml-4">
                        {line.slice(2)}
                    </li>
                );
            }
            if (line.startsWith('```')) {
                return (
                    <pre
                        key={index}
                        className="bg-gray-100 dark:bg-gray-800 p-3 rounded-md overflow-x-auto"
                    >
                        <code>{line.slice(3)}</code>
                    </pre>
                );
            }
            if (line.startsWith('`') && line.endsWith('`')) {
                return (
                    <code
                        key={index}
                        className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm"
                    >
                        {line.slice(1, -1)}
                    </code>
                );
            }
            if (line.trim() === '') {
                return <br key={index} />;
            }
            return (
                <p key={index} className="mb-2">
                    {line}
                </p>
            );
        });
    };

    return (
        <div
            className={`prose prose-sm max-w-none ${isUser ? 'prose-invert' : 'dark:prose-invert'}`}
        >
            {renderContent(content)}
        </div>
    );
};

const meta: Meta<typeof MockMarkdownRenderer> = {
    title: 'Chat/MarkdownRenderer',
    component: MockMarkdownRenderer,
    parameters: {
        layout: 'padded',
        docs: {
            description: {
                component:
                    'Markdown content renderer with syntax highlighting. (Mock implementation for Storybook)',
            },
        },
    },
    tags: ['autodocs'],
    argTypes: {
        content: {
            control: 'text',
        },
        isUser: {
            control: 'boolean',
        },
    },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const SimpleText: Story = {
    args: {
        content: 'This is a simple text message without any formatting.',
        isUser: false,
    },
};

export const WithMarkdown: Story = {
    args: {
        content: `# Heading 1

## Heading 2

This is a paragraph with some **bold text** and *italic text*.

- List item 1
- List item 2
- List item 3

Here's some \`inline code\` and a code block:

\`\`\`javascript
function hello() {
  console.log('Hello, World!');
}
\`\`\`

> This is a blockquote`,
        isUser: false,
    },
};

export const UserMessage: Story = {
    args: {
        content: 'Hello! How can I help you with your RAG system today?',
        isUser: true,
    },
};

export const CodeExample: Story = {
    args: {
        content: `\`\`\`python
def create_rag_pipeline(documents, embedding_model):
    # Create vector store
    vector_store = QdrantVectorStore()

    # Initialize RAG
    rag = VectorRag(
        vector_store=vector_store,
        embedding_model=embedding_model,
        chunker=SentenceChunker()
    )

    # Add documents
    rag.add_documents(documents)

    return rag
\`\`\`

This function creates a complete RAG pipeline with vector embeddings and document chunking.`,
        isUser: false,
    },
};

export const MixedContent: Story = {
    args: {
        content: `# RAG System Overview

RAG (Retrieval-Augmented Generation) combines the power of large language models with external knowledge retrieval.

## Key Components

1. **Document Processing**
   - Chunking strategies (character, sentence, word-based)
   - Embedding generation
   - Vector storage

2. **Query Processing**
   - Semantic search
   - Context retrieval
   - Response generation

## Benefits

- **Accuracy**: Access to up-to-date information
- **Reliability**: Source-grounded responses
- **Scalability**: Handle large document collections

> "The future of AI lies in combining generative models with reliable knowledge retrieval."`,
        isUser: false,
    },
};
