import { test, expect } from '@playwright/test';

test.describe('User Signup Flow', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
    });

    test('should successfully sign up a new user', async ({ page }) => {
        // Navigate to signup page
        await page.click('text=Sign up');

        // Fill in signup form
        const timestamp = Date.now();
        await page.fill('input[name="username"]', `testuser${timestamp}`);
        await page.fill('input[name="email"]', `testuser${timestamp}@example.com`);
        await page.fill('input[name="fullName"]', 'Test User');
        await page.fill('input[name="password"]', 'SecurePassword123!');
        await page.fill('input[name="confirmPassword"]', 'SecurePassword123!');

        // Submit form
        await page.click('button[type="submit"]:has-text("Sign up")');

        // Verify redirect to chat page
        await expect(page).toHaveURL('/chat');

        // Verify user menu shows username
        await expect(page.locator(`text=${testuser${timestamp}}`)).toBeVisible();
    });

    test('should show validation error for mismatched passwords', async ({ page }) => {
        await page.click('text=Sign up');

        await page.fill('input[name="username"]', 'testuser');
        await page.fill('input[name="email"]', 'testuser@example.com');
        await page.fill('input[name="password"]', 'Password123!');
        await page.fill('input[name="confirmPassword"]', 'DifferentPassword123!');

        await page.click('button[type="submit"]:has-text("Sign up")');

        // Verify error message
        await expect(page.locator('text=Passwords do not match')).toBeVisible();
    });

    test('should show validation error for invalid email', async ({ page }) => {
        await page.click('text=Sign up');

        await page.fill('input[name="username"]', 'testuser');
        await page.fill('input[name="email"]', 'invalid-email');
        await page.fill('input[name="password"]', 'Password123!');
        await page.fill('input[name="confirmPassword"]', 'Password123!');

        await page.click('button[type="submit"]:has-text("Sign up")');

        // Verify error message
        await expect(page.locator('text=/.*email.*/i')).toBeVisible();
    });

    test('should navigate to login page from signup', async ({ page }) => {
        await page.click('text=Sign up');

        // Click "Already have an account?" link
        await page.click('text=Already have an account?');

        // Verify we're on login page
        await expect(page.locator('h1:has-text("Sign in")')).toBeVisible();
    });
});
