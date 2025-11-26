describe('Authentication', () => {
    beforeEach(() => {
        cy.clearLocalStorage();
        cy.visit('/');
    });

    describe('User Login', () => {
        it('should successfully log in with valid credentials', () => {
            cy.fixture('users').then((users) => {
                cy.login(users.testUser.username, users.testUser.password);

                // Verify we're on the main page
                cy.url().should('match', /\/$|\/workspaces/);

                // Verify users menu is visible
                cy.findByText(users.testUser.username).should('be.visible');
            });
        });

        it('should show error with invalid credentials', () => {
            cy.visit('/login');
            cy.findByLabelText(/username/i).type('invaliduser');
            cy.findByLabelText(/password/i).type('wrongpassword');
            cy.findByRole('button', { name: /login|sign in/i }).click();

            // Should stay on login page
            cy.url().should('include', '/login');

            // Should show error message
            cy.contains(/invalid.*credentials|login.*failed/i).should('be.visible');
        });

        it('should show validation errors for empty fields', () => {
            cy.visit('/login');
            cy.findByRole('button', { name: /login|sign in/i }).click();

            // Should show validation errors
            cy.contains(/username.*required|username.*cannot be empty/i).should('be.visible');
            cy.contains(/password.*required|password.*cannot be empty/i).should('be.visible');
        });

        it('should redirect to main page if already logged in', () => {
            cy.fixture('users').then((users) => {
                cy.login(users.testUser.username, users.testUser.password);
                cy.visit('/login');

                // Should redirect to main page
                cy.url().should('match', /\/$|\/workspaces/);
            });
        });
    });

    describe('User Signup', () => {
        it('should successfully sign up with valid data', () => {
            const timestamp = Date.now();
            const newUser = {
                username: `testuser${timestamp}`,
                email: `testuser${timestamp}@example.com`,
                password: 'TestPassword123!',
                fullName: 'Test User',
            };

            cy.signup(newUser.username, newUser.email, newUser.password, newUser.fullName);

            // Verify we're on the main page
            cy.url().should('match', /\/$|\/workspaces/);

            // Verify users menu is visible
            cy.findByText(newUser.username).should('be.visible');
        });

        it('should show error when username already exists', () => {
            cy.fixture('users').then((users) => {
                cy.visit('/signup');
                cy.findByLabelText(/username/i).type(users.testUser.username);
                cy.findByLabelText(/email/i).type('newemail@example.com');
                cy.findByLabelText(/^password/i).type(users.testUser.password);
                cy.findByRole('button', { name: /sign up|create account/i }).click();

                // Should show error message
                cy.contains(/username.*exists|username.*taken/i).should('be.visible');
            });
        });

        it('should show error when email already exists', () => {
            cy.fixture('users').then((users) => {
                cy.visit('/signup');
                cy.findByLabelText(/username/i).type('newusername');
                cy.findByLabelText(/email/i).type(users.testUser.email);
                cy.findByLabelText(/^password/i).type(users.testUser.password);
                cy.findByRole('button', { name: /sign up|create account/i }).click();

                // Should show error message
                cy.contains(/email.*exists|email.*already.*use/i).should('be.visible');
            });
        });

        it('should validate password strength', () => {
            cy.visit('/signup');
            cy.findByLabelText(/username/i).type('testuser');
            cy.findByLabelText(/email/i).type('test@example.com');
            cy.findByLabelText(/^password/i).type('weak');
            cy.findByRole('button', { name: /sign up|create account/i }).click();

            // Should show password strength error
            cy.contains(/password.*weak|password.*must.*contain|password.*least.*8/i).should(
                'be.visible'
            );
        });
    });

    describe('User Logout', () => {
        beforeEach(() => {
            cy.fixture('users').then((users) => {
                cy.login(users.testUser.username, users.testUser.password);
            });
        });

        it('should successfully log out', () => {
            cy.logout();

            // Verify we're on the login page
            cy.url().should('include', '/login');

            // Verify token is removed
            cy.window().then((win) => {
                void expect(win.localStorage.getItem('token')).to.be.null;
            });
        });

        it('should require login to access protected routes after logout', () => {
            cy.logout();

            // Try to access a protected route
            cy.visit('/workspaces');

            // Should redirect to login
            cy.url().should('include', '/login');
        });
    });

    describe('Get Current User Profile', () => {
        beforeEach(() => {
            cy.fixture('users').then((users) => {
                cy.login(users.testUser.username, users.testUser.password);
            });
        });

        it('should display users profile information', () => {
            cy.fixture('users').then((users) => {
                // Navigate to settings/profile page
                cy.findByRole('button', { name: /settings|profile/i }).click();

                // Verify users information is displayed
                cy.findByText(users.testUser.username).should('be.visible');
                cy.findByText(users.testUser.email).should('be.visible');
            });
        });

        it('should apply users theme preference', () => {
            // Check if theme is applied
            cy.get('html').should('have.class', /dark|light/);
        });
    });

    describe('Update User Profile', () => {
        beforeEach(() => {
            cy.fixture('users').then((users) => {
                cy.login(users.testUser.username, users.testUser.password);
            });
        });

        it('should successfully update profile information', () => {
            // Navigate to settings page
            cy.findByRole('button', { name: /settings|profile/i }).click();

            // Click edit profile
            cy.findByRole('button', { name: /edit.*profile/i }).click();

            // Update full name
            const newFullName = 'Updated Name';
            cy.findByLabelText(/full.*name/i)
                .clear()
                .type(newFullName);

            // Save changes
            cy.findByRole('button', { name: /save/i }).click();

            // Verify success message
            cy.contains(/profile.*updated|changes.*saved/i).should('be.visible');

            // Verify name is updated in the UI
            cy.findByText(newFullName).should('be.visible');
        });

        it('should show error for invalid email format', () => {
            cy.findByRole('button', { name: /settings|profile/i }).click();
            cy.findByRole('button', { name: /edit.*profile/i }).click();

            cy.findByLabelText(/email/i).clear().type('invalid-email');

            cy.findByRole('button', { name: /save/i }).click();

            // Should show validation error
            cy.contains(/invalid.*email|email.*format/i).should('be.visible');
        });
    });

    describe('Update User Preferences', () => {
        beforeEach(() => {
            cy.fixture('users').then((users) => {
                cy.login(users.testUser.username, users.testUser.password);
            });
        });

        it('should toggle theme preference', () => {
            // Get current theme
            cy.get('html').then(($html) => {
                const currentTheme = $html.hasClass('dark') ? 'dark' : 'light';
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

                // Click theme toggle
                cy.findByRole('button', { name: /theme|dark.*mode|light.*mode/i }).click();

                // Verify theme changed
                cy.get('html').should('have.class', newTheme);
            });
        });
    });

    describe('Change User Password', () => {
        beforeEach(() => {
            cy.fixture('users').then((users) => {
                cy.login(users.testUser.username, users.testUser.password);
            });
        });

        it('should successfully change password', () => {
            cy.fixture('users').then((users) => {
                // Navigate to settings page
                cy.findByRole('button', { name: /settings|profile/i }).click();

                // Find password change section
                cy.findByLabelText(/current.*password/i).type(users.testUser.password);
                cy.findByLabelText(/new.*password/i).type('NewPassword123!');
                cy.findByLabelText(/confirm.*password/i).type('NewPassword123!');

                // Submit password change
                cy.findByRole('button', { name: /change.*password|update.*password/i }).click();

                // Verify success message
                cy.contains(/password.*updated|password.*changed/i).should('be.visible');
            });
        });

        it('should show error for incorrect current password', () => {
            // Navigate to settings page
            cy.findByRole('button', { name: /settings|profile/i }).click();

            cy.findByLabelText(/current.*password/i).type('wrongpassword');
            cy.findByLabelText(/new.*password/i).type('NewPassword123!');
            cy.findByLabelText(/confirm.*password/i).type('NewPassword123!');

            cy.findByRole('button', { name: /change.*password|update.*password/i }).click();

            // Should show error
            cy.contains(/current.*password.*incorrect|password.*invalid/i).should('be.visible');
        });

        it('should show error when passwords do not match', () => {
            cy.fixture('users').then((users) => {
                cy.findByRole('button', { name: /settings|profile/i }).click();

                cy.findByLabelText(/current.*password/i).type(users.testUser.password);
                cy.findByLabelText(/new.*password/i).type('NewPassword123!');
                cy.findByLabelText(/confirm.*password/i).type('DifferentPassword123!');

                cy.findByRole('button', { name: /change.*password|update.*password/i }).click();

                // Should show validation error
                cy.contains(/passwords.*do not match|passwords.*must.*match/i).should('be.visible');
            });
        });
    });
});
