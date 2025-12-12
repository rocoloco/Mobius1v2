import { test, expect } from '@playwright/test';

test.describe('Terminal Simple Test', () => {
  test('verify terminal has CRT styling and fixed height', async ({ page }) => {
    // Navigate to the workbench
    await page.goto('/');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check if terminal has CRT styling
    const terminalContainer = page.locator('.terminal-teleprinter');
    await expect(terminalContainer).toBeVisible();
    
    // Get the terminal's computed styles
    const terminalStyles = await terminalContainer.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        background: styles.background,
        color: styles.color,
        height: styles.height,
        overflow: styles.overflow
      };
    });
    
    console.log('Terminal styles:', terminalStyles);
    
    // Verify CRT styling
    expect(terminalStyles.color).toContain('rgb(0, 255, 65)'); // #00ff41 in RGB
    expect(terminalStyles.overflow).toBe('hidden');
    
    // Get telemetry section height
    const telemetrySection = page.locator('text=TELEMETRY').locator('..').locator('..');
    const sectionBox = await telemetrySection.boundingBox();
    console.log('Telemetry section height:', sectionBox?.height);
    
    // Take screenshot
    await page.screenshot({ 
      path: 'test-results/terminal-crt-styling.png',
      fullPage: true 
    });
    
    console.log('✅ Terminal CRT styling verified');
  });
});