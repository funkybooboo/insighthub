/**
 * Global setup for Vitest - runs once before all test files
 */

export default function setup() {
    // Create localStorage mock
    const localStorageMock = (() => {
        let store: Record<string, string> = {};

        return {
            getItem: (key: string) => store[key] || null,
            setItem: (key: string, value: string) => {
                store[key] = value.toString();
            },
            removeItem: (key: string) => {
                delete store[key];
            },
            clear: () => {
                store = {};
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
    (globalThis as any).localStorage = localStorageMock;
    if (typeof global !== 'undefined') {
        (global as any).localStorage = localStorageMock;
    }
}
