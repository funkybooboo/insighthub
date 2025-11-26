// Custom Cypress commands for InsightHub E2E testing

/**
 * Login command
 * Logs in a users with the provided credentials
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
 * Logs out the current users
 */
Cypress.Commands.add('logout', () => {
    // Find and click logout button (usually in users menu)
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
 * Creates a new users account
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
 * Send chats message command
 * Sends a message in the chats interface
 */
Cypress.Commands.add('sendChatMessage', (message) => {
    // Find chats input and type message
    cy.findByPlaceholderText(/type.*message|enter.*message/i).type(message);

    // Click send button or press Enter
    cy.findByRole('button', { name: /send/i }).click();

    // Wait for the message to appear in the chats
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

/**
 * Wait for document to be indexed command
 * Waits for a document to complete the full Vector RAG pipeline
 */
Cypress.Commands.add('waitForDocumentIndexed', (documentId, timeout = 180000) => {
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
                    return response.status === 200 && response.body.status === 'ready';
                });
        },
        {
            timeout,
            interval: 3000,
            errorMsg: `Document ${documentId} was not indexed within ${timeout}ms`,
        }
    );
});

/**
 * Query Vector RAG command
 * Sends a query and waits for Vector RAG response with context
 */
Cypress.Commands.add('queryVectorRAG', (query, expectContext = true) => {
    cy.sendChatMessage(query);

    // Wait for bot response
    cy.get('[data-testid="bot-message"]', { timeout: 120000 }).should('exist');

    if (expectContext) {
        // Should show retrieved context
        cy.get('[data-testid="context-display"]').should('exist');
    }

    // Return the response for further assertions
    return cy.get('[data-testid="bot-message"]').last();
});

/**
 * Verify retrieved context command
 * Opens context display and verifies chunks and scores
 */
Cypress.Commands.add('verifyRetrievedContext', (expectedChunkCount?: number, minScore?: number) => {
    // Expand context display
    cy.findByRole('button', { name: /show.*context|view.*sources/i }).click();

    // Verify context is visible
    cy.get('[data-testid="context-chunks"]').should('be.visible');

    if (expectedChunkCount !== undefined) {
        cy.get('[data-testid="context-chunk-item"]').should('have.length', expectedChunkCount);
    }

    if (minScore !== undefined) {
        cy.get('[data-testid="chunk-score"]')
            .first()
            .invoke('text')
            .then((scoreText) => {
                const score = parseFloat(scoreText);
                expect(score).to.be.gte(minScore);
            });
    }
});

/**
 * Create Vector RAG workspace command
 * Creates a workspace specifically configured for Vector RAG
 */
Cypress.Commands.add('createVectorWorkspace', (name, config) => {
    cy.findByRole('button', { name: /create.*workspace|new workspace/i }).click();

    // Basic info
    cy.findByLabelText(/workspace name|name/i).type(name);
    cy.findByLabelText(/description/i).type(config.description || 'Vector RAG test workspace');

    // RAG type
    cy.get('[data-testid="rag-type-select"]').select('vector');

    // Vector RAG configuration
    if (config.chunkingAlgorithm) {
        cy.get('[data-testid="chunking-algorithm-select"]').select(config.chunkingAlgorithm);
    }

    if (config.embeddingAlgorithm) {
        cy.get('[data-testid="embedding-algorithm-select"]').select(config.embeddingAlgorithm);
    }

    if (config.chunkSize) {
        cy.findByLabelText(/chunk.*size/i)
            .clear()
            .type(config.chunkSize.toString());
    }

    if (config.chunkOverlap) {
        cy.findByLabelText(/chunk.*overlap/i)
            .clear()
            .type(config.chunkOverlap.toString());
    }

    if (config.topK) {
        cy.findByLabelText(/top.*k/i)
            .clear()
            .type(config.topK.toString());
    }

    // Create
    cy.findByRole('button', { name: /create|save/i }).click();

    // Wait for workspace to appear
    cy.contains(name).should('be.visible');

    // Wait for ready status
    cy.contains(name)
        .parent()
        .within(() => {
            cy.get('[data-testid="status-badge"]', { timeout: 120000 }).should(
                'contain.text',
                /ready/i
            );
        });
});

/**
 * Upload and wait for document command
 * Uploads a document and waits for it to be fully indexed
 */
Cypress.Commands.add('uploadAndIndexDocument', (filePath, timeout = 180000) => {
    // Upload file
    cy.get('input[type="file"]').attachFile(filePath);

    // Get filename from path
    const filename = filePath.split('/').pop() || filePath;

    // Wait for upload success
    cy.contains(/upload.*success/i, { timeout: 30000 }).should('be.visible');

    // Wait for document to be ready
    cy.contains(filename)
        .parent()
        .within(() => {
            cy.get('[data-testid="status-badge"]', { timeout }).should('contain.text', /ready/i);
        });

    // Return filename for further use
    cy.wrap(filename);
});

/**
 * Get vector statistics command
 * Fetches vector database statistics for a workspace
 */
Cypress.Commands.add('getVectorStats', (workspaceId) => {
    return cy.window().then((win) => {
        const token = win.localStorage.getItem('token');

        return cy
            .request({
                url: `${Cypress.env('apiUrl')}/workspaces/${workspaceId}/vector-stats`,
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })
            .then((response) => {
                return cy.wrap(response.body);
            });
    });
});

/**
 * Get document chunks command
 * Fetches chunks for a specific document
 */
Cypress.Commands.add('getDocumentChunks', (documentId) => {
    return cy.window().then((win) => {
        const token = win.localStorage.getItem('token');

        return cy
            .request({
                url: `${Cypress.env('apiUrl')}/documents/${documentId}/chunks`,
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })
            .then((response) => {
                return cy.wrap(response.body.chunks);
            });
    });
});
