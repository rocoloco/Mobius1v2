/**
 * UI/UX Analysis - Detailed Screenshots for Design Review
 */

import { test, expect } from '@playwright/test';

test.describe('UI/UX Analysis - Demo Dashboard Review', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Disable animations for consistent screenshots
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `
    });
  });

  test('Full dashboard overview for UX analysis', async ({ page }) => {
    // Take full page screenshot for overall layout analysis
    await expect(page).toHaveScreenshot('dashboard-full-overview.png', {
      fullPage: true,
    });
  });

  test('Header and navigation analysis', async ({ page }) => {
    const header = page.locator('header, h1').first().locator('..');
    await expect(header).toHaveScreenshot('header-navigation-analysis.png');
  });

  test('Control panels section - UX issues', async ({ page }) => {
    const controlPanels = page.locator('text=Industrial Control Panels').locator('..').locator('..');
    await expect(controlPanels).toHaveScreenshot('control-panels-ux-analysis.png');
  });

  test('Button sections - Usability review', async ({ page }) => {
    // Enhanced buttons
    const enhancedButtons = page.locator('text=Enhanced with Physics').locator('..').locator('..');
    await expect(enhancedButtons).toHaveScreenshot('enhanced-buttons-usability.png');
    
    // Standard buttons
    const standardButtons = page.locator('text=Standard Industrial').locator('..').locator('..');
    await expect(standardButtons).toHaveScreenshot('standard-buttons-usability.png');
  });

  test('Form controls - Input usability', async ({ page }) => {
    const formControls = page.locator('text=Industrial Form Controls').locator('..').locator('..');
    await expect(formControls).toHaveScreenshot('form-controls-usability.png');
  });

  test('Status indicators - Information hierarchy', async ({ page }) => {
    const indicators = page.locator('text=Industrial Status Indicators').locator('..').locator('..');
    await expect(indicators).toHaveScreenshot('status-indicators-hierarchy.png');
  });

  test('Manufacturing hardware - Visual clutter analysis', async ({ page }) => {
    const hardware = page.locator('text=Manufacturing Hardware Details').locator('..').locator('..');
    await expect(hardware).toHaveScreenshot('hardware-visual-clutter.png');
  });

  test('Design foundation - Token presentation', async ({ page }) => {
    const foundation = page.locator('text=Design Foundation').locator('..').locator('..');
    await expect(foundation).toHaveScreenshot('foundation-token-presentation.png');
  });

  test('Mobile responsiveness issues', async ({ page }) => {
    // Test mobile portrait
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('mobile-ux-issues.png', { fullPage: true });
    
    // Test tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('tablet-ux-issues.png', { fullPage: true });
  });

  test('Interactive elements - Accessibility concerns', async ({ page }) => {
    // Highlight all interactive elements
    await page.addStyleTag({
      content: `
        button, input, [role="button"], [tabindex="0"] {
          outline: 3px solid red !important;
          outline-offset: 2px !important;
        }
        button:hover, input:hover {
          outline-color: orange !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('interactive-elements-accessibility.png', {
      fullPage: true,
    });
  });

  test('Typography and spacing issues', async ({ page }) => {
    // Add visual guides for typography analysis
    await page.addStyleTag({
      content: `
        h1, h2, h3 { 
          background: rgba(255, 0, 0, 0.1) !important;
          outline: 1px solid red !important;
        }
        p, span, label { 
          background: rgba(0, 255, 0, 0.1) !important;
          outline: 1px solid green !important;
        }
        .space-y-2, .space-y-4, .space-y-6, .space-y-8 {
          background: rgba(0, 0, 255, 0.05) !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('typography-spacing-analysis.png', {
      fullPage: true,
    });
  });

});