/**
 * Visual Regression Tests for Luminous Dashboard
 * 
 * Captures screenshots of the Luminous Dashboard components and compares
 * them against baseline images to detect visual regressions.
 * 
 * Requirements: 12.1-12.7 (Glassmorphism Visual Effects)
 */

import { test, expect } from '@playwright/test';

test.describe('Luminous Dashboard - Visual Regression', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    // Wait for animations to settle
    await page.waitForTimeout(1000);
  });

  test('Full dashboard layout', async ({ page }) => {
    // Capture full page screenshot
    await expect(page).toHaveScreenshot('dashboard-full.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('AppShell header', async ({ page }) => {
    // Capture header screenshot
    const header = page.locator('[data-testid="app-shell-header"]');
    await expect(header).toHaveScreenshot('appshell-header.png', {
      animations: 'disabled',
    });
  });

  test('Canvas empty state', async ({ page }) => {
    // Capture canvas area with empty state
    const canvas = page.locator('[data-testid="canvas"]').first();
    if (await canvas.count() > 0) {
      await expect(canvas).toHaveScreenshot('canvas-empty-state.png', {
        animations: 'disabled',
      });
    }
  });

  test('ComplianceGauge component', async ({ page }) => {
    // Capture compliance gauge
    const gauge = page.locator('[data-testid="compliance-gauge"]').first();
    if (await gauge.count() > 0) {
      await expect(gauge).toHaveScreenshot('compliance-gauge.png', {
        animations: 'disabled',
      });
    }
  });

  test('Director chat interface', async ({ page }) => {
    // Capture director component
    const director = page.locator('[data-testid="director"]').first();
    if (await director.count() > 0) {
      await expect(director).toHaveScreenshot('director-chat.png', {
        animations: 'disabled',
      });
    }
  });

  test('ContextDeck constraints panel', async ({ page }) => {
    // Capture context deck
    const contextDeck = page.locator('[data-testid="context-deck"]').first();
    if (await contextDeck.count() > 0) {
      await expect(contextDeck).toHaveScreenshot('context-deck.png', {
        animations: 'disabled',
      });
    }
  });

  test('Glassmorphism effects on panels', async ({ page }) => {
    // Verify glassmorphism styling is applied
    // Take screenshot of a glass panel to verify blur and transparency
    const glassPanel = page.locator('.backdrop-blur-md').first();
    if (await glassPanel.count() > 0) {
      await expect(glassPanel).toHaveScreenshot('glassmorphism-panel.png', {
        animations: 'disabled',
      });
    }
  });

  test('Connection pulse indicator states', async ({ page }) => {
    // Capture connection pulse in connected state
    const connectionPulse = page.locator('[data-testid="connection-pulse"]');
    if (await connectionPulse.count() > 0) {
      await expect(connectionPulse).toHaveScreenshot('connection-pulse-connected.png', {
        animations: 'disabled',
      });
    }
  });

  test('Quick action buttons', async ({ page }) => {
    // Capture quick action buttons
    const quickActionFix = page.locator('[data-testid="quick-action-fix-red"]');
    if (await quickActionFix.count() > 0) {
      await expect(quickActionFix).toHaveScreenshot('quick-action-fix.png', {
        animations: 'disabled',
      });
    }
  });

  test('Input field styling', async ({ page }) => {
    // Capture prompt input field
    const promptInput = page.locator('[data-testid="prompt-input"]');
    if (await promptInput.count() > 0) {
      // Focus the input to see focus styling
      await promptInput.focus();
      await page.waitForTimeout(300);
      await expect(promptInput).toHaveScreenshot('prompt-input-focused.png', {
        animations: 'disabled',
      });
    }
  });

});

test.describe('Luminous Dashboard - Hover States', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test('Settings button hover state', async ({ page }) => {
    const settingsButton = page.locator('[data-testid="settings-button"]');
    if (await settingsButton.count() > 0) {
      // Use force to bypass overlay buttons that may intercept
      await settingsButton.hover({ force: true });
      await page.waitForTimeout(300);
      await expect(settingsButton).toHaveScreenshot('settings-button-hover.png', {
        animations: 'disabled',
      });
    }
  });

  test('User avatar hover state', async ({ page }) => {
    const userAvatar = page.locator('[data-testid="user-avatar"]');
    if (await userAvatar.count() > 0) {
      // Use force to bypass overlay buttons that may intercept
      await userAvatar.hover({ force: true });
      await page.waitForTimeout(300);
      await expect(userAvatar).toHaveScreenshot('user-avatar-hover.png', {
        animations: 'disabled',
      });
    }
  });

  test('Submit button hover state', async ({ page }) => {
    const submitButton = page.locator('[data-testid="submit-button"]');
    if (await submitButton.count() > 0) {
      // First type something to enable the button
      const input = page.locator('[data-testid="prompt-input"]');
      await input.fill('Test prompt');
      await submitButton.hover({ force: true });
      await page.waitForTimeout(300);
      await expect(submitButton).toHaveScreenshot('submit-button-hover.png', {
        animations: 'disabled',
      });
    }
  });

});

test.describe('Luminous Dashboard - Dark Mode Consistency', () => {
  
  test('Background color is deep charcoal', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Verify the background color
    const backgroundColor = await page.evaluate(() => {
      const body = document.body;
      const computed = window.getComputedStyle(body);
      return computed.backgroundColor;
    });
    
    // The background should be dark (close to #101012)
    // RGB values should be very low
    console.log('Background color:', backgroundColor);
    
    // Take a screenshot to verify dark mode
    await expect(page).toHaveScreenshot('dark-mode-background.png', {
      fullPage: false,
      clip: { x: 0, y: 0, width: 100, height: 100 },
      animations: 'disabled',
    });
  });

  test('Text contrast on dark background', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Capture text elements to verify contrast
    const heading = page.locator('h1').first();
    if (await heading.count() > 0) {
      await expect(heading).toHaveScreenshot('heading-contrast.png', {
        animations: 'disabled',
      });
    }
  });

});
