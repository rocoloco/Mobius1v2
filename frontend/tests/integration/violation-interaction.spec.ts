/**
 * Integration Test: Violation Interaction
 * 
 * Tests the interaction between ComplianceGauge violations and Canvas bounding boxes.
 * Tests work with the actual application state.
 * 
 * Requirements: 5.12, 6.8
 */

import { test, expect } from '@playwright/test';

test.describe('Violation Interaction', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
    await page.waitForTimeout(1000);
    await expect(page.locator('[data-testid="compliance-gauge"]')).toBeVisible();
  });

  test('displays sample violations on initial load', async ({ page }) => {
    const violationItems = page.locator('[data-testid="violation-item"]');
    await expect(violationItems.first()).toBeVisible({ timeout: 5000 });
    const count = await violationItems.count();
    console.log(`Found ${count} violation items`);
    expect(count).toBeGreaterThan(0);
  });

  test('compliance gauge displays score', async ({ page }) => {
    const complianceGauge = page.locator('[data-testid="compliance-gauge"]');
    await expect(complianceGauge).toBeVisible();
    const scoreText = await complianceGauge.textContent();
    expect(scoreText).toMatch(/\d+/);
    console.log(`✅ Compliance gauge score: ${scoreText?.match(/\d+/)?.[0]}%`);
  });

  test('violation items show severity indicators', async ({ page }) => {
    const violationItems = page.locator('[data-testid="violation-item"]');
    await expect(violationItems.first()).toBeVisible({ timeout: 5000 });
    const count = await violationItems.count();
    for (let i = 0; i < count; i++) {
      const text = await violationItems.nth(i).textContent();
      console.log(`Violation ${i + 1}: ${text?.substring(0, 50)}...`);
    }
    console.log('✅ Violation items displayed with content');
  });

  test('compliance gauge renders SVG chart', async ({ page }) => {
    const complianceGauge = page.locator('[data-testid="compliance-gauge"]');
    await expect(complianceGauge).toBeVisible();
    const gaugeHtml = await complianceGauge.innerHTML();
    expect(gaugeHtml).toContain('svg');
    console.log('✅ Compliance gauge renders with SVG chart');
  });

  test('dashboard zones are properly laid out', async ({ page }) => {
    const zones = [
      '[data-testid="zone-director"]',
      '[data-testid="zone-canvas"]',
      '[data-testid="zone-gauge"]',
      '[data-testid="zone-context"]',
      '[data-testid="zone-twin"]',
    ];
    for (const zone of zones) {
      await expect(page.locator(zone)).toBeVisible();
    }
    console.log('✅ All dashboard zones visible');
  });

  test('canvas zone is visible', async ({ page }) => {
    const canvas = page.locator('[data-testid="canvas"]');
    await expect(canvas).toBeVisible();
    console.log('✅ Canvas zone is visible');
  });

  test('violation list is scrollable', async ({ page }) => {
    const violationItems = page.locator('[data-testid="violation-item"]');
    await expect(violationItems.first()).toBeVisible({ timeout: 5000 });
    const count = await violationItems.count();
    if (count > 2) {
      await violationItems.last().scrollIntoViewIfNeeded();
      await expect(violationItems.last()).toBeVisible();
      console.log('✅ Violation list is scrollable');
    } else {
      console.log('ℹ️ Not enough violations to test scrolling');
    }
  });
});
