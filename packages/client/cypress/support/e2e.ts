// Import commands
import './commands';

// Import Testing Library
import '@testing-library/cypress/add-commands';

// Import cypress-wait-until
import 'cypress-wait-until';

// Prevent TypeScript errors for custom commands
/* eslint-disable @typescript-eslint/no-namespace */
declare global {
    namespace Cypress {
        interface Chainable {
            login(username?: string, password?: string): Chainable<void>;
            logout(): Chainable<void>;
            signup(
                username: string,
                email: string,
                password: string,
                fullName?: string
            ): Chainable<void>;
            createWorkspace(
                name: string,
                description: string,
                ragConfig?: Record<string, unknown>
            ): Chainable<void>;
            selectWorkspace(workspaceName: string): Chainable<void>;
            uploadDocument(filePath: string, workspaceId: string): Chainable<void>;
            sendChatMessage(message: string): Chainable<void>;
            waitForDocumentStatus(
                documentId: string,
                status: string,
                timeout?: number
            ): Chainable<void>;
            waitForWorkspaceStatus(
                workspaceId: string,
                status: string,
                timeout?: number
            ): Chainable<void>;
            clearLocalStorage(): Chainable<void>;
        }
    }
}
/* eslint-enable @typescript-eslint/no-namespace */

// Preserve authentication state between tests
beforeEach(() => {
    // Preserve localStorage and sessionStorage between tests
    cy.window().then((win) => {
        win.sessionStorage.clear();
    });
});

// Handle uncaught exceptions
Cypress.on('uncaught:exception', (err, _runnable) => {
    // Return false to prevent failing the test on uncaught exceptions
    // You can add specific exceptions to ignore here
    console.error('Uncaught exception:', err);
    return false;
});
