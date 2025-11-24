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

// Debug
console.log('Document setup complete:', {
    document: typeof global.document,
    body: !!global.document?.body,
    window: typeof global.window,
});

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, vi } from 'vitest';

// MSW setup removed - using direct mocking instead

// Mock localStorage using Storage API
const localStorageMock = (() => {
    const store: Record<string, string> = {};

    return {
        get length(): number {
            return Object.keys(store).length;
        },

        clear(): void {
            Object.keys(store).forEach((key) => delete store[key]);
        },

        getItem(key: string): string | null {
            return store[key] ?? null;
        },

        key(index: number): string | null {
            return Object.keys(store)[index] ?? null;
        },

        removeItem(key: string): void {
            delete store[key];
        },

        setItem(key: string, value: string): void {
            store[key] = String(value);
        },
    };
})();

// Assign to global
(global as unknown as { localStorage: typeof localStorageMock }).localStorage = localStorageMock;
(globalThis as unknown as { localStorage: typeof localStorageMock }).localStorage =
    localStorageMock;

// Reset localStorage before each test
beforeEach(() => {
    localStorageMock.clear();
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
