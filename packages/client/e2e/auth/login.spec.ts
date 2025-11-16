import { test, expect } from '@playwright/test';

test.describe('User Login Flow', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
    });

    test('should successfully log in an existing user', async ({ page }) => {
        // Fill in login form
        await page.fill('input[name="username"]', 'testuser');
        await page.fill('input[name="password"]', 'password123');

        // Submit form
        await page.click('button[type="submit"]:has-text("Sign in")');

        // Verify redirect to chat page
        await expect(page).toHaveURL('/chat');

        // Verify user menu is visible
        await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });

    test('should show error for invalid credentials', async ({ page }) => {
        await page.fill('input[name="username"]', 'wronguser');
        await page.fill('input[name="password"]', 'wrongpassword');

        await page.click('button[type="submit"]:has-text("Sign in")');

        // Verify error message
        await expect(page.locator('text=/.*invalid.*/i')).toBeVisible();

        // Verify we're still on login page
        await expect(page).toHaveURL('/');
    });

    test('should show validation error for empty fields', async ({ page }) => {
        await page.click('button[type="submit"]:has-text("Sign in")');

        // Verify HTML5 validation or custom error messages
        const usernameInput = page.locator('input[name="username"]');
        await expect(usernameInput).toBeFocused();
    });

    test('should persist session after page reload', async ({ page }) => {
        // Log in
        await page.fill('input[name="username"]', 'testuser');
        await page.fill('input[name="password"]', 'password123');
        await page.click('button[type="submit"]:has-text("Sign in")');

        await expect(page).toHaveURL('/chat');

        // Reload page
        await page.reload();

        // Verify user is still logged in
        await expect(page).toHaveURL('/chat');
        await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });

    test('should navigate to signup page from login', async ({ page }) => {
        await page.click('text=Sign up');

        // Verify we're on signup page
        await expect(page.locator('h1:has-text("Sign up")')).toBeVisible();
    });
});
