import { defineConfig, devices } from '@playwright/test';

// E2E config. By default Playwright boots the Vite dev server, which proxies API
// calls to a running backend (http://localhost:8000). Start the backend (or the
// full docker-compose stack) before running `npm run test:e2e`.
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
