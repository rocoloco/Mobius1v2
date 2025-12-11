import { test, expect } from '@playwright/test';

test.describe('Layout Analysis and Fix', () => {
  test('analyze layout issues and provide fix recommendations', async ({ page }) => {
    // Navigate to the workbench
    await page.goto('/');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Get viewport dimensions
    const viewportSize = page.viewportSize();
    console.log('Viewport size:', viewportSize);
    
    // Analyze key elements
    const dataPlate = page.locator('.hidden.lg\\:block.absolute.top-24.left-8').first();
    const mainContent = page.locator('main > div.flex-1.flex.flex-col');
    const viewport = page.locator('[class*="aspect-video"]').first();
    const monitoringPanel = page.locator('.hidden.xl\\:block.absolute.top-24').first();
    const complianceSection = page.locator('text=COMPLIANCE').locator('..').locator('..');
    const telemetrySection = page.locator('text=TELEMETRY').locator('..').locator('..');
    
    // Get bounding boxes
    const dataPlateBox = await dataPlate.boundingBox();
    const mainContentBox = await mainContent.boundingBox();
    const viewportBox = await viewport.boundingBox();
    const monitoringBox = await monitoringPanel.boundingBox();
    const complianceBox = await complianceSection.boundingBox();
    const telemetryBox = await telemetrySection.boundingBox();
    
    console.log('=== LAYOUT ANALYSIS ===');
    console.log('DataPlate:', dataPlateBox);
    console.log('Main Content:', mainContentBox);
    console.log('Viewport:', viewportBox);
    console.log('Monitoring Panel:', monitoringBox);
    console.log('Compliance Section:', complianceBox);
    console.log('Telemetry Section:', telemetryBox);
    
    // Check for overlaps
    if (monitoringBox && viewportBox) {
      const overlap = monitoringBox.x < (viewportBox.x + viewportBox.width);
      console.log('Monitoring overlaps viewport:', overlap);
      
      if (overlap) {
        console.log('ISSUE: Monitoring panel overlaps with viewport');
        console.log('Monitoring starts at x:', monitoringBox.x);
        console.log('Viewport ends at x:', viewportBox.x + viewportBox.width);
      }
    }
    
    // Check alignment with DataPlate
    if (dataPlateBox && viewportBox) {
      const alignmentDiff = Math.abs(dataPlateBox.y - viewportBox.y);
      console.log('DataPlate vs Viewport Y alignment diff:', alignmentDiff);
      
      if (alignmentDiff > 10) {
        console.log('ISSUE: DataPlate and Viewport not aligned vertically');
      }
    }
    
    // Check if telemetry is cut off
    if (telemetryBox && viewportSize) {
      const cutoff = (telemetryBox.y + telemetryBox.height) > viewportSize.height;
      console.log('Telemetry cut off:', cutoff);
      
      if (cutoff) {
        console.log('ISSUE: Telemetry section extends beyond viewport');
        console.log('Telemetry bottom:', telemetryBox.y + telemetryBox.height);
        console.log('Viewport height:', viewportSize.height);
      }
    }
    
    // Take detailed screenshots
    await page.screenshot({ 
      path: 'test-results/layout-analysis-full.png',
      fullPage: true 
    });
    
    // Highlight problem areas with CSS
    await page.addStyleTag({
      content: `
        .hidden.xl\\:block.absolute.top-24 {
          outline: 3px solid red !important;
          outline-offset: 2px;
        }
        [class*="aspect-video"] {
          outline: 3px solid blue !important;
          outline-offset: 2px;
        }
        .hidden.lg\\:block.absolute.top-24.left-8 {
          outline: 3px solid green !important;
          outline-offset: 2px;
        }
      `
    });
    
    await page.screenshot({ 
      path: 'test-results/layout-analysis-highlighted.png',
      fullPage: true 
    });
    
    console.log('=== RECOMMENDATIONS ===');
    console.log('1. Remove absolute positioning from monitoring panel');
    console.log('2. Use flex layout with proper gap');
    console.log('3. Align monitoring panel top with viewport top');
    console.log('4. Ensure proper height constraints for telemetry');
  });
});