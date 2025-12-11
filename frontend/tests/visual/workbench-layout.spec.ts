import { test, expect } from '@playwright/test';

test.describe('Workbench Layout Analysis', () => {
  test('capture current workbench layout for analysis', async ({ page }) => {
    // Navigate to the workbench
    await page.goto('/');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    
    // Wait for any animations to complete
    await page.waitForTimeout(2000);
    
    // Take a full page screenshot
    await page.screenshot({ 
      path: 'test-results/workbench-current-layout.png',
      fullPage: true 
    });
    
    // Take a screenshot of just the main content area
    const mainContent = page.locator('main');
    await mainContent.screenshot({ 
      path: 'test-results/workbench-main-content.png' 
    });
    
    // Check if monitoring components are visible
    const complianceRadar = page.locator('text=COMPLIANCE');
    const telemetry = page.locator('text=TELEMETRY');
    
    await expect(complianceRadar).toBeVisible();
    await expect(telemetry).toBeVisible();
    
    // Take screenshots of individual monitoring components
    if (await complianceRadar.isVisible()) {
      const complianceSection = complianceRadar.locator('..').locator('..');
      await complianceSection.screenshot({ 
        path: 'test-results/compliance-radar.png' 
      });
    }
    
    if (await telemetry.isVisible()) {
      const telemetrySection = telemetry.locator('..').locator('..');
      await telemetrySection.screenshot({ 
        path: 'test-results/telemetry-terminal.png' 
      });
    }
    
    // Get viewport dimensions and element positions for analysis
    const viewportSize = page.viewportSize();
    console.log('Viewport size:', viewportSize);
    
    // Get bounding boxes of key elements
    const dataPlate = page.locator('[class*="DataPlate"], [class*="data-plate"]').first();
    const viewport = page.locator('[class*="RecessedScreen"]').first();
    const monitoringPanel = page.locator('text=COMPLIANCE').locator('..').locator('..').locator('..');
    
    if (await dataPlate.isVisible()) {
      const dataPlateBox = await dataPlate.boundingBox();
      console.log('DataPlate position:', dataPlateBox);
    }
    
    if (await viewport.isVisible()) {
      const viewportBox = await viewport.boundingBox();
      console.log('Viewport position:', viewportBox);
    }
    
    if (await monitoringPanel.isVisible()) {
      const monitoringBox = await monitoringPanel.boundingBox();
      console.log('Monitoring panel position:', monitoringBox);
    }
  });
});