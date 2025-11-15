import { test, expect } from '@playwright/test';

test.describe('New Chat Conversation', () => {
    test.beforeEach(async ({ page }) => {
        // Log in before each test
        await page.goto('/');
        await page.fill('input[name="username"]', 'testuser');
        await page.fill('input[name="password"]', 'password123');
        await page.click('button[type="submit"]:has-text("Sign in")');
        await expect(page).toHaveURL('/chat');
    });

    test('should send a message and receive a response', async ({ page }) => {
        // Type a message
        const messageText = 'Hello, how are you?';
        await page.fill('textarea[placeholder*="Ask"]', messageText);

        // Send message
        await page.click('button[type="submit"]');

        // Verify user message appears
        await expect(page.locator(`text=${messageText}`)).toBeVisible();

        // Verify typing indicator appears
        await expect(page.locator('[data-testid="typing-indicator"]')).toBeVisible({
            timeout: 2000,
        });

        // Wait for bot response (with longer timeout for API)
        await expect(page.locator('.bg-gray-100').first()).toBeVisible({
            timeout: 30000,
        });

        // Verify typing indicator disappears
        await expect(page.locator('[data-testid="typing-indicator"]')).not.toBeVisible();
    });

    test('should create a new chat session', async ({ page }) => {
        // Click "New Chat" button
        await page.click('button:has-text("New Chat")');

        // Verify new session is created
        await expect(page.locator('text=New Chat')).toBeVisible();

        // Verify chat input is focused
        await expect(page.locator('textarea[placeholder*="Ask"]')).toBeFocused();
    });

    test('should handle long messages', async ({ page }) => {
        const longMessage = 'This is a very long message. '.repeat(50);
        await page.fill('textarea[placeholder*="Ask"]', longMessage);
        await page.click('button[type="submit"]');

        // Verify message appears (truncated or scrollable)
        await expect(page.locator('text=/This is a very long message/')).toBeVisible();
    });

    test('should display error on API failure', async ({ page }) => {
        // Mock API failure by intercepting the request
        await page.route('**/api/chat/send', (route) => {
            route.abort();
        });

        await page.fill('textarea[placeholder*="Ask"]', 'Test message');
        await page.click('button[type="submit"]');

        // Verify error message appears
        await expect(page.locator('text=/error|failed/i')).toBeVisible({
            timeout: 10000,
        });
    });

    test('should preserve message history on session switch', async ({ page }) => {
        // Send a message in first session
        const firstMessage = 'Message in first session';
        await page.fill('textarea[placeholder*="Ask"]', firstMessage);
        await page.click('button[type="submit"]');
        await expect(page.locator(`text=${firstMessage}`)).toBeVisible();

        // Create new session
        await page.click('button:has-text("New Chat")');

        // Send message in second session
        const secondMessage = 'Message in second session';
        await page.fill('textarea[placeholder*="Ask"]', secondMessage);
        await page.click('button[type="submit"]');
        await expect(page.locator(`text=${secondMessage}`)).toBeVisible();

        // Switch back to first session
        const sessionList = page.locator('[data-testid="session-list"] > div').first();
        await sessionList.click();

        // Verify first message is still visible
        await expect(page.locator(`text=${firstMessage}`)).toBeVisible();
        await expect(page.locator(`text=${secondMessage}`)).not.toBeVisible();
    });
});
