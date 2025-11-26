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

// Set up JSDOM first, before any other imports
import { JSDOM } from 'jsdom';

const { window: jsdomWindow } = new JSDOM('<html><body></body></html>', {
    url: 'http://localhost:3000',
    pretendToBeVisual: true,
});

// Add missing methods that React expects
jsdomWindow.Element.prototype.attachEvent = function (
    event: string,
    handler: (event: Event) => void
) {
    return this.addEventListener(event.replace(/^on/, ''), handler);
};

jsdomWindow.Element.prototype.detachEvent = function (
    event: string,
    handler: (event: Event) => void
) {
    return this.removeEventListener(event.replace(/^on/, ''), handler);
};

jsdomWindow.Element.prototype.detachEvent = function (event: string, handler: EventListener) {
    return this.removeEventListener(event.replace(/^on/, ''), handler as EventListener);
};

// Mock scrollIntoView method
jsdomWindow.Element.prototype.scrollIntoView = vi.fn();

// Set up global window and document
(global as unknown as { window: typeof jsdomWindow }).window = jsdomWindow;
global.document = jsdomWindow.document;
global.navigator = jsdomWindow.navigator;
global.HTMLInputElement = jsdomWindow.HTMLInputElement;
global.HTMLTextAreaElement = jsdomWindow.HTMLTextAreaElement;
global.HTMLButtonElement = jsdomWindow.HTMLButtonElement;
global.HTMLElement = jsdomWindow.HTMLElement;
global.Element = jsdomWindow.Element;
global.Node = jsdomWindow.Node;
global.Event = jsdomWindow.Event;
global.CustomEvent = jsdomWindow.CustomEvent;
global.MouseEvent = jsdomWindow.MouseEvent;
global.KeyboardEvent = jsdomWindow.KeyboardEvent;

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, vi, beforeAll, afterAll } from 'vitest';
import { server } from './msw-server';

// MSW setup
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterAll(() => server.close());
afterEach(() => server.resetHandlers());

// Reset localStorage before each test
beforeEach(() => {
    localStorage.clear();
});

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
