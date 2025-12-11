import { test, expect } from '@playwright/test';

test('UI Alignment Analysis - Workbench Layout', async ({ page }) => {
  await page.goto('http://localhost:5174');
  
  // Wait for components to load
  await page.waitForSelector('[data-testid="recessed-screen"]', { timeout: 10000 });
  
  // Get viewport dimensions and position
  const viewport = await page.locator('.aspect-video.bg-surface').first();
  const viewportBox = await viewport.boundingBox();
  
  // Get DataPlate dimensions and position
  const dataPlate = await page.locator('.absolute.top-24.left-8').first();
  const dataPlateBox = await dataPlate.boundingBox();
  
  // Get GenerationHistory dimensions and position
  const historyPanel = await page.locator('.absolute.right-0.top-0').first();
  const historyBox = await historyPanel.boundingBox();
  
  console.log('=== LAYOUT ANALYSIS ===');
  console.log('Viewport:', viewportBox);
  console.log('DataPlate:', dataPlateBox);
  console.log('History Panel:', historyBox);
  
  // Calculate alignment
  if (viewportBox && dataPlateBox && historyBox) {
    const viewportCenter = viewportBox.x + viewportBox.width / 2;
    const screenCenter = await page.evaluate(() => window.innerWidth / 2);
    
    console.log('Viewport center X:', viewportCenter);
    console.log('Screen center X:', screenCenter);
    console.log('DataPlate top:', dataPlateBox.y);
    console.log('History top:', historyBox.y);
    console.log('Viewport top:', viewportBox.y);
    
    // Check vertical alignment
    const dataPlateAligned = Math.abs(dataPlateBox.y - viewportBox.y) < 50;
    const historyAligned = Math.abs(historyBox.y - viewportBox.y) < 50;
    
    console.log('DataPlate aligned with viewport:', dataPlateAligned);
    console.log('History aligned with viewport:', historyAligned);
  }
  
  // Take screenshot for visual analysis
  await page.screenshot({ 
    path: 'frontend/tests/visual/workbench-alignment.png',
    fullPage: true 
  });
  
  // Add alignment guides overlay
  await page.addStyleTag({
    content: `
      .alignment-guide {
        position: fixed;
        background: rgba(255, 0, 0, 0.3);
        z-index: 9999;
        pointer-events: none;
      }
      .vertical-guide {
        width: 2px;
        height: 100vh;
        top: 0;
      }
      .horizontal-guide {
        height: 2px;
        width: 100vw;
        left: 0;
      }
    `
  });
  
  // Add center line
  await page.evaluate(() => {
    const centerLine = document.createElement('div');
    centerLine.className = 'alignment-guide vertical-guide';
    centerLine.style.left = '50%';
    document.body.appendChild(centerLine);
  });
  
  // Screenshot with guides
  await page.screenshot({ 
    path: 'frontend/tests/visual/workbench-with-guides.png',
    fullPage: true 
  });
});