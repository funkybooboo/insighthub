/**
 * Global setup for Vitest - runs once before all test files
 */
import { JSDOM } from 'jsdom';

export default function setup() {
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
    jsdomWindow.Element.prototype.scrollIntoView = () => {};

    // Set up global window and document
    (global as unknown as { window: typeof jsdomWindow }).window = jsdomWindow;
    global.document = jsdomWindow.document;
    // Skip navigator as it's read-only in some environments
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

    // Create localStorage mock
    const localStorageMock = (() => {
        const store: Record<string, string> = {};

        return {
            getItem: (key: string) => store[key] || null,
            setItem: (key: string, value: string) => {
                store[key] = value.toString();
            },
            removeItem: (key: string) => {
                delete store[key];
            },
            clear: () => {
                Object.keys(store).forEach((key) => delete store[key]);
            },
            key: (index: number): string | null => {
                const keys = Object.keys(store);
                return keys[index] || null;
            },
            get length() {
                return Object.keys(store).length;
            },
        };
    })();

    // Set localStorage on all global objects
    (globalThis as unknown as { localStorage: typeof localStorageMock }).localStorage =
        localStorageMock;
    if (typeof global !== 'undefined') {
        (global as unknown as { localStorage: typeof localStorageMock }).localStorage =
            localStorageMock;
    }
}
