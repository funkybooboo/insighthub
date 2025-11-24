/**
 * Global setup for Vitest - runs once before all test files
 */

export default function setup() {
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
