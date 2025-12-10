/**
 * Industrial Components - Isolated Visual Tests
 * 
 * Tests individual components in isolation for precise visual validation
 */

import { test, expect } from '@playwright/test';

test.describe('Industrial Components - Isolated Testing', () => {
  
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

  test('Individual Industrial Bolts', async ({ page }) => {
    // Test each bolt type individually
    const boltTypes = ['Phillips', 'Flathead', 'Torx', 'Hex'];
    
    for (const boltType of boltTypes) {
      const boltElement = page.locator(`text=${boltType}`).locator('..').first();
      await expect(boltElement).toHaveScreenshot(`bolt-${boltType.toLowerCase()}.png`);
    }
  });

  test('Individual Connector Ports', async ({ page }) => {
    const portTypes = ['Ethernet', 'USB', 'Power', 'Data'];
    
    for (const portType of portTypes) {
      const portElement = page.locator(`text=${portType}`).locator('..').first();
      await expect(portElement).toHaveScreenshot(`port-${portType.toLowerCase()}.png`);
    }
  });

  test('Individual Surface Textures', async ({ page }) => {
    const textureTypes = ['Brushed Metal', 'Diamond Plate', 'Perforated', 'Carbon Fiber'];
    
    for (const textureType of textureTypes) {
      const textureElement = page.locator(`text=${textureType}`).locator('..');
      await expect(textureElement).toHaveScreenshot(`texture-${textureType.toLowerCase().replace(' ', '-')}.png`);
    }
  });

  test('Individual Status Indicators', async ({ page }) => {
    const indicatorLabels = ['System Offline', 'System Online', 'Critical Error', 'Warning State', 'All Systems Go'];
    
    for (const label of indicatorLabels) {
      const indicatorElement = page.locator(`text=${label}`).locator('..');
      await expect(indicatorElement).toHaveScreenshot(`indicator-${label.toLowerCase().replace(/\s+/g, '-')}.png`);
    }
  });

  test('Button Size Variations', async ({ page }) => {
    // Test different button sizes if available
    const buttons = page.locator('button').filter({ hasText: /Control|Action|Process/ });
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < Math.min(buttonCount, 5); i++) {
      const button = buttons.nth(i);
      const buttonText = await button.textContent();
      const safeFileName = buttonText?.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '') || `button-${i}`;
      await expect(button).toHaveScreenshot(`button-${safeFileName}.png`);
    }
  });

  test('Input Field Variations', async ({ page }) => {
    const inputs = page.locator('input[type="text"]');
    const inputCount = await inputs.count();
    
    for (let i = 0; i < inputCount; i++) {
      const input = inputs.nth(i);
      const inputContainer = input.locator('..').locator('..');
      await expect(inputContainer).toHaveScreenshot(`input-field-${i + 1}.png`);
    }
  });

  test('Neumorphic Shadow Variations', async ({ page }) => {
    const shadowVariants = ['subtle', 'normal', 'deep'];
    const shadowTypes = ['Raised', 'Recessed'];
    
    for (const variant of shadowVariants) {
      for (const type of shadowTypes) {
        const shadowElement = page.locator(`text=${type}`).filter({ hasText: type }).first();
        if (await shadowElement.count() > 0) {
          await expect(shadowElement).toHaveScreenshot(`shadow-${variant}-${type.toLowerCase()}.png`);
        }
      }
    }
  });

  test('Color Palette Swatches', async ({ page }) => {
    const colorSection = page.locator('text=Color Palette').locator('..').locator('div').nth(1);
    const colorSwatches = colorSection.locator('div').filter({ has: page.locator('div[style*="background-color"]') });
    const swatchCount = await colorSwatches.count();
    
    for (let i = 0; i < swatchCount; i++) {
      const swatch = colorSwatches.nth(i);
      await expect(swatch).toHaveScreenshot(`color-swatch-${i + 1}.png`);
    }
  });

});

test.describe('Industrial Components - Detailed Measurements', () => {
  
  test('Component spacing and alignment', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Add measurement grid overlay for visual validation
    await page.addStyleTag({
      content: `
        body::before {
          content: '';
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-image: 
            linear-gradient(rgba(255,0,0,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,0,0,0.1) 1px, transparent 1px);
          background-size: 20px 20px;
          pointer-events: none;
          z-index: 9999;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('layout-with-grid-overlay.png', {
      fullPage: true,
    });
  });

  test('Typography consistency', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Highlight all text elements
    await page.addStyleTag({
      content: `
        h1, h2, h3, h4, h5, h6 { outline: 2px solid red !important; }
        p { outline: 1px solid blue !important; }
        span { outline: 1px solid green !important; }
        label { outline: 1px solid orange !important; }
      `
    });
    
    await expect(page).toHaveScreenshot('typography-outline-view.png', {
      fullPage: true,
    });
  });

  test('Shadow depth consistency', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Enhance shadow visibility for testing
    await page.addStyleTag({
      content: `
        [style*="box-shadow"] {
          outline: 1px dashed rgba(255, 0, 255, 0.5) !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('shadow-elements-highlighted.png', {
      fullPage: true,
    });
  });

});