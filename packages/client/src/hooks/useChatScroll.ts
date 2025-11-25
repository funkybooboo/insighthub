import { useRef, useState, useCallback, useEffect } from 'react';

export const useChatScroll = (messages: unknown[], isBotTyping: boolean) => {
  const lastMessageRef = useRef<HTMLDivElement | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const shouldAutoScrollRef = useRef(true);

  const isAtBottom = useCallback(() => {
    if (!scrollContainerRef.current) return true;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    return scrollHeight - scrollTop - clientHeight < 100;
  }, []);

  const scrollToBottom = useCallback(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
      shouldAutoScrollRef.current = true;
    }
  }, []);

  const handleScroll = useCallback(() => {
    if (!scrollContainerRef.current) return;
    const atBottom = isAtBottom();
    shouldAutoScrollRef.current = atBottom;
    setShowScrollButton(!atBottom && messages.length > 0);
  }, [isAtBottom, messages.length]);

  useEffect(() => {
    if (shouldAutoScrollRef.current && lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages, isBotTyping]);

  return {
    lastMessageRef,
    scrollContainerRef,
    showScrollButton,
    scrollToBottom,
    handleScroll,
  };
};