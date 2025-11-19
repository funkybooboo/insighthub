/**
 * Storybook stories for ChatMessages component
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import ChatMessages, { type Message } from './ChatMessages';

const meta: Meta<typeof ChatMessages> = {
    title: 'Chat/ChatMessages',
    component: ChatMessages,
    parameters: {
        layout: 'padded',
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ChatMessages>;

const sampleMessages: Message[] = [
    { role: 'user', content: 'Hello! Can you help me understand machine learning?' },
    {
        role: 'bot',
        content:
            'Of course! Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.',
    },
    {
        role: 'user',
        content: 'What are the main types of machine learning?',
    },
    {
        role: 'bot',
        content:
            'There are three main types:\n\n1. **Supervised Learning** - Learning from labeled data\n2. **Unsupervised Learning** - Finding patterns in unlabeled data\n3. **Reinforcement Learning** - Learning through trial and error',
    },
];

export const Empty: Story = {
    name: 'Empty Messages',
    args: {
        messages: [],
        error: '',
        isBotTyping: false,
    },
};

export const SingleUserMessage: Story = {
    args: {
        messages: [{ role: 'user', content: 'Hello!' }],
        error: '',
        isBotTyping: false,
    },
};

export const SingleBotMessage: Story = {
    args: {
        messages: [{ role: 'bot', content: 'Hello! How can I help you today?' }],
        error: '',
        isBotTyping: false,
    },
};

export const Conversation: Story = {
    name: 'Multi-turn Conversation',
    args: {
        messages: sampleMessages,
        error: '',
        isBotTyping: false,
    },
};

export const WithTypingIndicator: Story = {
    name: 'Bot is Typing',
    args: {
        messages: sampleMessages,
        error: '',
        isBotTyping: true,
    },
};

export const WithError: Story = {
    name: 'With Error Message',
    args: {
        messages: sampleMessages,
        error: 'Connection error: Unable to reach the server',
        isBotTyping: false,
    },
};

export const WithMarkdown: Story = {
    name: 'Messages with Markdown',
    args: {
        messages: [
            { role: 'user', content: 'Can you show me some code examples?' },
            {
                role: 'bot',
                content:
                    '# Python Example\n\nHere\'s a simple function:\n\n```python\ndef greet(name):\n    return f"Hello, {name}!"\n```\n\nYou can call it like this: `greet("World")`',
            },
        ],
        error: '',
        isBotTyping: false,
    },
};

export const WithLinks: Story = {
    name: 'Messages with Links',
    args: {
        messages: [
            {
                role: 'user',
                content: 'Where can I learn more about AI?',
            },
            {
                role: 'bot',
                content:
                    'Here are some great resources:\n\n- [OpenAI](https://openai.com)\n- [Machine Learning Mastery](https://machinelearningmastery.com)\n- [Fast.ai](https://fast.ai)',
            },
        ],
        error: '',
        isBotTyping: false,
    },
};

export const WithCodeBlocks: Story = {
    name: 'Messages with Code Blocks',
    args: {
        messages: [
            {
                role: 'user',
                content: 'Show me a React component example',
            },
            {
                role: 'bot',
                content:
                    "Here's a simple React component:\n\n```tsx\nimport React from 'react';\n\ninterface Props {\n  name: string;\n}\n\nconst Greeting: React.FC<Props> = ({ name }) => {\n  return <h1>Hello, {name}!</h1>;\n};\n\nexport default Greeting;\n```",
            },
        ],
        error: '',
        isBotTyping: false,
    },
};

export const WithLists: Story = {
    name: 'Messages with Lists',
    args: {
        messages: [
            {
                role: 'user',
                content: 'What are the key features of React?',
            },
            {
                role: 'bot',
                content:
                    'React has several key features:\n\n- Component-based architecture\n- Virtual DOM for efficient updates\n- JSX syntax for writing components\n- Unidirectional data flow\n- Rich ecosystem of libraries\n- Strong community support',
            },
        ],
        error: '',
        isBotTyping: false,
    },
};

export const LongConversation: Story = {
    args: {
        messages: [
            ...sampleMessages,
            { role: 'user', content: 'Can you give me an example?' },
            {
                role: 'bot',
                content:
                    "Sure! Here's a simple example of supervised learning:\n\n```python\nfrom sklearn.linear_model import LinearRegression\n\n# Training data\nX = [[1], [2], [3], [4]]\ny = [2, 4, 6, 8]\n\n# Create and train model\nmodel = LinearRegression()\nmodel.fit(X, y)\n\n# Make prediction\nprint(model.predict([[5]]))  # Output: [10]\n```",
            },
            { role: 'user', content: "That's very helpful, thank you!" },
            {
                role: 'bot',
                content:
                    "You're welcome! Feel free to ask if you have any more questions about machine learning.",
            },
        ],
        error: '',
        isBotTyping: false,
    },
};

export const WithEmojis: Story = {
    name: 'Messages with Emojis',
    args: {
        messages: [
            { role: 'user', content: 'Hello! 👋' },
            { role: 'bot', content: 'Hi there! 😊 How can I help you today?' },
            { role: 'user', content: "I'm learning to code! 💻" },
            { role: 'bot', content: "That's awesome! 🎉 Keep up the great work! 🚀" },
        ],
        error: '',
        isBotTyping: false,
    },
};

export const WithSpecialCharacters: Story = {
    name: 'Messages with Special Characters',
    args: {
        messages: [
            {
                role: 'user',
                content: 'What does this mean: <html> & "quotes"?',
            },
            {
                role: 'bot',
                content:
                    'Those are special characters:\n\n- `<html>` - HTML tag syntax\n- `&` - Ampersand character\n- `"quotes"` - Double quotation marks',
            },
        ],
        error: '',
        isBotTyping: false,
    },
};

export const ErrorAndTyping: Story = {
    name: 'Error with Typing Indicator',
    args: {
        messages: sampleMessages,
        error: 'Retrying connection...',
        isBotTyping: true,
    },
};

export const VeryLongMessage: Story = {
    args: {
        messages: [
            {
                role: 'user',
                content: 'Can you explain neural networks in detail?',
            },
            {
                role: 'bot',
                content:
                    'Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) organized in layers. The basic structure includes:\n\n**Input Layer**: Receives the initial data\n\n**Hidden Layers**: Process the data through weighted connections. Each neuron applies an activation function to determine its output based on the weighted sum of its inputs.\n\n**Output Layer**: Produces the final result\n\nKey concepts:\n\n1. **Weights**: Determine the strength of connections between neurons\n2. **Biases**: Allow the activation function to be shifted\n3. **Activation Functions**: Introduce non-linearity (e.g., ReLU, Sigmoid, Tanh)\n4. **Backpropagation**: Algorithm for training the network by adjusting weights\n5. **Loss Function**: Measures the difference between predicted and actual outputs\n\nDeep learning uses neural networks with many hidden layers, enabling the model to learn complex patterns and representations from data.',
            },
        ],
        error: '',
        isBotTyping: false,
    },
};
