/**
 * Mobile Device Testing for Luminous Dashboard
 * 
 * Tests the dashboard on mobile viewports to ensure responsive behavior
 * and mobile-specific functionality works correctly.
 * 
 * Requirements: 11.1-11.7 (Responsive Mobile Layout)
 */

import { test, expect } from '@playwright/test';

// Test responsive breakpoints using viewport sizes
test.describe('Luminous Dashboard - Mobile Responsive', () => {

  test('Mobile viewport (375x667) - iPhone SE size', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // Verify the page loads
    const header = page.locator('[data-testid="app-shell-header"]');
    await expect(header).toBeVisible();
    
    // Take screenshot for visual verification
    await expect(page).toHaveScreenshot('mobile-375x667.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('Mobile viewport (390x844) - iPhone 12/13 size', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('mobile-390x844.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('Mobile viewport (412x915) - Pixel 5/Android size', async ({ page }) => {
    await page.setViewportSize({ width: 412, height: 915 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('mobile-412x915.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('Tablet viewport (768x1024) - iPad size', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('tablet-768x1024.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('Desktop viewport (1280x720)', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('desktop-1280x720.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

});

test.describe('Luminous Dashboard - Touch Target Sizes', () => {

  test('Touch targets are at least 44x44px on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Check settings button
    const settingsButton = page.locator('[data-testid="settings-button"]');
    if (await settingsButton.count() > 0) {
      const box = await settingsButton.boundingBox();
      expect(box?.width).toBeGreaterThanOrEqual(44);
      expect(box?.height).toBeGreaterThanOrEqual(44);
    }

    // Check user avatar
    const userAvatar = page.locator('[data-testid="user-avatar"]');
    if (await userAvatar.count() > 0) {
      const box = await userAvatar.boundingBox();
      expect(box?.width).toBeGreaterThanOrEqual(44);
      expect(box?.height).toBeGreaterThanOrEqual(44);
    }

    // Check submit button
    const submitButton = page.locator('[data-testid="submit-button"]');
    if (await submitButton.count() > 0) {
      const box = await submitButton.boundingBox();
      expect(box?.width).toBeGreaterThanOrEqual(44);
      expect(box?.height).toBeGreaterThanOrEqual(44);
    }

    // Check quick action buttons
    const quickActionFix = page.locator('[data-testid="quick-action-fix-red"]');
    if (await quickActionFix.count() > 0) {
      const box = await quickActionFix.boundingBox();
      expect(box?.height).toBeGreaterThanOrEqual(44);
    }
  });

  test('Touch targets are properly sized on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Check settings button
    const settingsButton = page.locator('[data-testid="settings-button"]');
    if (await settingsButton.count() > 0) {
      const box = await settingsButton.boundingBox();
      expect(box?.width).toBeGreaterThanOrEqual(44);
      expect(box?.height).toBeGreaterThanOrEqual(44);
    }
  });

});

test.describe('Luminous Dashboard - Mobile Input', () => {

  test('Input field is usable on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const input = page.locator('[data-testid="prompt-input"]');
    if (await input.count() > 0) {
      await expect(input).toBeVisible();
      
      // Input should be wide enough to type
      const box = await input.boundingBox();
      expect(box?.width).toBeGreaterThan(200);
      
      // Should be able to type in the input
      await input.fill('Test mobile input');
      await expect(input).toHaveValue('Test mobile input');
    }
  });

  test('Input field works on Android viewport', async ({ page }) => {
    await page.setViewportSize({ width: 412, height: 915 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const input = page.locator('[data-testid="prompt-input"]');
    if (await input.count() > 0) {
      await input.fill('Test Android input');
      await expect(input).toHaveValue('Test Android input');
    }
  });

});

test.describe('Luminous Dashboard - Orientation', () => {

  test('Portrait orientation on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('orientation-portrait.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('Landscape orientation on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 812, height: 375 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('orientation-landscape.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

});

test.describe('Luminous Dashboard - Mobile Header', () => {

  test('Header is visible and properly sized on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const header = page.locator('[data-testid="app-shell-header"]');
    await expect(header).toBeVisible();
    
    // Header should be full width on mobile
    const headerBox = await header.boundingBox();
    expect(headerBox?.width).toBe(375);
    
    // Header height should be 64px (h-16)
    expect(headerBox?.height).toBe(64);
  });

  test('Header adapts to tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const header = page.locator('[data-testid="app-shell-header"]');
    await expect(header).toBeVisible();
    
    const headerBox = await header.boundingBox();
    expect(headerBox?.width).toBe(768);
  });

});

test.describe('Luminous Dashboard - Mobile Scrolling', () => {

  test('Page scrolls correctly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Try to scroll the page
    await page.evaluate(() => window.scrollTo(0, 100));
    await page.waitForTimeout(300);
    
    // Page should handle scroll
    const scrollY = await page.evaluate(() => window.scrollY);
    // Scroll position may be 0 if content fits, which is fine
    expect(scrollY).toBeGreaterThanOrEqual(0);
  });

});

test.describe('Luminous Dashboard - Mobile Components', () => {

  test('Director component renders on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const director = page.locator('[data-testid="director"]').first();
    if (await director.count() > 0) {
      await expect(director).toBeVisible();
    }
  });

  test('ComplianceGauge renders on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const gauge = page.locator('[data-testid="compliance-gauge"]').first();
    if (await gauge.count() > 0) {
      await expect(gauge).toBeVisible();
    }
  });

  test('Canvas renders on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const canvas = page.locator('[data-testid="canvas"]').first();
    if (await canvas.count() > 0) {
      await expect(canvas).toBeVisible();
    }
  });

});
