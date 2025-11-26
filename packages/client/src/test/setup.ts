// Mock Audio before any other imports
global.Audio = vi.fn().mockImplementation(function (this: unknown) {
    (
        this as { play: ReturnType<typeof vi.fn>; pause: ReturnType<typeof vi.fn>; volume: number }
    ).play = vi.fn();
    (
        this as { play: ReturnType<typeof vi.fn>; pause: ReturnType<typeof vi.fn>; volume: number }
    ).pause = vi.fn();
    (
        this as { play: ReturnType<typeof vi.fn>; pause: ReturnType<typeof vi.fn>; volume: number }
    ).volume = 0;
    return this;
});

// Mock audio files
vi.mock('@/assets/sounds/pop.mp3', () => ({
    default: 'mock-pop-sound',
}));

vi.mock('@/assets/sounds/notification.mp3', () => ({
    default: 'mock-notification-sound',
}));

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi, beforeAll, afterAll } from 'vitest';
import { server } from './msw-server';

// MSW setup
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterAll(() => server.close());
afterEach(() => server.resetHandlers());

// Clean up after each test
afterEach(() => {
    cleanup();
});

// Mock window.matchMedia
if (typeof window !== 'undefined') {
    Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation((query: string) => ({
            matches: false,
            media: query,
            onchange: null,
            addListener: vi.fn(),
            removeListener: vi.fn(),
            addEventListener: vi.fn(),
            removeEventListener: vi.fn(),
            dispatchEvent: vi.fn(),
        })),
    });
}

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
    constructor() {}
    disconnect() {}
    observe() {}
    takeRecords(): IntersectionObserverEntry[] {
        return [];
    }
    unobserve() {}
} as unknown as typeof IntersectionObserver;

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
    constructor() {}
    disconnect() {}
    observe() {}
    unobserve() {}
} as unknown as typeof ResizeObserver;
