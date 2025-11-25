import { useSelector } from 'react-redux';
import { selectIsWorkspaceProcessing } from '@/store/slices/statusSlice';
import { selectActiveWorkspaceId } from '@/store/slices/workspaceSlice';

import TypingIndicator from './TypingIndicator';
import { MessageItem } from './MessageItem';
import {
    ChatScrollContainer,
    ScrollToBottomButton,
    EmptyChatState,
    ChatError,
} from './ChatComponents';
import { useChatScroll } from '../../hooks/useChatScroll';
import { type Message as MessageType } from '../../types/chat';

type Props = {
    messages: MessageType[];
    error: string;
    isBotTyping: boolean;
    onFetchWikipedia: (query: string) => void; // New prop for fetching Wikipedia
};

const ChatMessages = ({ messages, error, isBotTyping, onFetchWikipedia }: Props) => {
    const activeWorkspaceId = useSelector(selectActiveWorkspaceId);
    const isWorkspaceProcessing = useSelector(selectIsWorkspaceProcessing(activeWorkspaceId || -1));

    const { lastMessageRef, scrollContainerRef, showScrollButton, scrollToBottom, handleScroll } =
        useChatScroll(messages, isBotTyping);

    return (
        <div className="flex-1 relative overflow-hidden">
            <ChatScrollContainer ref={scrollContainerRef} onScroll={handleScroll}>
                <div className="max-w-3xl mx-auto space-y-5">
                    {messages.length === 0 ? (
                        <EmptyChatState />
                    ) : (
                        <>
                            {messages.map((message, index) => (
                                <MessageItem
                                    key={message.id}
                                    message={message}
                                    onFetchWikipedia={onFetchWikipedia}
                                    isWorkspaceProcessing={isWorkspaceProcessing}
                                    ref={index === messages.length - 1 ? lastMessageRef : null}
                                />
                            ))}
                        </>
                    )}
                    {isBotTyping && (
                        <div className="flex justify-start">
                            <TypingIndicator />
                        </div>
                    )}
                    {error && <ChatError error={error} />}
                </div>
            </ChatScrollContainer>

            <ScrollToBottomButton onClick={scrollToBottom} visible={showScrollButton} />
        </div>
    );
};

export default ChatMessages;
