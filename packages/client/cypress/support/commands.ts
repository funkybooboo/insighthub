// Custom Cypress commands for InsightHub E2E testing

/**
 * Login command
 * Logs in a user with the provided credentials
 */
Cypress.Commands.add(
    'login',
    (username = Cypress.env('testUsername'), password = Cypress.env('testPassword')) => {
        cy.visit('/login');
        cy.findByLabelText(/username/i).type(username);
        cy.findByLabelText(/password/i).type(password);
        cy.findByRole('button', { name: /login|sign in/i }).click();

        // Wait for redirect to main page
        cy.url().should('not.include', '/login');
        cy.url().should('match', /\/$|\/workspaces/);

        // Verify token is stored
        cy.window().then((win) => {
            const token = win.localStorage.getItem('token');
            void expect(token).to.exist;
        });
    }
);

/**
 * Logout command
 * Logs out the current user
 */
Cypress.Commands.add('logout', () => {
    // Find and click logout button (usually in user menu)
    cy.findByRole('button', { name: /logout|sign out/i }).click();

    // Wait for redirect to login page
    cy.url().should('include', '/login');

    // Verify token is removed
    cy.window().then((win) => {
        const token = win.localStorage.getItem('token');
        void expect(token).to.be.null;
    });
});

/**
 * Signup command
 * Creates a new user account
 */
Cypress.Commands.add('signup', (username, email, password, fullName = '') => {
    cy.visit('/signup');
    cy.findByLabelText(/username/i).type(username);
    cy.findByLabelText(/email/i).type(email);
    cy.findByLabelText(/^password/i).type(password);

    if (fullName) {
        cy.findByLabelText(/full name|name/i).type(fullName);
    }

    cy.findByRole('button', { name: /sign up|create account/i }).click();

    // Wait for redirect to main page
    cy.url().should('not.include', '/signup');
    cy.url().should('match', /\/$|\/workspaces/);

    // Verify token is stored
    cy.window().then((win) => {
        const token = win.localStorage.getItem('token');
        void expect(token).to.exist;
    });
});

/**
 * Create workspace command
 * Creates a new workspace with the given configuration
 */
Cypress.Commands.add('createWorkspace', (name, description, ragConfig) => {
    // Click create workspace button
    cy.findByRole('button', { name: /create.*workspace|new workspace/i }).click();

    // Fill out the form
    cy.findByLabelText(/workspace name|name/i).type(name);
    cy.findByLabelText(/description/i).type(description);

    // If ragConfig is provided, configure it
    if (ragConfig) {
        // This depends on your RAG config form structure
        if (ragConfig.retriever_type) {
            cy.findByLabelText(/retriever.*type|rag.*type/i).select(ragConfig.retriever_type);
        }
        if (ragConfig.chunk_size) {
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type(ragConfig.chunk_size.toString());
        }
        if (ragConfig.top_k) {
            cy.findByLabelText(/top.*k/i)
                .clear()
                .type(ragConfig.top_k.toString());
        }
    }

    // Submit the form
    cy.findByRole('button', { name: /create|save/i }).click();

    // Wait for the workspace to appear in the list
    cy.contains(name).should('be.visible');
});

/**
 * Select workspace command
 * Selects a workspace by name
 */
Cypress.Commands.add('selectWorkspace', (workspaceName) => {
    cy.contains(workspaceName).click();

    // Verify the workspace is now active
    cy.contains(workspaceName).should('have.class', /active|selected/i);
});

/**
 * Upload document command
 * Uploads a document to the specified workspace
 */
Cypress.Commands.add('uploadDocument', (filePath, _workspaceId) => {
    // Find the file upload input
    cy.get('input[type="file"]').attachFile(filePath);

    // Wait for upload to complete
    cy.contains(/upload.*success|document.*uploaded/i, { timeout: 30000 });
});

/**
 * Send chat message command
 * Sends a message in the chat interface
 */
Cypress.Commands.add('sendChatMessage', (message) => {
    // Find chat input and type message
    cy.findByPlaceholderText(/type.*message|enter.*message/i).type(message);

    // Click send button or press Enter
    cy.findByRole('button', { name: /send/i }).click();

    // Wait for the message to appear in the chat
    cy.contains(message).should('be.visible');
});

/**
 * Wait for document status command
 * Waits for a document to reach a specific status
 */
Cypress.Commands.add('waitForDocumentStatus', (documentId, status, timeout = 60000) => {
    cy.waitUntil(
        () => {
            return cy
                .request({
                    url: `${Cypress.env('apiUrl')}/documents/${documentId}`,
                    headers: {
                        Authorization: `Bearer ${window.localStorage.getItem('token')}`,
                    },
                    failOnStatusCode: false,
                })
                .then((response) => {
                    return response.status === 200 && response.body.status === status;
                });
        },
        {
            timeout,
            interval: 2000,
            errorMsg: `Document ${documentId} did not reach status ${status} within ${timeout}ms`,
        }
    );
});

/**
 * Wait for workspace status command
 * Waits for a workspace to reach a specific status
 */
Cypress.Commands.add('waitForWorkspaceStatus', (workspaceId, status, timeout = 60000) => {
    cy.waitUntil(
        () => {
            return cy
                .request({
                    url: `${Cypress.env('apiUrl')}/workspaces/${workspaceId}`,
                    headers: {
                        Authorization: `Bearer ${window.localStorage.getItem('token')}`,
                    },
                    failOnStatusCode: false,
                })
                .then((response) => {
                    return response.status === 200 && response.body.status === status;
                });
        },
        {
            timeout,
            interval: 2000,
            errorMsg: `Workspace ${workspaceId} did not reach status ${status} within ${timeout}ms`,
        }
    );
});

/**
 * Clear localStorage command
 * Clears all localStorage data
 */
Cypress.Commands.add('clearLocalStorage', () => {
    cy.window().then((win) => {
        win.localStorage.clear();
    });
});
