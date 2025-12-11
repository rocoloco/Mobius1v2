import { test, expect } from '@playwright/test';

test('reticle visibility analysis', async ({ page }) => {
  await page.goto('http://localhost:5174');
  
  // Wait for the viewport to load
  await page.waitForSelector('[data-testid="recessed-screen"]', { timeout: 10000 });
  
  // Get the viewport container dimensions
  const viewport = await page.locator('[data-testid="recessed-screen"]').first();
  const viewportBox = await viewport.boundingBox();
  
  console.log('Viewport dimensions:', viewportBox);
  
  // Check if reticles are present and get their positions
  const reticles = await page.locator('[aria-hidden="true"]').filter({ hasText: '' });
  const reticleCount = await reticles.count();
  
  console.log('Number of reticle elements found:', reticleCount);
  
  // Get parent container info
  const parentContainer = await page.locator('.aspect-video.bg-surface').first();
  const parentBox = await parentContainer.boundingBox();
  const parentStyles = await parentContainer.evaluate(el => {
    const styles = window.getComputedStyle(el);
    return {
      padding: styles.padding,
      borderRadius: styles.borderRadius,
      overflow: styles.overflow
    };
  });
  
  console.log('Parent container dimensions:', parentBox);
  console.log('Parent container styles:', parentStyles);
  
  // Check RecessedScreen styles
  const recessedStyles = await viewport.evaluate(el => {
    const styles = window.getComputedStyle(el);
    return {
      overflow: styles.overflow,
      borderRadius: styles.borderRadius,
      position: styles.position
    };
  });
  
  console.log('RecessedScreen styles:', recessedStyles);
});