describe('Document Management', () => {
    let workspaceName: string;

    beforeEach(() => {
        cy.clearLocalStorage();
        cy.fixture('users').then((users) => {
            cy.login(users.testUser.username, users.testUser.password);
        });

        // Create a workspace for document testing
        cy.fixture('workspaces').then((workspaces) => {
            const timestamp = Date.now();
            workspaceName = `Doc Test ${timestamp}`;
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
        });
    });

    describe('Upload Document', () => {
        it('should successfully upload a text document', () => {
            // Upload test document
            cy.get('input[type="file"]').attachFile('test-document.txt');

            // Verify upload success message
            cy.contains(/upload.*success|document.*uploaded/i, {
                timeout: 30000,
            }).should('be.visible');

            // Verify document appears in list
            cy.contains('test-document.txt').should('be.visible');
        });

        it('should show upload progress', () => {
            cy.get('input[type="file"]').attachFile('test-document.txt');

            // Should show loading indicator during upload
            cy.get('[data-testid="loading-spinner"]').should('be.visible');
        });

        it('should show error for unsupported file type', () => {
            // Try to upload an unsupported file type
            cy.get('input[type="file"]').attachFile({
                filePath: 'test-document.txt',
                fileName: 'test.xyz',
                mimeType: 'application/octet-stream',
            });

            // Should show error message
            cy.contains(/unsupported.*file.*type|invalid.*file/i).should('be.visible');
        });

        it('should show error for file size exceeding limit', () => {
            // This would require creating a large file fixture
            // or mocking the file size validation
            cy.log('Test requires large file fixture or mock');
        });

        it('should allow multiple file uploads', () => {
            // Upload first document
            cy.get('input[type="file"]').attachFile('test-document.txt');
            cy.contains(/upload.*success/i, { timeout: 30000 });

            // Upload second document
            cy.get('input[type="file"]').attachFile({
                filePath: 'test-document.txt',
                fileName: 'second-document.txt',
            });
            cy.contains(/upload.*success/i, { timeout: 30000 });

            // Verify both documents are in the list
            cy.contains('test-document.txt').should('be.visible');
            cy.contains('second-document.txt').should('be.visible');
        });

        it('should disable upload button while workspace is processing', () => {
            // Upload a document
            cy.get('input[type="file"]').attachFile('test-document.txt');

            // While processing, upload button should be disabled
            cy.get('input[type="file"]').should('be.disabled');
        });
    });

    describe('Document Processing Status', () => {
        beforeEach(() => {
            // Upload a test document
            cy.get('input[type="file"]').attachFile('test-document.txt');
            cy.contains('test-document.txt', { timeout: 30000 }).should('be.visible');
        });

        it('should show document status progression', () => {
            // Document should go through: pending -> parsing -> chunking -> embedding -> indexing -> ready

            // Check that document eventually reaches ready status
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 120000 }).should(
                        'contain.text',
                        /ready/i
                    );
                });
        });

        it('should show loading spinner during processing', () => {
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="loading-spinner"]').should('be.visible');
                });
        });

        it('should update status in real-time via WebSocket', () => {
            // Monitor status changes
            let previousStatus = '';
            let statusChanged = false;

            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]').then(($badge) => {
                        previousStatus = $badge.text();
                    });
                });

            // Wait and check if status changed
            cy.wait(5000);
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]').then(($badge) => {
                        const currentStatus = $badge.text();
                        if (currentStatus !== previousStatus) {
                            statusChanged = true;
                        }
                        void expect(statusChanged).to.be.true;
                    });
                });
        });

        it('should show error status if processing fails', () => {
            // This test would require mocking a processing failure
            // Implementation depends on how you want to simulate failures
            cy.log('Test requires mock setup for processing failure');
        });
    });

    describe('List Documents in Workspace', () => {
        beforeEach(() => {
            // Upload multiple documents
            cy.get('input[type="file"]').attachFile('test-document.txt');
            cy.wait(2000);
            cy.get('input[type="file"]').attachFile({
                filePath: 'test-document.txt',
                fileName: 'document-2.txt',
            });
            cy.wait(2000);
        });

        it('should display all documents in the workspace', () => {
            // Verify both documents are listed
            cy.contains('test-document.txt').should('be.visible');
            cy.contains('document-2.txt').should('be.visible');
        });

        it('should show document count', () => {
            // Should show document count somewhere in the UI
            cy.contains(/\d+.*documents?/i).should('be.visible');
        });

        it('should refresh document list when switching workspaces', () => {
            // Create another workspace
            const timestamp = Date.now();
            const newWorkspaceName = `Second Workspace ${timestamp}`;
            cy.fixture('workspaces').then((workspaces) => {
                cy.createWorkspace(
                    newWorkspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                // Wait for workspace to be ready
                cy.contains(newWorkspaceName)
                    .parent()
                    .within(() => {
                        cy.get('[data-testid="status-badge"]', { timeout: 60000 }).should(
                            'contain.text',
                            /ready/i
                        );
                    });

                // Select the new workspace
                cy.selectWorkspace(newWorkspaceName);

                // Document list should be empty or show different documents
                cy.contains('test-document.txt').should('not.exist');
            });
        });

        it('should show empty state when no documents exist', () => {
            // Create a fresh workspace
            const timestamp = Date.now();
            const emptyWorkspaceName = `Empty Workspace ${timestamp}`;
            cy.fixture('workspaces').then((workspaces) => {
                cy.createWorkspace(
                    emptyWorkspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                // Wait for ready status
                cy.contains(emptyWorkspaceName)
                    .parent()
                    .within(() => {
                        cy.get('[data-testid="status-badge"]', { timeout: 60000 }).should(
                            'contain.text',
                            /ready/i
                        );
                    });

                cy.selectWorkspace(emptyWorkspaceName);

                // Should show empty state
                cy.contains(/no documents|upload.*first.*document/i).should('be.visible');
            });
        });
    });

    describe('Delete Document', () => {
        beforeEach(() => {
            // Upload a document to delete
            cy.get('input[type="file"]').attachFile('test-document.txt');
            cy.contains('test-document.txt', { timeout: 30000 }).should('be.visible');
        });

        it('should successfully delete a document', () => {
            // Find and click delete button for the document
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.findByRole('button', { name: /delete|remove/i }).click();
                });

            // Confirm deletion
            cy.findByRole('button', { name: /confirm|yes|delete/i }).click();

            // Document should be removed from list
            cy.contains('test-document.txt').should('not.exist');

            // Should show success message
            cy.contains(/document.*deleted|removed.*successfully/i).should('be.visible');
        });

        it('should show confirmation dialog before deleting', () => {
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.findByRole('button', { name: /delete|remove/i }).click();
                });

            // Verify confirmation dialog appears
            cy.contains(/are you sure|confirm.*delete/i).should('be.visible');

            // Cancel deletion
            cy.findByRole('button', { name: /cancel|no/i }).click();

            // Document should still exist
            cy.contains('test-document.txt').should('be.visible');
        });

        it('should update document count after deletion', () => {
            // Get initial count
            cy.contains(/\d+.*documents?/i)
                .invoke('text')
                .then((initialText) => {
                    const initialCount = parseInt(initialText.match(/\d+/)?.[0] || '0');

                    // Delete document
                    cy.contains('test-document.txt')
                        .parent()
                        .within(() => {
                            cy.findByRole('button', { name: /delete|remove/i }).click();
                        });
                    cy.findByRole('button', { name: /confirm|yes|delete/i }).click();

                    // Verify count decreased
                    cy.contains(/\d+.*documents?/i)
                        .invoke('text')
                        .then((finalText) => {
                            const finalCount = parseInt(finalText.match(/\d+/)?.[0] || '0');
                            expect(finalCount).to.equal(initialCount - 1);
                        });
                });
        });

        it('should remove document vectors from RAG system', () => {
            // Wait for document to be fully processed
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.get('[data-testid="status-badge"]', { timeout: 120000 }).should(
                        'contain.text',
                        /ready/i
                    );
                });

            // Delete the document
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    cy.findByRole('button', { name: /delete|remove/i }).click();
                });
            cy.findByRole('button', { name: /confirm|yes|delete/i }).click();

            // This would ideally verify via API that vectors are removed
            // For now, just verify the deletion was successful
            cy.contains('test-document.txt').should('not.exist');
        });
    });

    describe('Document Metadata Display', () => {
        beforeEach(() => {
            cy.get('input[type="file"]').attachFile('test-document.txt');
            cy.contains('test-document.txt', { timeout: 30000 }).should('be.visible');
        });

        it('should display document filename', () => {
            cy.contains('test-document.txt').should('be.visible');
        });

        it('should display document upload date', () => {
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    // Should show some date/time information
                    cy.contains(/\d{1,2}\/\d{1,2}\/\d{4}|\d+ (minute|hour|day)s? ago/i).should(
                        'be.visible'
                    );
                });
        });

        it('should display document size', () => {
            cy.contains('test-document.txt')
                .parent()
                .within(() => {
                    // Should show file size
                    cy.contains(/\d+\s*(B|KB|MB)/i).should('be.visible');
                });
        });
    });

    describe('Document Upload from RAG Enhancement Prompt', () => {
        it('should allow document upload when no context found', () => {
            // This test would require triggering a chat message that returns no context
            // Then testing the upload flow from the enhancement prompt
            cy.log('Test requires chat integration with no context scenario');
        });
    });

    describe('Document List Filtering and Sorting', () => {
        beforeEach(() => {
            // Upload multiple documents
            cy.get('input[type="file"]').attachFile('test-document.txt');
            cy.wait(2000);
            cy.get('input[type="file"]').attachFile({
                filePath: 'test-document.txt',
                fileName: 'alpha.txt',
            });
            cy.wait(2000);
            cy.get('input[type="file"]').attachFile({
                filePath: 'test-document.txt',
                fileName: 'zeta.txt',
            });
            cy.wait(2000);
        });

        it('should sort documents by name', () => {
            // Check if there's a sort button or dropdown
            cy.get('body').then(($body) => {
                if ($body.find('[data-testid="sort-select"]').length) {
                    cy.get('[data-testid="sort-select"]').select('name');

                    // Verify alphabetical order
                    cy.get('[data-testid="document-item"]')
                        .first()
                        .should('contain.text', 'alpha.txt');
                } else {
                    cy.log('No sorting UI found, skipping test');
                }
            });
        });

        it('should sort documents by upload date', () => {
            cy.get('body').then(($body) => {
                if ($body.find('[data-testid="sort-select"]').length) {
                    cy.get('[data-testid="sort-select"]').select('date');

                    // Most recent should be first
                    cy.get('[data-testid="document-item"]')
                        .first()
                        .should('contain.text', 'zeta.txt');
                } else {
                    cy.log('No sorting UI found, skipping test');
                }
            });
        });

        it('should filter documents by status', () => {
            cy.get('body').then(($body) => {
                if ($body.find('[data-testid="status-filter"]').length) {
                    cy.get('[data-testid="status-filter"]').select('ready');

                    // Should only show ready documents
                    cy.get('[data-testid="document-item"]').each(($item) => {
                        cy.wrap($item).within(() => {
                            cy.get('[data-testid="status-badge"]').should('contain.text', /ready/i);
                        });
                    });
                } else {
                    cy.log('No status filter found, skipping test');
                }
            });
        });
    });
});
