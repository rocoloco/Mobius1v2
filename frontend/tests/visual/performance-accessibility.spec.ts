/**
 * Industrial Design System - Performance & Accessibility Tests
 * 
 * Tests for performance metrics and accessibility compliance
 */

import { test, expect } from '@playwright/test';

test.describe('Industrial Design System - Performance Tests', () => {
  
  test('Page load performance', async ({ page }) => {
    // Start measuring performance
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Assert reasonable load time (adjust threshold as needed)
    expect(loadTime).toBeLessThan(5000); // 5 seconds max
    
    console.log(`Page load time: ${loadTime}ms`);
  });

  test('Animation performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test button hover animation performance
    const button = page.locator('text=Primary Control').first();
    
    // Measure hover animation
    const startTime = Date.now();
    await button.hover();
    await page.waitForTimeout(500); // Wait for animation
    const animationTime = Date.now() - startTime;
    
    expect(animationTime).toBeLessThan(1000); // Animation should complete quickly
    
    console.log(`Hover animation time: ${animationTime}ms`);
  });

  test('Memory usage - Component rendering', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Get initial memory usage
    const initialMetrics = await page.evaluate(() => {
      return (performance as any).memory ? {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
      } : null;
    });
    
    if (initialMetrics) {
      console.log('Memory usage:', initialMetrics);
      
      // Assert reasonable memory usage (adjust as needed)
      expect(initialMetrics.usedJSHeapSize).toBeLessThan(50 * 1024 * 1024); // 50MB max
    }
  });

  test('CSS bundle size impact', async ({ page }) => {
    await page.goto('/');
    
    // Get all stylesheets
    const stylesheets = await page.evaluate(() => {
      const sheets = Array.from(document.styleSheets);
      return sheets.map(sheet => {
        try {
          return {
            href: sheet.href,
            rules: sheet.cssRules ? sheet.cssRules.length : 0
          };
        } catch (e) {
          return { href: sheet.href, rules: 'Access denied' };
        }
      });
    });
    
    console.log('Loaded stylesheets:', stylesheets);
    
    // Assert reasonable number of CSS rules
    const totalRules = stylesheets.reduce((sum, sheet) => 
      sum + (typeof sheet.rules === 'number' ? sheet.rules : 0), 0
    );
    
    expect(totalRules).toBeLessThan(10000); // Reasonable CSS rule count
  });

});

test.describe('Industrial Design System - Accessibility Tests', () => {
  
  test('Keyboard navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test tab navigation through interactive elements
    const interactiveElements = page.locator('button, input, [tabindex="0"]');
    const elementCount = await interactiveElements.count();
    
    // Tab through first few elements
    for (let i = 0; i < Math.min(elementCount, 5); i++) {
      await page.keyboard.press('Tab');
      
      // Take screenshot of focused element
      const focusedElement = page.locator(':focus');
      if (await focusedElement.count() > 0) {
        await expect(focusedElement).toHaveScreenshot(`focused-element-${i + 1}.png`);
      }
    }
  });

  test('Color contrast validation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check color contrast for text elements
    const textElements = page.locator('h1, h2, h3, p, span, label, button');
    const elementCount = await textElements.count();
    
    for (let i = 0; i < Math.min(elementCount, 10); i++) {
      const element = textElements.nth(i);
      
      const styles = await element.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          color: computed.color,
          backgroundColor: computed.backgroundColor,
          fontSize: computed.fontSize,
        };
      });
      
      console.log(`Element ${i + 1} styles:`, styles);
      
      // Basic validation - ensure text has color
      expect(styles.color).not.toBe('rgba(0, 0, 0, 0)');
    }
  });

  test('ARIA attributes validation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check for proper ARIA attributes on interactive elements
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      
      const ariaLabel = await button.getAttribute('aria-label');
      const ariaDisabled = await button.getAttribute('aria-disabled');
      const role = await button.getAttribute('role');
      
      // Buttons should have accessible names
      const hasAccessibleName = ariaLabel || await button.textContent();
      expect(hasAccessibleName).toBeTruthy();
      
      console.log(`Button ${i + 1}:`, { ariaLabel, ariaDisabled, role, hasAccessibleName: !!hasAccessibleName });
    }
  });

  test('Screen reader compatibility', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test heading structure
    const headings = page.locator('h1, h2, h3, h4, h5, h6');
    const headingCount = await headings.count();
    
    const headingStructure: Array<{ level: string; text: string | null }> = [];
    for (let i = 0; i < headingCount; i++) {
      const heading = headings.nth(i);
      const tagName = await heading.evaluate(el => el.tagName.toLowerCase());
      const text = await heading.textContent();
      
      headingStructure.push({ level: tagName, text });
    }
    
    console.log('Heading structure:', headingStructure);
    
    // Should have proper heading hierarchy (h1 -> h2 -> h3, etc.)
    expect(headingStructure[0]?.level).toBe('h1');
    
    // Take screenshot with headings highlighted
    await page.addStyleTag({
      content: `
        h1, h2, h3, h4, h5, h6 {
          outline: 3px solid red !important;
          outline-offset: 2px !important;
        }
        h1::before { content: "H1: "; color: red; font-weight: bold; }
        h2::before { content: "H2: "; color: orange; font-weight: bold; }
        h3::before { content: "H3: "; color: blue; font-weight: bold; }
      `
    });
    
    await expect(page).toHaveScreenshot('heading-structure-highlighted.png', {
      fullPage: true,
    });
  });

  test('Focus indicators visibility', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Enhance focus indicators for testing
    await page.addStyleTag({
      content: `
        *:focus {
          outline: 3px solid #ff0000 !important;
          outline-offset: 2px !important;
          box-shadow: 0 0 0 5px rgba(255, 0, 0, 0.3) !important;
        }
      `
    });
    
    // Tab through elements and capture focus states
    const focusableElements = page.locator('button, input, [tabindex="0"]');
    const elementCount = await focusableElements.count();
    
    for (let i = 0; i < Math.min(elementCount, 3); i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
      
      await expect(page).toHaveScreenshot(`focus-indicator-${i + 1}.png`);
    }
  });

});

test.describe('Industrial Design System - Cross-Platform Consistency', () => {
  
  test('Font rendering consistency', async ({ page, browserName }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Focus on typography-heavy section
    const headerSection = page.locator('h1').first().locator('..');
    await expect(headerSection).toHaveScreenshot(`typography-${browserName}.png`);
  });

  test('SVG rendering consistency', async ({ page, browserName }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Focus on SVG-heavy section (bolts)
    const boltsSection = page.locator('text=Industrial Fasteners').locator('..').locator('..');
    await expect(boltsSection).toHaveScreenshot(`svg-rendering-${browserName}.png`);
  });

  test('CSS Grid layout consistency', async ({ page, browserName }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test grid layouts
    const gridSection = page.locator('text=Industrial Control Panels').locator('..').locator('..');
    await expect(gridSection).toHaveScreenshot(`grid-layout-${browserName}.png`);
  });

});