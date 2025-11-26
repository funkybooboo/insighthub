import { defineConfig } from 'cypress';

export default defineConfig({
    e2e: {
        baseUrl: 'http://localhost:5173',
        viewportWidth: 1280,
        viewportHeight: 720,
        video: true,
        videosFolder: 'cypress/videos',
        screenshotsFolder: 'cypress/screenshots',
        screenshotOnRunFailure: true,
        // Increased timeouts for Vector RAG pipeline (embedding, indexing can take time)
        defaultCommandTimeout: 15000,
        requestTimeout: 30000,
        responseTimeout: 30000,
        pageLoadTimeout: 60000,
        execTimeout: 120000,
        taskTimeout: 120000,
        setupNodeEvents(_on, _config) {
            // implement node event listeners here
        },
        specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
        supportFile: 'cypress/support/e2e.ts',
        experimentalStudio: true,
        experimentalWebKitSupport: false,
        watchForFileChanges: true,
    },
    env: {
        // API configuration
        apiUrl: 'http://localhost:8000/api',

        // Test users credentials
        testUsername: 'testuser',
        testPassword: 'TestPassword123!',
        testEmail: 'testuser@example.com',

        // Vector RAG pipeline timeouts (in milliseconds)
        documentUploadTimeout: 30000,      // 30 seconds for upload
        documentParsingTimeout: 60000,     // 1 minute for parsing
        documentChunkingTimeout: 60000,    // 1 minute for chunking
        documentEmbeddingTimeout: 120000,  // 2 minutes for embedding generation
        documentIndexingTimeout: 120000,   // 2 minutes for vector indexing
        documentReadyTimeout: 300000,      // 5 minutes total pipeline timeout

        // Chat and query timeouts
        chatResponseTimeout: 120000,       // 2 minutes for LLM response
        contextRetrievalTimeout: 30000,    // 30 seconds for vector search

        // Workspace provisioning
        workspaceProvisioningTimeout: 120000, // 2 minutes for workspace setup
    },
    retries: {
        runMode: 2,      // Retry failed tests twice in CI
        openMode: 0,     // No retries in interactive mode
    },
    // Reporter configuration for CI/CD
    reporter: 'cypress-multi-reporters',
    reporterOptions: {
        reporterEnabled: 'spec, json',
        jsonReporterOptions: {
            toConsole: false,
            output: 'cypress/results/test-results.json',
        },
    },
});
