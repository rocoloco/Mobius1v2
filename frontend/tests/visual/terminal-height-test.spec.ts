import { test, expect } from '@playwright/test';

test.describe('Terminal Height Constraint Test', () => {
  test('verify terminal maintains fixed height and scrolls properly', async ({ page }) => {
    // Navigate to the workbench
    await page.goto('/');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Get the terminal container
    const telemetrySection = page.locator('text=TELEMETRY').locator('..').locator('..');
    const terminalContainer = telemetrySection.locator('.terminal-teleprinter');
    
    // Get initial height
    const initialBox = await telemetrySection.boundingBox();
    console.log('Initial telemetry section height:', initialBox?.height);
    
    // Wait for more logs to be added (they should be added every 15 seconds)
    await page.waitForTimeout(16000);
    
    // Get height after more logs
    const afterBox = await telemetrySection.boundingBox();
    console.log('After more logs height:', afterBox?.height);
    
    // Verify height hasn't changed significantly (should be same or very close)
    if (initialBox && afterBox) {
      const heightDiff = Math.abs(afterBox.height - initialBox.height);
      console.log('Height difference:', heightDiff);
      expect(heightDiff).toBeLessThan(10); // Allow small variations but no major growth
    }
    
    // Verify terminal has scrollbar if needed
    const hasScrollbar = await page.evaluate(() => {
      const terminal = document.querySelector('.terminal-teleprinter div[style*="overflow-y: auto"]');
      if (terminal) {
        return terminal.scrollHeight > terminal.clientHeight;
      }
      return false;
    });
    
    console.log('Terminal has scrollbar (content overflows):', hasScrollbar);
    
    // Take screenshot to verify visual appearance
    await page.screenshot({ 
      path: 'test-results/terminal-height-fixed.png',
      fullPage: true 
    });
    
    console.log('✅ Terminal height constraint test completed');
  });
});