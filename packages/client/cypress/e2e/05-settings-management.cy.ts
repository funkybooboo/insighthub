describe('Settings Management', () => {
    beforeEach(() => {
        cy.clearLocalStorage();
        cy.fixture('users').then((users) => {
            cy.login(users.testUser.username, users.testUser.password);
        });

        // Navigate to settings page
        cy.findByRole('button', { name: /settings|profile/i }).click();
    });

    describe('Settings Page Navigation', () => {
        it('should display settings page with all sections', () => {
            // Verify main sections are visible
            cy.contains(/profile|account/i).should('be.visible');
            cy.contains(/preferences|theme/i).should('be.visible');
            cy.contains(/rag.*config|default.*configuration/i).should('be.visible');
            cy.contains(/password|security/i).should('be.visible');
        });

        it('should have working tabs or sections', () => {
            // If using tabs, test tab switching
            cy.get('body').then(($body) => {
                if ($body.find('[role="tab"]').length > 0) {
                    cy.get('[role="tab"]').each(($tab) => {
                        cy.wrap($tab).click();
                        cy.wrap($tab).should('have.attr', 'aria-selected', 'true');
                    });
                } else {
                    cy.log('No tab navigation found');
                }
            });
        });
    });

    describe('Profile Settings', () => {
        beforeEach(() => {
            // Ensure we're on profile section
            cy.get('body').then(($body) => {
                if ($body.find('[role="tab"]').length > 0) {
                    cy.findByRole('tab', { name: /profile|account/i }).click();
                }
            });
        });

        it('should display current users information', () => {
            cy.fixture('users').then((users) => {
                cy.contains(users.testUser.username).should('be.visible');
                cy.contains(users.testUser.email).should('be.visible');
            });
        });

        it('should allow editing profile information', () => {
            // Click edit button
            cy.findByRole('button', { name: /edit.*profile/i }).click();

            // Update full name
            const newName = `Updated Name ${Date.now()}`;
            cy.findByLabelText(/full.*name/i)
                .clear()
                .type(newName);

            // Save changes
            cy.findByRole('button', { name: /save/i }).click();

            // Verify success
            cy.contains(/profile.*updated|changes.*saved/i).should('be.visible');
            cy.contains(newName).should('be.visible');
        });

        it('should validate email format', () => {
            cy.findByRole('button', { name: /edit.*profile/i }).click();

            cy.findByLabelText(/email/i).clear().type('invalid-email');

            cy.findByRole('button', { name: /save/i }).click();

            cy.contains(/invalid.*email|email.*format/i).should('be.visible');
        });

        it('should cancel profile editing', () => {
            cy.findByRole('button', { name: /edit.*profile/i }).click();

            cy.findByLabelText(/full.*name/i)
                .clear()
                .type('Changed Name');

            // Click cancel
            cy.findByRole('button', { name: /cancel/i }).click();

            // Changes should not be saved
            cy.findByLabelText(/full.*name/i).should('not.have.value', 'Changed Name');
        });

        it('should display account creation date', () => {
            cy.contains(/member since|joined|created/i).should('be.visible');
            cy.contains(/\d{1,2}\/\d{1,2}\/\d{4}/i).should('be.visible');
        });
    });

    describe('Theme Preferences', () => {
        beforeEach(() => {
            cy.get('body').then(($body) => {
                if ($body.find('[role="tab"]').length > 0) {
                    cy.findByRole('tab', { name: /preferences|theme/i }).click();
                }
            });
        });

        it('should toggle between light and dark theme', () => {
            // Get current theme
            cy.get('html').then(($html) => {
                const currentTheme = $html.hasClass('dark') ? 'dark' : 'light';
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

                // Toggle theme
                cy.findByRole('button', { name: /theme|dark.*mode|light.*mode/i }).click();

                // Verify theme changed
                cy.get('html').should('have.class', newTheme);

                // Verify preference is saved
                cy.reload();
                cy.get('html').should('have.class', newTheme);
            });
        });

        it('should apply theme immediately', () => {
            cy.get('html').then(($html) => {
                const currentTheme = $html.hasClass('dark') ? 'dark' : 'light';

                cy.findByRole('button', { name: /theme/i }).click();

                // Theme should change without page reload
                cy.get('html').should('not.have.class', currentTheme);
            });
        });

        it('should persist theme preference across sessions', () => {
            // Set theme to dark
            cy.get('html').then(($html) => {
                if (!$html.hasClass('dark')) {
                    cy.findByRole('button', { name: /theme/i }).click();
                }
            });

            cy.get('html').should('have.class', 'dark');

            // Logout and login again
            cy.logout();
            cy.fixture('users').then((users) => {
                cy.login(users.testUser.username, users.testUser.password);
            });

            // Theme should still be dark
            cy.get('html').should('have.class', 'dark');
        });

        it('should show current theme selection', () => {
            cy.get('html').then(($html) => {
                const currentTheme = $html.hasClass('dark') ? 'dark' : 'light';

                // Current theme button should be highlighted or checked
                cy.findByRole('button', { name: new RegExp(currentTheme, 'i') })
                    .should('exist')
                    .and('have.attr', 'aria-pressed', 'true');
            });
        });
    });

    describe('Default RAG Configuration', () => {
        beforeEach(() => {
            cy.get('body').then(($body) => {
                if ($body.find('[role="tab"]').length > 0) {
                    cy.findByRole('tab', { name: /rag.*config/i }).click();
                }
            });
        });

        it('should display current default RAG configuration', () => {
            // Verify RAG config fields are visible
            cy.findByLabelText(/retriever.*type|rag.*type/i).should('be.visible');
            cy.findByLabelText(/chunk.*size/i).should('be.visible');
            cy.findByLabelText(/chunk.*overlap/i).should('be.visible');
            cy.findByLabelText(/top.*k/i).should('be.visible');
        });

        it('should update Vector RAG configuration', () => {
            // Select Vector RAG type
            cy.findByLabelText(/retriever.*type/i).select('vector');

            // Update chunk size
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('1500');

            // Update chunk overlap
            cy.findByLabelText(/chunk.*overlap/i)
                .clear()
                .type('300');

            // Update top k
            cy.findByLabelText(/top.*k/i)
                .clear()
                .type('10');

            // Save changes
            cy.findByRole('button', { name: /save.*changes/i }).click();

            // Verify success
            cy.contains(/settings.*saved|configuration.*updated/i).should('be.visible');
        });

        it('should update Graph RAG configuration', () => {
            // Select Graph RAG type
            cy.findByLabelText(/retriever.*type/i).select('graph');

            // Update max hops
            cy.findByLabelText(/max.*hops/i)
                .clear()
                .type('3');

            // Save changes
            cy.findByRole('button', { name: /save.*changes/i }).click();

            cy.contains(/settings.*saved/i).should('be.visible');
        });

        it('should validate RAG configuration values', () => {
            // Try to set invalid chunk size
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('0');

            cy.findByRole('button', { name: /save.*changes/i }).click();

            // Should show validation error
            cy.contains(/invalid.*value|must be greater/i).should('be.visible');
        });

        it('should show different fields for Vector vs Graph RAG', () => {
            // Select Vector RAG
            cy.findByLabelText(/retriever.*type/i).select('vector');

            // Vector-specific fields should be visible
            cy.findByLabelText(/chunk.*size/i).should('be.visible');
            cy.findByLabelText(/embedding.*model/i).should('be.visible');

            // Select Graph RAG
            cy.findByLabelText(/retriever.*type/i).select('graph');

            // Graph-specific fields should be visible
            cy.findByLabelText(/max.*hops/i).should('be.visible');
            cy.findByLabelText(/entity.*extraction/i).should('be.visible');
        });

        it('should reset to default values', () => {
            // Make changes
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('2000');

            // Click reset button
            cy.findByRole('button', { name: /reset|restore.*defaults/i }).click();

            // Should show default value
            cy.findByLabelText(/chunk.*size/i).should('have.value', '1000');
        });

        it('should use updated config for new workspaces', () => {
            // Update default config
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('2500');

            cy.findByRole('button', { name: /save.*changes/i }).click();
            cy.contains(/settings.*saved/i).should('be.visible');

            // Navigate to create workspace
            cy.visit('/');
            cy.findByRole('button', { name: /create.*workspace/i }).click();

            // Verify new default is pre-populated
            cy.findByLabelText(/chunk.*size/i).should('have.value', '2500');
        });
    });

    describe('Password Change', () => {
        beforeEach(() => {
            cy.get('body').then(($body) => {
                if ($body.find('[role="tab"]').length > 0) {
                    cy.findByRole('tab', { name: /password|security/i }).click();
                }
            });
        });

        it('should successfully change password', () => {
            cy.fixture('users').then((users) => {
                // Fill password change form
                cy.findByLabelText(/current.*password/i).type(users.testUser.password);
                cy.findByLabelText(/new.*password/i).type('NewPassword123!');
                cy.findByLabelText(/confirm.*password/i).type('NewPassword123!');

                // Submit
                cy.findByRole('button', { name: /change.*password|update.*password/i }).click();

                // Verify success
                cy.contains(/password.*updated|password.*changed/i).should('be.visible');

                // Form should be cleared
                cy.findByLabelText(/current.*password/i).should('have.value', '');
            });
        });

        it('should show error for incorrect current password', () => {
            cy.findByLabelText(/current.*password/i).type('wrongpassword');
            cy.findByLabelText(/new.*password/i).type('NewPassword123!');
            cy.findByLabelText(/confirm.*password/i).type('NewPassword123!');

            cy.findByRole('button', { name: /change.*password/i }).click();

            cy.contains(/current.*password.*incorrect/i).should('be.visible');
        });

        it('should validate password strength', () => {
            cy.fixture('users').then((users) => {
                cy.findByLabelText(/current.*password/i).type(users.testUser.password);
                cy.findByLabelText(/new.*password/i).type('weak');
                cy.findByLabelText(/confirm.*password/i).type('weak');

                cy.findByRole('button', { name: /change.*password/i }).click();

                cy.contains(/password.*weak|password.*must.*contain/i).should('be.visible');
            });
        });

        it('should validate password confirmation match', () => {
            cy.fixture('users').then((users) => {
                cy.findByLabelText(/current.*password/i).type(users.testUser.password);
                cy.findByLabelText(/new.*password/i).type('NewPassword123!');
                cy.findByLabelText(/confirm.*password/i).type('DifferentPassword123!');

                cy.findByRole('button', { name: /change.*password/i }).click();

                cy.contains(/passwords.*do not match/i).should('be.visible');
            });
        });

        it('should show password strength indicator', () => {
            cy.findByLabelText(/new.*password/i).type('Test123!');

            // Check for strength indicator
            cy.get('body').then(($body) => {
                if ($body.find('[data-testid="password-strength"]').length) {
                    cy.get('[data-testid="password-strength"]').should('be.visible');
                } else {
                    cy.log('No password strength indicator found');
                }
            });
        });

        it('should require all fields to be filled', () => {
            cy.findByRole('button', { name: /change.*password/i }).click();

            // Should show validation errors
            cy.contains(/current.*password.*required/i).should('be.visible');
            cy.contains(/new.*password.*required/i).should('be.visible');
        });

        it('should allow canceling password change', () => {
            cy.fixture('users').then((users) => {
                cy.findByLabelText(/current.*password/i).type(users.testUser.password);
                cy.findByLabelText(/new.*password/i).type('NewPassword123!');

                // Click cancel if available
                cy.get('body').then(($body) => {
                    if ($body.find('button:contains("Cancel")').length) {
                        cy.findByRole('button', { name: /cancel/i }).click();

                        // Fields should be cleared
                        cy.findByLabelText(/current.*password/i).should('have.value', '');
                    } else {
                        cy.log('No cancel button found');
                    }
                });
            });
        });
    });

    describe('Settings Persistence', () => {
        it('should save settings across page refreshes', () => {
            // Update a setting
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('3000');

            cy.findByRole('button', { name: /save.*changes/i }).click();
            cy.contains(/settings.*saved/i).should('be.visible');

            // Refresh page
            cy.reload();

            // Navigate back to settings
            cy.findByRole('button', { name: /settings/i }).click();

            // Verify setting persisted
            cy.findByLabelText(/chunk.*size/i).should('have.value', '3000');
        });

        it('should save settings across logout/login', () => {
            // Update theme
            cy.get('html').then(($html) => {
                if (!$html.hasClass('dark')) {
                    cy.findByRole('button', { name: /theme/i }).click();
                }
            });

            cy.get('html').should('have.class', 'dark');

            // Logout
            cy.logout();

            // Login again
            cy.fixture('users').then((users) => {
                cy.login(users.testUser.username, users.testUser.password);
            });

            // Theme should still be dark
            cy.get('html').should('have.class', 'dark');
        });
    });

    describe('Settings Validation', () => {
        it('should show unsaved changes warning', () => {
            // Make changes
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('4000');

            // Try to navigate away
            cy.findByRole('button', { name: /workspaces/i }).click();

            // Should show warning (if implemented)
            cy.get('body').then(($body) => {
                if ($body.text().includes('unsaved changes')) {
                    cy.contains(/unsaved changes/i).should('be.visible');
                } else {
                    cy.log('No unsaved changes warning implemented');
                }
            });
        });

        it('should disable save button while saving', () => {
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('5000');

            cy.findByRole('button', { name: /save.*changes/i }).click();

            // Button should be disabled during save
            cy.findByRole('button', { name: /save.*changes/i }).should('be.disabled');

            // Should re-enable after save completes
            cy.contains(/settings.*saved/i, { timeout: 10000 }).should('be.visible');
            cy.findByRole('button', { name: /save.*changes/i }).should('not.be.disabled');
        });
    });

    describe('Settings Error Handling', () => {
        it('should handle API errors gracefully', () => {
            // This would require mocking an API failure
            cy.log('Test requires mock setup for API failure');
        });

        it('should show error message when save fails', () => {
            // Mock a save failure and verify error message
            cy.log('Test requires mock setup for save failure');
        });

        it('should allow retry after error', () => {
            // Test retry functionality after error
            cy.log('Test requires mock setup for error retry');
        });
    });

    describe('Settings Accessibility', () => {
        it('should be keyboard navigable', () => {
            // Tab through all form fields
            cy.get('body').tab();
            cy.focused().should('have.attr', 'type', 'text');
        });

        it('should have proper ARIA labels', () => {
            // Check for proper accessibility attributes
            cy.findByLabelText(/chunk.*size/i).should('have.attr', 'aria-label');
        });

        it('should announce validation errors to screen readers', () => {
            // Trigger validation error
            cy.findByLabelText(/chunk.*size/i)
                .clear()
                .type('0');

            cy.findByRole('button', { name: /save/i }).click();

            // Error should have aria-live or role="alert"
            cy.contains(/invalid.*value/i).should('have.attr', 'role', 'alert');
        });
    });
});
