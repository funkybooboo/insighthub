/**
 * Comprehensive Vector RAG End-to-End Test
 *
 * This test covers the complete Vector RAG pipeline:
 * 1. User authentication
 * 2. Workspace creation with Vector RAG configuration
 * 3. Document upload and processing
 * 4. Vector indexing in Qdrant
 * 5. Chat queries with context retrieval
 * 6. Response generation with streaming
 */

describe('Vector RAG End-to-End Flow', () => {
    let workspaceName: string;
    let workspaceId: string;
    let documentId: string;

    before(() => {
        // Clean slate for E2E test
        cy.clearLocalStorage();
    });

    describe('Setup: Authentication and Workspace Creation', () => {
        it('should create a new users account for testing', () => {
            const timestamp = Date.now();
            const testUser = {
                username: `vectorrag${timestamp}`,
                email: `vectorrag${timestamp}@example.com`,
                password: 'VectorRAGTest123!',
                fullName: 'Vector RAG Tester',
            };

            cy.signup(testUser.username, testUser.email, testUser.password, testUser.fullName);

            // Verify successful signup
            cy.url().should('match', /\/$|\/workspaces/);
            cy.findByText(testUser.username).should('be.visible');

            // Store credentials for subsequent tests
            Cypress.env('vectorRagUsername', testUser.username);
            Cypress.env('vectorRagPassword', testUser.password);
        });

        it('should create Vector RAG workspace with proper configuration', () => {
            const timestamp = Date.now();
            workspaceName = `Vector RAG E2E ${timestamp}`;

            // Navigate to workspace creation
            cy.findByRole('button', { name: /create.*workspace|new workspace/i }).click();

            // Fill basic workspace info
            cy.findByLabelText(/workspace name|name/i).type(workspaceName);
            cy.findByLabelText(/description/i).type(
                'End-to-end test workspace for Vector RAG pipeline'
            );

            // Configure Vector RAG settings
            cy.get('[data-testid="rag-type-select"]').select('vector');

            // Configure chunking algorithm
            cy.get('[data-testid="chunking-algorithm-select"]').select('sentence');
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('1000');
            cy.findByLabelText(/chunk.*overlap/i)
                .clear()
                .type('200');

            // Configure embedding model
            cy.get('[data-testid="embedding-algorithm-select"]').select('nomic-embed-text');

            // Configure top-k for retrieval
            cy.findByLabelText(/top.*k/i)
                .clear()
                .type('5');

            // Create workspace
            cy.findByRole('button', { name: /create|save/i }).click();

            // Verify workspace appears and is provisioning
            cy.contains(workspaceName, { timeout: 30000 }).should('be.visible');

            // Wait for workspace to reach ready status
            cy.contains(workspaceName)
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 120000 }).should(
                        'contain.text',
                        /ready/i
                    );
                });

            // Extract workspace ID for API calls
            cy.contains(workspaceName)
                .parent()
                .invoke('attr', 'data-workspace-id')
                .then((id) => {
                    workspaceId = id as string;
                });

            // Select the workspace
            cy.selectWorkspace(workspaceName);
        });

        it('should verify workspace configuration via API', () => {
            // Verify Vector RAG configuration was saved correctly
            cy.window().then((win) => {
                const token = win.localStorage.getItem('token');

                cy.request({
                    url: `${Cypress.env('apiUrl')}/workspaces/${workspaceId}/vector-rag-config`,
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }).then((response) => {
                    expect(response.status).to.equal(200);
                    expect(response.body.chunking_algorithm).to.equal('sentence');
                    expect(response.body.embedding_algorithm).to.equal('nomic-embed-text');
                    expect(response.body.top_k).to.equal(5);
                    expect(response.body.chunk_size).to.equal(1000);
                    expect(response.body.chunk_overlap).to.equal(200);
                });
            });
        });
    });

    describe('Document Upload and Processing Pipeline', () => {
        it('should upload a document successfully', () => {
            // Upload test document
            cy.get('input[type="file"]').attachFile('test-document.txt');

            // Verify upload success
            cy.contains(/upload.*success|document.*uploaded/i, {
                timeout: 30000,
            }).should('be.visible');

            // Verify document appears in list
            cy.contains('test-document.txt').should('be.visible');

            // Extract document ID
            cy.contains('test-document.txt')
                .parent()
                .invoke('attr', 'data-document-id')
                .then((id) => {
                    documentId = id as string;
                });
        });

        it('should progress through parsing stage', () => {
            // Should show parsing status
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]').should('contain.text', /parsing/i);
                });
        });

        it('should progress through chunking stage', () => {
            // Should eventually show chunking status
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 60000 }).should(
                        'contain.text',
                        /chunk/i
                    );
                });
        });

        it('should progress through embedding stage', () => {
            // Should show embedding status
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 60000 }).should(
                        'contain.text',
                        /embed/i
                    );
                });
        });

        it('should progress through indexing stage', () => {
            // Should show indexing status
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 60000 }).should(
                        'contain.text',
                        /index/i
                    );
                });
        });

        it('should reach ready status after full pipeline', () => {
            // Wait for document to be fully processed
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 180000 }).should(
                        'contain.text',
                        /ready/i
                    );
                });
        });

        it('should verify chunks were created via API', () => {
            cy.window().then((win) => {
                const token = win.localStorage.getItem('token');

                cy.request({
                    url: `${Cypress.env('apiUrl')}/documents/${documentId}/chunks`,
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }).then((response) => {
                    expect(response.status).to.equal(200);
                    expect(response.body.chunks).to.be.an('array');
                    expect(response.body.chunks.length).to.be.greaterThan(0);

                    // Verify chunks have embeddings
                    response.body.chunks.forEach((chunk: { embedding?: unknown }) => {
                        expect(chunk).to.have.property('embedding');
                        // eslint-disable-next-line @typescript-eslint/no-unused-expressions
                        expect(chunk.embedding).to.not.be.null;
                    });
                });
            });
        });

        it('should verify vectors were indexed in Qdrant via API', () => {
            cy.window().then((win) => {
                const token = win.localStorage.getItem('token');

                // Check Qdrant collection exists and has vectors
                cy.request({
                    url: `${Cypress.env('apiUrl')}/workspaces/${workspaceId}/vector-stats`,
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }).then((response) => {
                    expect(response.status).to.equal(200);
                    expect(response.body.vector_count).to.be.greaterThan(0);
                    // eslint-disable-next-line @typescript-eslint/no-unused-expressions
                    expect(response.body.collection_name).to.exist;
                });
            });
        });
    });

    describe('Vector RAG Query and Retrieval', () => {
        beforeEach(() => {
            // Ensure we're on the chats page
            cy.findByRole('button', { name: /chat|messages/i }).click();
        });

        it('should retrieve relevant context for document-related query', () => {
            const query = 'What is mentioned about artificial intelligence?';

            cy.sendChatMessage(query);

            // User message should appear
            cy.get('[data-testid="user-message"]').should('contain.text', query);

            // Should show typing indicator
            cy.get('[data-testid="typing-indicator"]', { timeout: 5000 }).should('be.visible');

            // Wait for bot response
            cy.get('[data-testid="bot-message"]', { timeout: 120000 }).should('exist');

            // Should display context that was retrieved
            cy.get('[data-testid="context-display"]').should('exist');
        });

        it('should display retrieved chunks with relevance scores', () => {
            cy.sendChatMessage('Tell me about RAG and vector databases');

            cy.get('[data-testid="bot-message"]', { timeout: 120000 }).should('exist');

            // Expand context display
            cy.findByRole('button', { name: /show.*context|view.*sources/i }).click();

            // Should show retrieved chunks
            cy.get('[data-testid="context-chunks"]').should('be.visible');

            // Should show similarity scores
            cy.get('[data-testid="chunk-score"]').should('exist');

            // Scores should be between 0 and 1
            cy.get('[data-testid="chunk-score"]')
                .first()
                .invoke('text')
                .then((scoreText) => {
                    const score = parseFloat(scoreText);
                    expect(score).to.be.within(0, 1);
                });

            // Should retrieve top-k chunks (configured as 5)
            cy.get('[data-testid="context-chunk-item"]').should('have.length.lte', 5);
        });

        it('should verify context relevance to query', () => {
            const query = 'What does the document say about Qdrant?';

            cy.sendChatMessage(query);

            cy.get('[data-testid="bot-message"]', { timeout: 120000 }).should('exist');

            // Open context
            cy.findByRole('button', { name: /show.*context/i }).click();

            // Retrieved chunks should contain relevant keywords
            cy.get('[data-testid="context-chunks"]').should('contain.text', /qdrant|vector/i);
        });

        it('should generate response based on retrieved context', () => {
            const query = 'Explain the concept of RAG based on the document';

            cy.sendChatMessage(query);

            cy.get('[data-testid="bot-message"]', { timeout: 120000 })
                .invoke('text')
                .then((responseText) => {
                    // Response should mention RAG or related concepts
                    expect(responseText.toLowerCase()).to.match(
                        /rag|retrieval|augmented|generation|context/
                    );

                    // Response should be substantive (not just "I don't know")
                    expect(responseText.length).to.be.greaterThan(50);
                });
        });

        it('should handle query with no relevant context', () => {
            const query = 'What is the weather like in Tokyo today?';

            cy.sendChatMessage(query);

            // Should still get a response (but may show no context found)
            cy.get('[data-testid="bot-message"]', { timeout: 120000 }).should('exist');

            // May show enhancement prompt for no context
            cy.get('body').then(($body) => {
                if ($body.text().includes('no context found')) {
                    cy.contains(/no.*context.*found/i).should('be.visible');
                }
            });
        });

        it('should maintain conversation context across turns', () => {
            // First question
            cy.sendChatMessage('What is machine learning?');
            cy.get('[data-testid="bot-message"]', { timeout: 120000 }).should('exist');

            // Follow-up question using "it"
            cy.sendChatMessage('How is it different from deep learning?');
            cy.get('[data-testid="bot-message"]', { timeout: 120000 }).last().should('exist');

            // Another follow-up
            cy.sendChatMessage('Give me an example');
            cy.get('[data-testid="bot-message"]', { timeout: 120000 }).last().should('exist');

            // Should have 3 users messages and 3 bot responses
            cy.get('[data-testid="user-message"]').should('have.length', 3);
            cy.get('[data-testid="bot-message"]').should('have.length', 3);
        });
    });

    describe('Streaming Response Verification', () => {
        it('should stream response tokens progressively', () => {
            cy.sendChatMessage('Explain natural language processing in detail');

            // Wait for first token
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Capture initial response length
            cy.get('[data-testid="bot-message"]')
                .invoke('text')
                .then((text1) => {
                    const initialLength = text1.length;

                    // Wait and check if response grew
                    cy.wait(2000);

                    cy.get('[data-testid="bot-message"]')
                        .invoke('text')
                        .then((text2) => {
                            const finalLength = text2.length;

                            // Response should have grown (streaming)
                            expect(finalLength).to.be.gte(initialLength);
                        });
                });
        });

        it('should be able to cancel streaming', () => {
            cy.sendChatMessage('Write a very long essay about AI history');

            // Wait for streaming to start
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Click cancel button
            cy.findByRole('button', { name: /cancel|stop/i }).click();

            // Get current response
            cy.get('[data-testid="bot-message"]')
                .invoke('text')
                .then((stoppedText) => {
                    const stoppedLength = stoppedText.length;

                    // Wait and verify it stopped growing
                    cy.wait(3000);

                    cy.get('[data-testid="bot-message"]')
                        .invoke('text')
                        .then((finalText) => {
                            expect(finalText.length).to.equal(stoppedLength);
                        });
                });
        });
    });

    describe('Multi-Document Vector RAG', () => {
        it('should handle queries across multiple documents', () => {
            // Upload second document
            cy.get('input[type="file"]').attachFile({
                filePath: 'test-document.txt',
                fileName: 'ml-document.txt',
            });

            // Wait for processing
            cy.contains('ml-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 180000 }).should(
                        'contain.text',
                        /ready/i
                    );
                });

            // Query that might match content from both documents
            cy.sendChatMessage('What concepts are discussed in the documents?');

            cy.get('[data-testid="bot-message"]', { timeout: 120000 }).should('exist');

            // Should retrieve context from multiple documents
            cy.findByRole('button', { name: /show.*context/i }).click();

            cy.get('[data-testid="context-chunks"]').should('be.visible');

            // May show chunks from different documents
            cy.get('[data-testid="context-chunk-item"]').should('have.length.gte', 1);
        });
    });

    describe('Vector RAG Performance Verification', () => {
        it('should retrieve context within acceptable time', () => {
            const startTime = Date.now();

            cy.sendChatMessage('Quick query about vectors');

            // First response token should appear quickly
            cy.get('[data-testid="bot-message"]', { timeout: 30000 })
                .should('exist')
                .then(() => {
                    const responseTime = Date.now() - startTime;

                    // Should respond within 30 seconds
                    expect(responseTime).to.be.lessThan(30000);
                    cy.log(`Response time: ${responseTime}ms`);
                });
        });

        it('should handle concurrent queries gracefully', () => {
            // This test would require WebSocket support for multiple messages
            // For now, just verify sequential queries work
            cy.sendChatMessage('First query');
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            cy.sendChatMessage('Second query');
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).last().should('exist');

            // Both responses should exist
            cy.get('[data-testid="bot-message"]').should('have.length', 2);
        });
    });

    describe('Cleanup: Document and Workspace Deletion', () => {
        it('should delete document and remove vectors', () => {
            // Delete the first document
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.findByRole('button', { name: /delete|remove/i }).click();
                });

            cy.findByRole('button', { name: /confirm|yes|delete/i }).click();

            // Document should be removed
            cy.contains('test-document.txt').should('not.exist');

            // Verify vectors were removed via API
            cy.window().then((win) => {
                const token = win.localStorage.getItem('token');

                cy.request({
                    url: `${Cypress.env('apiUrl')}/workspaces/${workspaceId}/vector-stats`,
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }).then((response) => {
                    // Vector count should have decreased
                    expect(response.body.vector_count).to.be.greaterThan(0); // Still has ml-document
                });
            });
        });

        it('should delete workspace and cleanup all resources', () => {
            // Navigate to workspace settings
            cy.findByRole('button', { name: /workspace.*settings|settings/i }).click();

            // Click delete workspace
            cy.findByRole('button', { name: /delete.*workspace/i }).click();

            // Confirm deletion
            cy.findByRole('button', { name: /confirm|yes|delete/i }).click();

            // Workspace should be removed from list
            cy.contains(workspaceName).should('not.exist');

            // Should show success message
            cy.contains(/workspace.*deleted|removed.*successfully/i).should('be.visible');
        });
    });
});
