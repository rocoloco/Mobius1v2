import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for Industrial Design System Visual Testing
 */
export default defineConfig({
  testDir: './tests',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/visual-test-results.json' }]
  ],
  
  /* Shared settings for all the projects below. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:5174',
    
    /* Collect trace when retrying the failed test. */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Record video on failure */
    video: 'retain-on-failure',
  },

  /* Configure projects for major browsers */
  projects: [
    // Integration tests - run on Chromium only for speed
    {
      name: 'integration',
      testDir: './tests/integration',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
    },
    
    // Visual tests - run on multiple browsers
    {
      name: 'visual-chromium',
      testDir: './tests/visual',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
    },
    
    {
      name: 'visual-firefox',
      testDir: './tests/visual',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1280, height: 720 },
      },
    },
    
    {
      name: 'visual-webkit',
      testDir: './tests/visual',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1280, height: 720 },
      },
    },

    /* Test against mobile viewports for visual tests */
    {
      name: 'visual-mobile-chrome',
      testDir: './tests/visual',
      use: { 
        ...devices['Pixel 5'],
      },
    },
    
    {
      name: 'visual-mobile-safari',
      testDir: './tests/visual',
      use: { 
        ...devices['iPhone 12'],
      },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5174',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000, // 2 minutes
  },
  
  /* Global test timeout */
  timeout: 30 * 1000,
  
  /* Expect timeout for assertions */
  expect: {
    /* Timeout for expect() calls */
    timeout: 10 * 1000,
    
    /* Threshold for visual comparisons */
    toHaveScreenshot: { 
      threshold: 0.2,
      mode: 'pixel',
      animations: 'disabled', // Disable animations for consistent screenshots
    },
    
    toMatchSnapshot: { 
      threshold: 0.2,
      mode: 'pixel',
    },
  },
});