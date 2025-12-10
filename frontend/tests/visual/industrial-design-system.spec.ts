/**
 * Industrial Design System - Visual Regression Tests
 * 
 * Comprehensive visual testing for all industrial components
 */

import { test, expect } from '@playwright/test';

test.describe('Industrial Design System - Visual Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the demo page
    await page.goto('/');
    
    // Wait for the page to be fully loaded
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

  test('Full page screenshot - Industrial Design System Demo', async ({ page }) => {
    // Take a full page screenshot
    await expect(page).toHaveScreenshot('industrial-design-system-full-page.png', {
      fullPage: true,
    });
  });

  test('Header section with title and badges', async ({ page }) => {
    const header = page.locator('h1').first();
    await expect(header).toHaveScreenshot('header-section.png');
  });

  test('Industrial Control Panels section', async ({ page }) => {
    const controlPanels = page.locator('section').first();
    await expect(controlPanels).toHaveScreenshot('control-panels-section.png');
  });

  test('Individual Industrial Cards', async ({ page }) => {
    // System Status Card
    const systemCard = page.locator('[data-testid="system-status-card"]').first();
    if (await systemCard.count() > 0) {
      await expect(systemCard).toHaveScreenshot('system-status-card.png');
    }

    // Manufacturing Unit Card
    const manufacturingCard = page.locator('text=Manufacturing Unit').locator('..').locator('..');
    await expect(manufacturingCard).toHaveScreenshot('manufacturing-unit-card.png');

    // Data Terminal Card
    const dataCard = page.locator('text=Data Terminal').locator('..').locator('..');
    await expect(dataCard).toHaveScreenshot('data-terminal-card.png');
  });

  test('Enhanced Industrial Buttons', async ({ page }) => {
    const enhancedButtonsSection = page.locator('text=Enhanced with Physics').locator('..').locator('..');
    await expect(enhancedButtonsSection).toHaveScreenshot('enhanced-buttons-section.png');
  });

  test('Standard Industrial Buttons', async ({ page }) => {
    const standardButtonsSection = page.locator('text=Standard Industrial').locator('..').locator('..');
    await expect(standardButtonsSection).toHaveScreenshot('standard-buttons-section.png');
  });

  test('Form Controls section', async ({ page }) => {
    const formSection = page.locator('text=Industrial Form Controls').locator('..').locator('..');
    await expect(formSection).toHaveScreenshot('form-controls-section.png');
  });

  test('Status Indicators section', async ({ page }) => {
    const indicatorsSection = page.locator('text=Industrial Status Indicators').locator('..').locator('..');
    await expect(indicatorsSection).toHaveScreenshot('status-indicators-section.png');
  });

  test('Manufacturing Hardware section', async ({ page }) => {
    const hardwareSection = page.locator('text=Manufacturing Hardware Details').locator('..').locator('..');
    await expect(hardwareSection).toHaveScreenshot('manufacturing-hardware-section.png');
  });

  test('Industrial Bolts showcase', async ({ page }) => {
    const boltsSection = page.locator('text=Industrial Fasteners').locator('..').locator('..');
    await expect(boltsSection).toHaveScreenshot('industrial-bolts-showcase.png');
  });

  test('Connector Ports showcase', async ({ page }) => {
    const portsSection = page.locator('text=Connector Ports').locator('..').locator('..');
    await expect(portsSection).toHaveScreenshot('connector-ports-showcase.png');
  });

  test('Surface Textures section', async ({ page }) => {
    const texturesSection = page.locator('text=Industrial Surface Textures').locator('..').locator('..');
    await expect(texturesSection).toHaveScreenshot('surface-textures-section.png');
  });

  test('Ventilation Systems section', async ({ page }) => {
    const ventilationSection = page.locator('text=Ventilation & Cooling').locator('..').locator('..');
    await expect(ventilationSection).toHaveScreenshot('ventilation-systems-section.png');
  });

  test('Design Foundation section', async ({ page }) => {
    const foundationSection = page.locator('text=Design Foundation').locator('..').locator('..');
    await expect(foundationSection).toHaveScreenshot('design-foundation-section.png');
  });

  test('Color Palette showcase', async ({ page }) => {
    const colorSection = page.locator('text=Color Palette').locator('..').locator('..');
    await expect(colorSection).toHaveScreenshot('color-palette-showcase.png');
  });

  test('Neumorphic Shadows showcase', async ({ page }) => {
    const shadowsSection = page.locator('text=Neumorphic Shadows').locator('..').locator('..');
    await expect(shadowsSection).toHaveScreenshot('neumorphic-shadows-showcase.png');
  });

});

