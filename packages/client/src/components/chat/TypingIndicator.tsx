type DotProps = {
    className?: string;
};

const Dot = ({ className }: DotProps) => (
    <div
        className={`w-1.5 h-1.5 rounded-full bg-gray-400 dark:bg-gray-500 animate-pulse ${className}`}
    />
);

const TypingIndicator = () => {
    return (
        <div className="flex self-start gap-1.5 px-4 py-3 bg-white dark:bg-gray-800 rounded-2xl rounded-bl-md shadow-sm border border-gray-100 dark:border-gray-700/50">
            <Dot />
            <Dot className="[animation-delay:0.2s]" />
            <Dot className="[animation-delay:0.4s]" />
        </div>
    );
};

export default TypingIndicator;
