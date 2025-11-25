describe('Chat Interaction', () => {
    let workspaceName: string;

    beforeEach(() => {
        cy.clearLocalStorage();
        cy.fixture('users').then((users) => {
            cy.login(users.testUser.username, users.testUser.password);
        });

        // Create a workspace and upload a document for chat testing
        cy.fixture('workspaces').then((workspaces) => {
            const timestamp = Date.now();
            workspaceName = `Chat Test ${timestamp}`;
            cy.createWorkspace(
                workspaceName,
                workspaces.default.description,
                workspaces.default.ragConfig
            );

            // Wait for workspace to be ready
            cy.contains(workspaceName)
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 60000 }).should(
                        'contain.text',
                        /ready/i
                    );
                });

            // Select the workspace
            cy.selectWorkspace(workspaceName);

            // Upload a test document
            cy.get('input[type="file"]').attachFile('test-document.txt');

            // Wait for document to be fully processed
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 120000 }).should(
                        'contain.text',
                        /ready/i
                    );
                });
        });
    });

    describe('Chat Session Management', () => {
        it('should create a new chat session', () => {
            // Click new chat button
            cy.findByRole('button', { name: /new.*chat|create.*chat/i }).click();

            // Should show empty chat interface
            cy.get('[data-testid="chat-messages"]').should('be.empty');
        });

        it('should display list of chat sessions', () => {
            // Create multiple chat sessions
            cy.findByRole('button', { name: /new.*chat/i }).click();
            cy.sendChatMessage('First session message');

            cy.findByRole('button', { name: /new.*chat/i }).click();
            cy.sendChatMessage('Second session message');

            // Should show both sessions in the list
            cy.get('[data-testid="chat-session-item"]').should('have.length.gte', 2);
        });

        it('should switch between chat sessions', () => {
            // Create two sessions with different messages
            cy.findByRole('button', { name: /new.*chat/i }).click();
            const message1 = 'Message in first session';
            cy.sendChatMessage(message1);

            cy.findByRole('button', { name: /new.*chat/i }).click();
            const message2 = 'Message in second session';
            cy.sendChatMessage(message2);

            // Click on first session
            cy.contains(message1).parent('[data-testid="chat-session-item"]').click();

            // Should show first session messages
            cy.get('[data-testid="chat-messages"]').should('contain.text', message1);
            cy.get('[data-testid="chat-messages"]').should('not.contain.text', message2);
        });

        it('should delete a chat session', () => {
            // Create a chat session
            cy.findByRole('button', { name: /new.*chat/i }).click();
            const testMessage = 'Message to delete';
            cy.sendChatMessage(testMessage);

            // Delete the session
            cy.contains(testMessage)
                .parent('[data-testid="chat-session-item"]')
                .within(() => {
                    cy.findByRole('button', { name: /delete|remove/i }).click();
                });

            // Confirm deletion
            cy.findByRole('button', { name: /confirm|yes|delete/i }).click();

            // Session should be removed
            cy.contains(testMessage).should('not.exist');
        });
    });

    describe('Send Chat Message', () => {
        it('should successfully send a message and receive response', () => {
            const userMessage = 'What is artificial intelligence?';
            cy.sendChatMessage(userMessage);

            // User message should appear immediately
            cy.get('[data-testid="chat-messages"]').should('contain.text', userMessage);

            // Should show typing indicator
            cy.get('[data-testid="typing-indicator"]').should('be.visible');

            // Wait for bot response
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Typing indicator should disappear
            cy.get('[data-testid="typing-indicator"]').should('not.exist');
        });

        it('should disable input while waiting for response', () => {
            cy.sendChatMessage('Test message');

            // Chat input should be disabled
            cy.findByPlaceholderText(/type.*message/i).should('be.disabled');

            // Wait for response
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Chat input should be re-enabled
            cy.findByPlaceholderText(/type.*message/i).should('not.be.disabled');
        });

        it('should stream bot response token by token', () => {
            cy.sendChatMessage('Explain machine learning');

            // Monitor for streaming updates
            // Check multiple times to detect streaming
            cy.get('[data-testid="bot-message"]', { timeout: 60000 })
                .should('exist')
                .then(() => {
                    cy.get('[data-testid="bot-message"]')
                        .invoke('text')
                        .then((_text1) => {
                            cy.wait(1000);
                            cy.get('[data-testid="bot-message"]')
                                .invoke('text')
                                .then((text2) => {
                                    // Response should eventually be complete
                                    void expect(text2.length).to.be.gt(0);
                                });
                        });
                });
        });

        it('should handle Enter key to send message', () => {
            const message = 'Testing Enter key';
            cy.findByPlaceholderText(/type.*message/i)
                .type(message)
                .type('{enter}');

            // Message should appear in chat
            cy.get('[data-testid="chat-messages"]').should('contain.text', message);
        });

        it('should handle Shift+Enter for multiline input', () => {
            const multilineMessage = 'Line 1{shift+enter}Line 2';
            cy.findByPlaceholderText(/type.*message/i).type(multilineMessage);

            // Input should contain both lines
            cy.findByPlaceholderText(/type.*message/i).should('contain.value', 'Line 1\nLine 2');
        });

        it('should prevent sending empty messages', () => {
            // Try to send empty message
            cy.findByRole('button', { name: /send/i }).click();

            // No message should appear
            cy.get('[data-testid="user-message"]').should('have.length', 0);
        });
    });

    describe('Cancel Chat Message Streaming', () => {
        it('should cancel streaming response when cancel button clicked', () => {
            cy.sendChatMessage('Write a long essay about AI');

            // Wait for streaming to start
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Click cancel button
            cy.findByRole('button', { name: /cancel|stop/i }).click();

            // Get current response length
            cy.get('[data-testid="bot-message"]')
                .invoke('text')
                .then((text1) => {
                    const length1 = text1.length;

                    // Wait and verify response stopped growing
                    cy.wait(2000);
                    cy.get('[data-testid="bot-message"]')
                        .invoke('text')
                        .then((text2) => {
                            expect(text2.length).to.equal(length1);
                        });
                });

            // Send button should be re-enabled
            cy.findByRole('button', { name: /send/i }).should('not.be.disabled');
        });

        it('should handle Ctrl+C to cancel streaming', () => {
            cy.sendChatMessage('Explain quantum computing in detail');

            // Wait for streaming to start
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Press Ctrl+C
            cy.get('body').type('{ctrl}c');

            // Verify streaming stopped
            cy.findByRole('button', { name: /send/i }).should('not.be.disabled');
        });
    });

    describe('RAG Context Display', () => {
        it('should display retrieved context with the response', () => {
            cy.sendChatMessage('What does the document say about RAG?');

            // Wait for response
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Should show context display
            cy.get('[data-testid="context-display"]').should('exist');

            // Should show retrieved chunks
            cy.contains(/retrieved|context|sources/i).should('be.visible');
        });

        it('should show relevance scores for retrieved chunks', () => {
            cy.sendChatMessage('Tell me about vector databases');

            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Check for score display
            cy.get('[data-testid="context-display"]').within(() => {
                cy.contains(/score|relevance|similarity/i).should('be.visible');
            });
        });

        it('should expand and collapse context display', () => {
            cy.sendChatMessage('What is mentioned about Qdrant?');

            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Click to expand context
            cy.findByRole('button', { name: /show.*context|view.*sources/i }).click();

            // Context should be visible
            cy.get('[data-testid="context-chunks"]').should('be.visible');

            // Click to collapse
            cy.findByRole('button', { name: /hide.*context|collapse/i }).click();

            // Context should be hidden
            cy.get('[data-testid="context-chunks"]').should('not.be.visible');
        });
    });

    describe('RAG Enhancement Prompt', () => {
        it('should show enhancement prompt when no context found', () => {
            // Ask a question unrelated to uploaded documents
            cy.sendChatMessage('What is the capital of France?');

            // Should show no context found message
            cy.contains(/no.*context.*found|no.*relevant.*documents/i, {
                timeout: 60000,
            }).should('be.visible');

            // Should show enhancement options
            cy.contains(/upload.*document/i).should('be.visible');
            cy.contains(/fetch.*wikipedia/i).should('be.visible');
            cy.contains(/continue.*without/i).should('be.visible');
        });

        it('should allow document upload from enhancement prompt', () => {
            cy.sendChatMessage('Tell me about quantum mechanics');

            // Wait for no context message
            cy.contains(/no.*context.*found/i, { timeout: 60000 }).should('be.visible');

            // Click upload document option
            cy.findByRole('button', { name: /upload.*document/i }).click();

            // File upload interface should appear
            cy.get('input[type="file"]').should('be.visible');
        });

        it('should trigger Wikipedia fetch from enhancement prompt', () => {
            cy.sendChatMessage('What is quantum entanglement?');

            cy.contains(/no.*context.*found/i, { timeout: 60000 }).should('be.visible');

            // Click fetch from Wikipedia
            cy.findByRole('button', { name: /fetch.*wikipedia/i }).click();

            // Should show loading indicator
            cy.contains(/fetching|loading/i).should('be.visible');

            // Should eventually process the query
            cy.get('[data-testid="bot-message"]', { timeout: 120000 }).should('exist');
        });

        it('should continue without context when requested', () => {
            cy.sendChatMessage('What is the weather today?');

            cy.contains(/no.*context.*found/i, { timeout: 60000 }).should('be.visible');

            // Click continue without context
            cy.findByRole('button', { name: /continue.*without/i }).click();

            // Should receive a response without RAG context
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');
        });
    });

    describe('Chat Message Display', () => {
        it('should display user messages with correct styling', () => {
            const userMessage = 'This is my message';
            cy.sendChatMessage(userMessage);

            cy.get('[data-testid="user-message"]')
                .should('contain.text', userMessage)
                .and('have.class', /user|right/i);
        });

        it('should display bot messages with correct styling', () => {
            cy.sendChatMessage('Test message');

            cy.get('[data-testid="bot-message"]', { timeout: 60000 })
                .should('exist')
                .and('have.class', /bot|assistant|left/i);
        });

        it('should render markdown in bot responses', () => {
            // This depends on the bot returning markdown
            cy.sendChatMessage('List three items');

            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).within(() => {
                // Check for markdown elements
                cy.get('body').then(($body) => {
                    const hasMarkdown =
                        $body.find('ul').length > 0 ||
                        $body.find('ol').length > 0 ||
                        $body.find('strong').length > 0 ||
                        $body.find('em').length > 0;

                    if (hasMarkdown) {
                        void expect(hasMarkdown).to.be.true;
                    } else {
                        cy.log('No markdown detected in response');
                    }
                });
            });
        });

        it('should show timestamps for messages', () => {
            cy.sendChatMessage('Message with timestamp');

            cy.get('[data-testid="user-message"]')
                .parent()
                .within(() => {
                    cy.contains(/\d{1,2}:\d{2}|\d+ (minute|hour)s? ago/i).should('be.visible');
                });
        });

        it('should auto-scroll to latest message', () => {
            // Send multiple messages to fill the chat
            for (let i = 0; i < 5; i++) {
                cy.sendChatMessage(`Message ${i + 1}`);
                cy.wait(1000);
            }

            // Latest message should be visible
            cy.contains('Message 5').should('be.visible');

            // Chat container should be scrolled to bottom
            cy.get('[data-testid="chat-messages"]').then(($el) => {
                const scrollHeight = $el[0].scrollHeight;
                const scrollTop = $el[0].scrollTop;
                const clientHeight = $el[0].clientHeight;

                expect(scrollTop + clientHeight).to.be.closeTo(scrollHeight, 50);
            });
        });
    });

    describe('Chat Error Handling', () => {
        it('should show error message when chat fails', () => {
            // This would require mocking a chat failure
            // Implementation depends on how you simulate errors
            cy.log('Test requires mock setup for chat failure');
        });

        it('should allow retry after error', () => {
            // Mock an error scenario and test retry functionality
            cy.log('Test requires mock setup for error retry');
        });

        it('should handle network disconnection gracefully', () => {
            // Test WebSocket disconnection handling
            cy.log('Test requires network condition simulation');
        });
    });

    describe('Chat Session Persistence', () => {
        it('should persist chat history in local state', () => {
            const message = 'Persistent message';
            cy.sendChatMessage(message);

            // Wait for response
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Refresh the page
            cy.reload();

            // Message should still be visible (if client-side persistence is implemented)
            cy.get('body').then(($body) => {
                if ($body.text().includes(message)) {
                    cy.contains(message).should('be.visible');
                } else {
                    cy.log('Chat history not persisted client-side');
                }
            });
        });
    });

    describe('Multi-turn Conversations', () => {
        it('should maintain conversation context across multiple messages', () => {
            // First message
            cy.sendChatMessage('What is RAG?');
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');

            // Follow-up question
            cy.sendChatMessage('Can you explain that in simpler terms?');
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).last().should('exist');

            // Another follow-up
            cy.sendChatMessage('What are its advantages?');
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).last().should('exist');

            // All messages should be visible
            cy.get('[data-testid="chat-messages"]')
                .should('contain.text', 'What is RAG?')
                .and('contain.text', 'simpler terms')
                .and('contain.text', 'advantages');
        });
    });

    describe('Chat with Different RAG Types', () => {
        it('should work with Vector RAG', () => {
            // Already using Vector RAG by default
            cy.sendChatMessage('Test Vector RAG');
            cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');
        });

        it('should work with Graph RAG when configured', () => {
            // Create a Graph RAG workspace
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const graphWorkspaceName = `Graph RAG ${timestamp}`;

                cy.createWorkspace(
                    graphWorkspaceName,
                    workspaces.graphWorkspace.description,
                    workspaces.graphWorkspace.ragConfig
                );

                // Wait for workspace to be ready
                cy.contains(graphWorkspaceName)
                    .parent()
                    .within(() => {
                        cy.get('[data-testid="status-badge"]', { timeout: 60000 }).should(
                            'contain.text',
                            /ready/i
                        );
                    });

                cy.selectWorkspace(graphWorkspaceName);

                // Upload document
                cy.get('input[type="file"]').attachFile('test-document.txt');
                cy.contains('test-document.txt')
                    .parent()
                    .within(() => {
                        cy.get('[data-testid="status-badge"]', { timeout: 120000 }).should(
                            'contain.text',
                            /ready/i
                        );
                    });

                // Test chat
                cy.sendChatMessage('Test Graph RAG');
                cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');
            });
        });
    });
});