test.describe('Industrial Components - Interactive States', () => {
  
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

  test('Button hover states', async ({ page }) => {
    const primaryButton = page.locator('text=Primary Control').first();
    
    // Default state
    await expect(primaryButton).toHaveScreenshot('button-default-state.png');
    
    // Hover state
    await primaryButton.hover();
    await expect(primaryButton).toHaveScreenshot('button-hover-state.png');
  });

  test('Button pressed states', async ({ page }) => {
    const emergencyButton = page.locator('text=EMERGENCY STOP').first();
    
    // Default state
    await expect(emergencyButton).toHaveScreenshot('emergency-button-default.png');
    
    // Pressed state (simulate mousedown)
    await emergencyButton.dispatchEvent('mousedown');
    await expect(emergencyButton).toHaveScreenshot('emergency-button-pressed.png');
  });

  test('Input field states', async ({ page }) => {
    const systemInput = page.locator('input[placeholder*="Enter value"]').first();
    
    // Default state
    await expect(systemInput.locator('..').locator('..')).toHaveScreenshot('input-default-state.png');
    
    // Focused state
    await systemInput.focus();
    await expect(systemInput.locator('..').locator('..')).toHaveScreenshot('input-focused-state.png');
    
    // With content
    await systemInput.fill('Test Value');
    await expect(systemInput.locator('..').locator('..')).toHaveScreenshot('input-with-content.png');
  });

  test('Card status cycling', async ({ page }) => {
    const systemCard = page.locator('text=System Status').locator('..').locator('..');
    
    // Initial active state
    await expect(systemCard).toHaveScreenshot('card-active-state.png');
    
    // Click to cycle to next state
    await systemCard.click();
    await page.waitForTimeout(100); // Brief wait for state change
    await expect(systemCard).toHaveScreenshot('card-inactive-state.png');
    
    // Click again for error state
    await systemCard.click();
    await page.waitForTimeout(100);
    await expect(systemCard).toHaveScreenshot('card-error-state.png');
    
    // Click again for warning state
    await systemCard.click();
    await page.waitForTimeout(100);
    await expect(systemCard).toHaveScreenshot('card-warning-state.png');
  });

});

test.describe('Industrial Components - Cross-Browser Consistency', () => {
  
  test('Neumorphic shadows render consistently', async ({ page, browserName }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const shadowsSection = page.locator('text=Neumorphic Shadows').locator('..').locator('..');
    await expect(shadowsSection).toHaveScreenshot(`shadows-${browserName}.png`);
  });

  test('Industrial bolts render consistently', async ({ page, browserName }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const boltsSection = page.locator('text=Industrial Fasteners').locator('..').locator('..');
    await expect(boltsSection).toHaveScreenshot(`bolts-${browserName}.png`);
  });

  test('Surface textures render consistently', async ({ page, browserName }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const texturesSection = page.locator('text=Industrial Surface Textures').locator('..').locator('..');
    await expect(texturesSection).toHaveScreenshot(`textures-${browserName}.png`);
  });

});

test.describe('Industrial Components - Responsive Design', () => {
  
  test('Mobile layout - Portrait', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('mobile-portrait-layout.png', {
      fullPage: true,
    });
  });

  test('Mobile layout - Landscape', async ({ page }) => {
    await page.setViewportSize({ width: 667, height: 375 }); // iPhone SE landscape
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('mobile-landscape-layout.png', {
      fullPage: true,
    });
  });

  test('Tablet layout', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('tablet-layout.png', {
      fullPage: true,
    });
  });

  test('Desktop layout - Large', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 }); // Full HD
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('desktop-large-layout.png', {
      fullPage: true,
    });
  });

});