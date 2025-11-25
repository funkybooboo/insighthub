describe('Workspace Management', () => {
    beforeEach(() => {
        cy.clearLocalStorage();
        cy.fixture('users').then((users) => {
            cy.login(users.testUser.username, users.testUser.password);
        });
    });

    describe('List Workspaces', () => {
        it('should display list of workspaces', () => {
            // Verify workspace list is visible
            cy.findByRole('heading', { name: /workspaces/i }).should('be.visible');

            // Verify at least one workspace exists or empty state
            cy.get('body').then(($body) => {
                if ($body.text().includes('No workspaces')) {
                    cy.contains(/no workspaces|create.*workspace/i).should('be.visible');
                } else {
                    cy.get('[data-testid="workspace-item"]').should('have.length.gt', 0);
                }
            });
        });

        it('should show workspace status badges', () => {
            // Create a new workspace to ensure we have one
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                cy.createWorkspace(
                    `${workspaces.default.name} ${timestamp}`,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                // Check for status badge
                cy.get('[data-testid="status-badge"]')
                    .first()
                    .should('be.visible')
                    .and('contain.text', /provisioning|ready/i);
            });
        });
    });

    describe('Select Active Workspace', () => {
        it('should select and activate a workspace', () => {
            // Create a workspace first
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `${workspaces.default.name} ${timestamp}`;
                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                // Select the workspace
                cy.selectWorkspace(workspaceName);

                // Verify workspace is highlighted/active
                cy.contains(workspaceName)
                    .parent()
                    .should('have.class', /active|selected/i);
            });
        });

        it('should update UI when switching workspaces', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspace1 = `Workspace 1 ${timestamp}`;
                const workspace2 = `Workspace 2 ${timestamp}`;

                // Create two workspaces
                cy.createWorkspace(workspace1, 'First workspace', workspaces.default.ragConfig);
                cy.createWorkspace(workspace2, 'Second workspace', workspaces.default.ragConfig);

                // Select first workspace
                cy.selectWorkspace(workspace1);
                cy.contains(workspace1).should('be.visible');

                // Select second workspace
                cy.selectWorkspace(workspace2);
                cy.contains(workspace2).should('be.visible');
            });
        });
    });

    describe('Create New Workspace', () => {
        it('should successfully create a workspace with default RAG config', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `Test Workspace ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                // Verify workspace appears in list
                cy.contains(workspaceName).should('be.visible');

                // Verify status is provisioning
                cy.contains(workspaceName)
                    .parent()
                    .within(() => {
                        cy.get('[data-testid="status-badge"]').should(
                            'contain.text',
                            /provisioning|ready/i
                        );
                    });
            });
        });

        it('should create workspace with custom RAG configuration', () => {
            const timestamp = Date.now();
            const customConfig = {
                retriever_type: 'vector',
                chunk_size: 1500,
                chunk_overlap: 300,
                top_k: 10,
            };

            cy.createWorkspace(
                `Custom RAG Workspace ${timestamp}`,
                'Testing custom RAG config',
                customConfig
            );

            // Verify workspace is created
            cy.contains(`Custom RAG Workspace ${timestamp}`).should('be.visible');
        });

        it('should show validation errors for invalid workspace name', () => {
            cy.findByRole('button', { name: /create.*workspace|new workspace/i }).click();

            // Try to submit without a name
            cy.findByRole('button', { name: /create|save/i }).click();

            // Should show validation error
            cy.contains(/name.*required|workspace.*name.*cannot be empty/i).should('be.visible');
        });

        it('should pre-populate form with default RAG config', () => {
            cy.fixture('workspaces').then((workspaces) => {
                cy.findByRole('button', { name: /create.*workspace|new workspace/i }).click();

                // Verify RAG config fields have default values
                cy.findByLabelText(/chunk.*size/i).should(
                    'have.value',
                    workspaces.default.ragConfig.chunk_size.toString()
                );
                cy.findByLabelText(/top.*k/i).should(
                    'have.value',
                    workspaces.default.ragConfig.top_k.toString()
                );
            });
        });
    });

    describe('View Workspace Details', () => {
        it('should display workspace details page', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `Details Test ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                // Navigate to workspace details
                cy.contains(workspaceName).click();
                cy.findByRole('link', { name: /workspace.*settings|view.*details/i }).click();

                // Verify details are displayed
                cy.contains(workspaceName).should('be.visible');
                cy.contains(workspaces.default.description).should('be.visible');

                // Verify RAG config is displayed
                cy.contains(/rag.*config|configuration/i).should('be.visible');
            });
        });

        it('should show document and session counts', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `Stats Test ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                cy.contains(workspaceName).click();
                cy.findByRole('link', { name: /workspace.*settings|view.*details/i }).click();

                // Check for document and session counts
                cy.contains(/\d+.*documents?/i).should('be.visible');
                cy.contains(/\d+.*sessions?/i).should('be.visible');
            });
        });

        it('should show workspace status with loading indicator', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `Status Test ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                cy.contains(workspaceName).click();

                // Check for status indicator
                cy.get('[data-testid="status-badge"]').should('be.visible');
            });
        });
    });

    describe('Edit Workspace Details', () => {
        it('should successfully update workspace name and description', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const originalName = `Edit Test ${timestamp}`;
                const updatedName = `Updated ${originalName}`;

                cy.createWorkspace(
                    originalName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                // Navigate to workspace settings
                cy.contains(originalName).click();
                cy.findByRole('link', { name: /workspace.*settings|view.*details/i }).click();

                // Click edit button
                cy.findByRole('button', { name: /edit/i }).click();

                // Update name and description
                cy.findByLabelText(/workspace.*name|name/i)
                    .clear()
                    .type(updatedName);
                cy.findByLabelText(/description/i)
                    .clear()
                    .type('Updated description');

                // Save changes
                cy.findByRole('button', { name: /save/i }).click();

                // Verify success message
                cy.contains(/workspace.*updated|changes.*saved/i).should('be.visible');

                // Verify changes in UI
                cy.contains(updatedName).should('be.visible');
                cy.contains('Updated description').should('be.visible');
            });
        });

        it('should not allow editing RAG config after provisioning', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `RAG Edit Test ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                // Wait for workspace to be ready
                cy.contains(workspaceName).click();
                cy.findByRole('link', { name: /workspace.*settings|view.*details/i }).click();

                // Try to edit
                cy.findByRole('button', { name: /edit/i }).click();

                // RAG config fields should be read-only
                cy.findByLabelText(/chunk.*size/i).should('be.disabled');
            });
        });

        it('should show validation error for empty workspace name', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `Validation Test ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                cy.contains(workspaceName).click();
                cy.findByRole('link', { name: /workspace.*settings|view.*details/i }).click();

                cy.findByRole('button', { name: /edit/i }).click();

                // Clear workspace name
                cy.findByLabelText(/workspace.*name|name/i).clear();
                cy.findByRole('button', { name: /save/i }).click();

                // Should show validation error
                cy.contains(/name.*required|workspace.*name.*cannot be empty/i).should(
                    'be.visible'
                );
            });
        });
    });

    describe('Delete Workspace', () => {
        it('should successfully delete a workspace', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `Delete Test ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                cy.contains(workspaceName).click();
                cy.findByRole('link', { name: /workspace.*settings|view.*details/i }).click();

                // Click delete button
                cy.findByRole('button', { name: /delete/i }).click();

                // Confirm deletion
                cy.findByRole('button', { name: /confirm|yes|delete/i }).click();

                // Should show deleting status
                cy.contains(/deleting/i).should('be.visible');

                // Should redirect to workspaces list
                cy.url().should('match', /\/workspaces$/);

                // Workspace should eventually disappear from list
                cy.contains(workspaceName, { timeout: 30000 }).should('not.exist');
            });
        });

        it('should show confirmation dialog before deleting', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `Confirm Delete ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                cy.contains(workspaceName).click();
                cy.findByRole('link', { name: /workspace.*settings|view.*details/i }).click();

                // Click delete button
                cy.findByRole('button', { name: /delete/i }).click();

                // Verify confirmation dialog appears
                cy.contains(/are you sure|confirm.*delete/i).should('be.visible');

                // Cancel deletion
                cy.findByRole('button', { name: /cancel|no/i }).click();

                // Workspace should still exist
                cy.contains(workspaceName).should('be.visible');
            });
        });

        it('should disable all workspace actions during deletion', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `Disable Test ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                cy.contains(workspaceName).click();
                cy.findByRole('link', { name: /workspace.*settings|view.*details/i }).click();

                // Initiate deletion
                cy.findByRole('button', { name: /delete/i }).click();
                cy.findByRole('button', { name: /confirm|yes|delete/i }).click();

                // Edit and delete buttons should be disabled
                cy.findByRole('button', { name: /edit/i }).should('be.disabled');
                cy.findByRole('button', { name: /delete/i }).should('be.disabled');

                // File upload should be disabled
                cy.get('input[type="file"]').should('be.disabled');
            });
        });
    });

    describe('Workspace Real-time Status Updates', () => {
        it('should update workspace status from provisioning to ready', () => {
            cy.fixture('workspaces').then((workspaces) => {
                const timestamp = Date.now();
                const workspaceName = `Status Update ${timestamp}`;

                cy.createWorkspace(
                    workspaceName,
                    workspaces.default.description,
                    workspaces.default.ragConfig
                );

                // Initially should be provisioning
                cy.contains(workspaceName)
                    .parent()
                    .within(() => {
                        cy.get('[data-testid="status-badge"]').should(
                            'contain.text',
                            /provisioning/i
                        );
                    });

                // Wait for status to change to ready
                cy.contains(workspaceName)
                    .parent()
                    .within(() => {
                        cy.get('[data-testid="status-badge"]', { timeout: 60000 }).should(
                            'contain.text',
                            /ready/i
                        );
                    });
            });
        });

        it('should show error status if provisioning fails', () => {
            // This test would require mocking a failed provisioning scenario
            // Implementation depends on how you want to simulate failures in tests
            cy.log('Test requires mock setup for failed provisioning');
        });
    });

    describe('Default RAG Configuration', () => {
        it('should fetch and display default RAG config in settings', () => {
            // Navigate to settings
            cy.findByRole('button', { name: /settings|profile/i }).click();

            // Find RAG configuration section
            cy.contains(/default.*rag.*config/i).should('be.visible');

            // Verify config fields are displayed
            cy.findByLabelText(/chunk.*size/i).should('be.visible');
            cy.findByLabelText(/top.*k/i).should('be.visible');
        });

        it('should save default RAG configuration', () => {
            cy.findByRole('button', { name: /settings|profile/i }).click();

            // Update default RAG config
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('1500');
            cy.findByLabelText(/chunk.*overlap/i)
                .clear()
                .type('300');

            // Save changes
            cy.findByRole('button', { name: /save.*changes/i }).click();

            // Verify success message
            cy.contains(/settings.*saved|configuration.*updated/i).should('be.visible');
        });

        it('should use saved default RAG config for new workspaces', () => {
            // Update default config
            cy.findByRole('button', { name: /settings|profile/i }).click();
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('2000');
            cy.findByRole('button', { name: /save.*changes/i }).click();

            // Create new workspace
            cy.findByRole('button', { name: /create.*workspace|new workspace/i }).click();

            // Verify default config is pre-populated
            cy.findByLabelText(/chunk.*size/i).should('have.value', '2000');
        });
    });
});
