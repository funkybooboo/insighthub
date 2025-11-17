import ReactMarkdown, { type Components } from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useSelector } from 'react-redux';
import type { RootState } from '@/store';

type Props = {
    content: string;
    isUser?: boolean;
};

const MarkdownRenderer = ({ content, isUser = false }: Props) => {
    const { theme } = useSelector((state: RootState) => state.theme);
    const isDark = theme === 'dark';

    const components: Components = {
        code({ children, className, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            const isInline = !className;

            return isInline ? (
                <code
                    className={`${
                        isUser
                            ? 'bg-blue-500/20 text-blue-100'
                            : isDark
                              ? 'bg-gray-700 text-gray-200'
                              : 'bg-gray-200 text-gray-800'
                    } px-1.5 py-0.5 rounded text-sm font-mono`}
                    {...props}
                >
                    {children}
                </code>
            ) : (
                <SyntaxHighlighter
                    style={(isDark ? oneDark : oneLight) as { [key: string]: React.CSSProperties }}
                    language={language}
                    PreTag="div"
                    className="rounded-lg my-2 text-sm"
                >
                    {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
            );
        },
        pre({ children }) {
            return <div className="my-2">{children}</div>;
        },
        a({ children, href, ...props }) {
            return (
                <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`${
                        isUser
                            ? 'text-blue-200 hover:text-blue-100'
                            : isDark
                              ? 'text-blue-400 hover:text-blue-300'
                              : 'text-blue-600 hover:text-blue-700'
                    } underline`}
                    {...props}
                >
                    {children}
                </a>
            );
        },
        p({ children }) {
            return <p className="mb-2 last:mb-0">{children}</p>;
        },
        ul({ children }) {
            return <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>;
        },
        ol({ children }) {
            return <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>;
        },
        li({ children }) {
            return <li className="ml-2">{children}</li>;
        },
        h1({ children }) {
            return <h1 className="text-xl font-bold mb-2 mt-4 first:mt-0">{children}</h1>;
        },
        h2({ children }) {
            return <h2 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h2>;
        },
        h3({ children }) {
            return <h3 className="text-base font-bold mb-2 mt-2 first:mt-0">{children}</h3>;
        },
        blockquote({ children }) {
            return (
                <blockquote
                    className={`border-l-4 pl-4 py-1 my-2 italic ${
                        isUser ? 'border-blue-300' : isDark ? 'border-gray-600' : 'border-gray-300'
                    }`}
                >
                    {children}
                </blockquote>
            );
        },
        table({ children }) {
            return (
                <div className="overflow-x-auto my-2">
                    <table className="min-w-full divide-y divide-gray-300 dark:divide-gray-700">
                        {children}
                    </table>
                </div>
            );
        },
        thead({ children }) {
            return <thead className={isDark ? 'bg-gray-800' : 'bg-gray-100'}>{children}</thead>;
        },
        tbody({ children }) {
            return (
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">{children}</tbody>
            );
        },
        tr({ children }) {
            return <tr>{children}</tr>;
        },
        th({ children }) {
            return (
                <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider">
                    {children}
                </th>
            );
        },
        td({ children }) {
            return <td className="px-3 py-2 text-sm">{children}</td>;
        },
    };

    return <ReactMarkdown components={components}>{content}</ReactMarkdown>;
};

export default MarkdownRenderer;
