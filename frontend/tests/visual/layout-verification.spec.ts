import { test, expect } from '@playwright/test';

test.describe('Layout Verification', () => {
  test('verify fixed layout is correct', async ({ page }) => {
    // Navigate to the workbench
    await page.goto('/');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Take a screenshot of the fixed layout
    await page.screenshot({ 
      path: 'test-results/layout-fixed.png',
      fullPage: true 
    });
    
    // Verify monitoring components are visible
    await expect(page.locator('text=COMPLIANCE')).toBeVisible();
    await expect(page.locator('text=TELEMETRY')).toBeVisible();
    
    // Verify no overlap by checking positions
    const viewport = page.locator('[class*="aspect-video"]').first();
    const monitoringPanel = page.locator('text=COMPLIANCE').locator('..').locator('..').locator('..');
    
    const viewportBox = await viewport.boundingBox();
    const monitoringBox = await monitoringPanel.boundingBox();
    
    console.log('Viewport:', viewportBox);
    console.log('Monitoring Panel:', monitoringBox);
    
    // Check no overlap
    if (viewportBox && monitoringBox) {
      const noOverlap = (viewportBox.x + viewportBox.width) <= monitoringBox.x;
      console.log('No overlap:', noOverlap);
      expect(noOverlap).toBeTruthy();
    }
    
    // Verify terminal is not cut off
    const viewportSize = page.viewportSize();
    if (monitoringBox && viewportSize) {
      const notCutOff = (monitoringBox.y + monitoringBox.height) <= viewportSize.height;
      console.log('Terminal not cut off:', notCutOff);
      expect(notCutOff).toBeTruthy();
    }
    
    console.log('✅ Layout verification passed!');
  });
});