import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Set viewport for consistent screenshots
  await page.setViewportSize({ width: 1280, height: 720 });
  
  // Navigate to the demo
  await page.goto('http://localhost:5173');
  await page.waitForLoadState('networkidle');
  
  // Take full page screenshot
  await page.screenshot({ 
    path: 'ui-analysis-full-page.png', 
    fullPage: true 
  });
  
  // Take screenshots of specific sections that might have UI/UX issues
  
  // 1. Header section
  const header = page.locator('h1').first().locator('..');
  await header.screenshot({ path: 'ui-analysis-header.png' });
  
  // 2. Control panels section
  const controlPanels = page.locator('text=Industrial Control Panels').locator('..').locator('..');
  await controlPanels.screenshot({ path: 'ui-analysis-control-panels.png' });
  
  // 3. Buttons section
  const buttons = page.locator('text=Industrial Control Buttons').locator('..').locator('..');
  await buttons.screenshot({ path: 'ui-analysis-buttons.png' });
  
  // 4. Form controls section
  const forms = page.locator('text=Industrial Form Controls').locator('..').locator('..');
  await forms.screenshot({ path: 'ui-analysis-forms.png' });
  
  // 5. Status indicators section
  const indicators = page.locator('text=Industrial Status Indicators').locator('..').locator('..');
  await indicators.screenshot({ path: 'ui-analysis-indicators.png' });
  
  // 6. Manufacturing hardware section
  const hardware = page.locator('text=Manufacturing Hardware Details').locator('..').locator('..');
  await hardware.screenshot({ path: 'ui-analysis-hardware.png' });
  
  console.log('Screenshots saved for UI/UX analysis');
  
  await browser.close();
})();