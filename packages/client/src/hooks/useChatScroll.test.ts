import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChatScroll } from './useChatScroll';
import '../test/setup';

describe('useChatScroll', () => {
    let mockScrollIntoView: ReturnType<typeof vi.fn>;

    beforeEach(() => {
        mockScrollIntoView = vi.fn();
        Element.prototype.scrollIntoView = mockScrollIntoView;
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    describe('Initial State', () => {
        it('should initialize with correct default values', () => {
            const { result } = renderHook(() => useChatScroll([], false));

            expect(result.current.lastMessageRef.current).toBeNull();
            expect(result.current.scrollContainerRef.current).toBeNull();
            expect(result.current.showScrollButton).toBe(false);
            expect(typeof result.current.scrollToBottom).toBe('function');
            expect(typeof result.current.handleScroll).toBe('function');
        });

        it('should not show scroll button initially', () => {
            const { result } = renderHook(() => useChatScroll([], false));
            expect(result.current.showScrollButton).toBe(false);
        });
    });

    describe('Refs', () => {
        it('should provide lastMessageRef', () => {
            const { result } = renderHook(() => useChatScroll([], false));
            expect(result.current.lastMessageRef).toBeDefined();
            expect(result.current.lastMessageRef.current).toBeNull();
        });

        it('should provide scrollContainerRef', () => {
            const { result } = renderHook(() => useChatScroll([], false));
            expect(result.current.scrollContainerRef).toBeDefined();
            expect(result.current.scrollContainerRef.current).toBeNull();
        });

        it('should allow setting lastMessageRef', () => {
            const { result } = renderHook(() => useChatScroll([], false));
            const mockElement = document.createElement('div');

            act(() => {
                result.current.lastMessageRef.current = mockElement;
            });

            expect(result.current.lastMessageRef.current).toBe(mockElement);
        });

        it('should allow setting scrollContainerRef', () => {
            const { result } = renderHook(() => useChatScroll([], false));
            const mockElement = document.createElement('div');

            act(() => {
                result.current.scrollContainerRef.current = mockElement;
            });

            expect(result.current.scrollContainerRef.current).toBe(mockElement);
        });
    });

    describe('scrollToBottom', () => {
        it('should call scrollIntoView on lastMessageRef when it exists', () => {
            const { result } = renderHook(() => useChatScroll([], false));
            const mockElement = document.createElement('div');

            act(() => {
                result.current.lastMessageRef.current = mockElement;
            });

            act(() => {
                result.current.scrollToBottom();
            });

            expect(mockScrollIntoView).toHaveBeenCalledWith({
                behavior: 'smooth',
                block: 'end',
            });
        });

        it('should not throw error when lastMessageRef is null', () => {
            const { result } = renderHook(() => useChatScroll([], false));

            expect(() => {
                act(() => {
                    result.current.scrollToBottom();
                });
            }).not.toThrow();
        });

        it('should be callable multiple times', () => {
            const { result } = renderHook(() => useChatScroll([], false));
            const mockElement = document.createElement('div');

            act(() => {
                result.current.lastMessageRef.current = mockElement;
            });

            act(() => {
                result.current.scrollToBottom();
                result.current.scrollToBottom();
                result.current.scrollToBottom();
            });

            expect(mockScrollIntoView).toHaveBeenCalledTimes(3);
        });
    });

    describe('handleScroll', () => {
        it('should not throw error when scrollContainerRef is null', () => {
            const { result } = renderHook(() => useChatScroll([], false));

            expect(() => {
                act(() => {
                    result.current.handleScroll();
                });
            }).not.toThrow();
        });

        it('should hide scroll button when at bottom with no messages', () => {
            const { result } = renderHook(() => useChatScroll([], false));
            const mockElement = document.createElement('div');
            Object.defineProperty(mockElement, 'scrollTop', { value: 0, writable: true });
            Object.defineProperty(mockElement, 'scrollHeight', { value: 100, writable: true });
            Object.defineProperty(mockElement, 'clientHeight', { value: 100, writable: true });

            act(() => {
                result.current.scrollContainerRef.current = mockElement;
            });

            act(() => {
                result.current.handleScroll();
            });

            expect(result.current.showScrollButton).toBe(false);
        });

        it('should show scroll button when not at bottom and messages exist', () => {
            const messages = [{ id: 1 }, { id: 2 }];
            const { result } = renderHook(() => useChatScroll(messages, false));
            const mockElement = document.createElement('div');
            Object.defineProperty(mockElement, 'scrollTop', { value: 0, writable: true });
            Object.defineProperty(mockElement, 'scrollHeight', { value: 1000, writable: true });
            Object.defineProperty(mockElement, 'clientHeight', { value: 100, writable: true });

            act(() => {
                result.current.scrollContainerRef.current = mockElement;
            });

            act(() => {
                result.current.handleScroll();
            });

            expect(result.current.showScrollButton).toBe(true);
        });

        it('should hide scroll button when at bottom', () => {
            const messages = [{ id: 1 }];
            const { result } = renderHook(() => useChatScroll(messages, false));
            const mockElement = document.createElement('div');
            Object.defineProperty(mockElement, 'scrollTop', { value: 950, writable: true });
            Object.defineProperty(mockElement, 'scrollHeight', { value: 1000, writable: true });
            Object.defineProperty(mockElement, 'clientHeight', { value: 100, writable: true });

            act(() => {
                result.current.scrollContainerRef.current = mockElement;
            });

            act(() => {
                result.current.handleScroll();
            });

            expect(result.current.showScrollButton).toBe(false);
        });

        it('should consider within 100px of bottom as at bottom', () => {
            const messages = [{ id: 1 }];
            const { result } = renderHook(() => useChatScroll(messages, false));
            const mockElement = document.createElement('div');
            Object.defineProperty(mockElement, 'scrollTop', { value: 850, writable: true });
            Object.defineProperty(mockElement, 'scrollHeight', { value: 1000, writable: true });
            Object.defineProperty(mockElement, 'clientHeight', { value: 100, writable: true });

            act(() => {
                result.current.scrollContainerRef.current = mockElement;
            });

            act(() => {
                result.current.handleScroll();
            });

            expect(result.current.showScrollButton).toBe(false);
        });
    });

    describe('Auto-scroll on new messages', () => {
        it('should auto-scroll when new message is added', async () => {
            const { result, rerender } = renderHook(
                ({ messages, isBotTyping }) => useChatScroll(messages, isBotTyping),
                { initialProps: { messages: [{ id: 1 }], isBotTyping: false } }
            );

            const mockElement = document.createElement('div');

            act(() => {
                result.current.lastMessageRef.current = mockElement;
            });

            act(() => {
                rerender({ messages: [{ id: 1 }, { id: 2 }], isBotTyping: false });
            });

            await waitFor(() => {
                expect(mockScrollIntoView).toHaveBeenCalled();
            });
        });

        it('should auto-scroll when bot starts typing', async () => {
            const { result, rerender } = renderHook(
                ({ messages, isBotTyping }) => useChatScroll(messages, isBotTyping),
                { initialProps: { messages: [{ id: 1 }], isBotTyping: false } }
            );

            const mockElement = document.createElement('div');

            act(() => {
                result.current.lastMessageRef.current = mockElement;
            });

            act(() => {
                rerender({ messages: [{ id: 1 }], isBotTyping: true });
            });

            await waitFor(() => {
                expect(mockScrollIntoView).toHaveBeenCalled();
            });
        });

        it('should not auto-scroll when lastMessageRef is null', async () => {
            const { rerender } = renderHook(
                ({ messages, isBotTyping }) => useChatScroll(messages, isBotTyping),
                { initialProps: { messages: [{ id: 1 }], isBotTyping: false } }
            );

            act(() => {
                rerender({ messages: [{ id: 1 }, { id: 2 }], isBotTyping: false });
            });

            await waitFor(() => {
                expect(mockScrollIntoView).not.toHaveBeenCalled();
            });
        });
    });

    describe('Edge Cases', () => {
        it('should handle empty messages array', () => {
            const { result } = renderHook(() => useChatScroll([], false));
            expect(result.current.showScrollButton).toBe(false);
        });

        it('should handle single message', () => {
            const { result } = renderHook(() => useChatScroll([{ id: 1 }], false));
            expect(result.current).toBeDefined();
        });

        it('should handle many messages', () => {
            const manyMessages = Array.from({ length: 1000 }, (_, i) => ({ id: i }));
            const { result } = renderHook(() => useChatScroll(manyMessages, false));
            expect(result.current).toBeDefined();
        });

        it('should handle rapid message additions', async () => {
            const { result, rerender } = renderHook(
                ({ messages }) => useChatScroll(messages, false),
                { initialProps: { messages: [] } }
            );

            const mockElement = document.createElement('div');

            act(() => {
                result.current.lastMessageRef.current = mockElement;
            });

            for (let i = 1; i <= 10; i++) {
                act(() => {
                    rerender({ messages: Array.from({ length: i }, (_, j) => ({ id: j })) });
                });
            }

            await waitFor(() => {
                expect(mockScrollIntoView).toHaveBeenCalled();
            });
        });
    });

    describe('Scroll behavior state management', () => {
        it('should maintain scroll state across multiple calls', () => {
            const messages = [{ id: 1 }];
            const { result } = renderHook(() => useChatScroll(messages, false));
            const mockElement = document.createElement('div');
            Object.defineProperty(mockElement, 'scrollTop', { value: 0, writable: true });
            Object.defineProperty(mockElement, 'scrollHeight', { value: 1000, writable: true });
            Object.defineProperty(mockElement, 'clientHeight', { value: 100, writable: true });

            act(() => {
                result.current.scrollContainerRef.current = mockElement;
            });

            act(() => {
                result.current.handleScroll();
            });

            expect(result.current.showScrollButton).toBe(true);

            Object.defineProperty(mockElement, 'scrollTop', { value: 950, writable: true });

            act(() => {
                result.current.handleScroll();
            });

            expect(result.current.showScrollButton).toBe(false);
        });
    });

    describe('Return value stability', () => {
        it('should return stable function references', () => {
            const { result, rerender } = renderHook(() => useChatScroll([], false));

            const initialScrollToBottom = result.current.scrollToBottom;
            const initialHandleScroll = result.current.handleScroll;

            rerender();

            expect(result.current.scrollToBottom).toBe(initialScrollToBottom);
            expect(result.current.handleScroll).toBe(initialHandleScroll);
        });

        it('should return stable ref objects', () => {
            const { result, rerender } = renderHook(() => useChatScroll([], false));

            const initialLastMessageRef = result.current.lastMessageRef;
            const initialScrollContainerRef = result.current.scrollContainerRef;

            rerender();

            expect(result.current.lastMessageRef).toBe(initialLastMessageRef);
            expect(result.current.scrollContainerRef).toBe(initialScrollContainerRef);
        });
    });
});
