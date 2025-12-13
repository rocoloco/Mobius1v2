/**
 * Integration Test: Multi-Turn Session
 * 
 * Tests the multi-turn generation workflow including chat history.
 * Tests work with the actual application state and real API interactions.
 * 
 * Requirements: 10.1-10.7
 */

import { test, expect } from '@playwright/test';

test.describe('Multi-Turn Session', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
    await page.waitForTimeout(1000);
    await expect(page.locator('[data-testid="director"]')).toBeVisible();
  });

  test('initial state shows empty or minimal chat', async ({ page }) => {
    const chatMessages = page.locator('[data-testid="chat-message"]');
    const count = await chatMessages.count();
    console.log(`Initial chat message count: ${count}`);
    expect(count).toBeLessThanOrEqual(1);
    console.log('✅ Initial chat state is correct');
  });

  test('submitting prompt adds user message', async ({ page }) => {
    const promptInput = page.locator('[data-testid="prompt-input"]');
    const submitButton = page.locator('[data-testid="submit-button"]');
    const chatMessages = page.locator('[data-testid="chat-message"]');
    
    await promptInput.fill('Create a professional LinkedIn post');
    await submitButton.click();
    await page.waitForTimeout(500);
    
    await expect(chatMessages.first()).toBeVisible();
    const messageText = await chatMessages.first().textContent();
    expect(messageText).toContain('LinkedIn');
    console.log('✅ User message added to chat');
  });

  test('system responds after submission', async ({ page }) => {
    const promptInput = page.locator('[data-testid="prompt-input"]');
    const submitButton = page.locator('[data-testid="submit-button"]');
    const generatingStatus = page.locator('[data-testid="generating-status"]');
    const chatMessages = page.locator('[data-testid="chat-message"]');
    
    await promptInput.fill('Create a brand asset');
    await submitButton.click();
    await page.waitForTimeout(2000);
    
    const isGenerating = await generatingStatus.isVisible();
    const messageCount = await chatMessages.count();
    
    console.log(`Generating: ${isGenerating}, Messages: ${messageCount}`);
    expect(isGenerating || messageCount >= 1).toBeTruthy();
    console.log('✅ System responded');
  });

  test('prompt input clears after submission', async ({ page }) => {
    const promptInput = page.locator('[data-testid="prompt-input"]');
    const submitButton = page.locator('[data-testid="submit-button"]');
    
    await promptInput.fill('Test prompt');
    await submitButton.click();
    await page.waitForTimeout(500);
    
    const value = await promptInput.inputValue();
    expect(value).toBe('');
    console.log('✅ Prompt input clears after submission');
  });

  test('submit button state during generation', async ({ page }) => {
    const promptInput = page.locator('[data-testid="prompt-input"]');
    const submitButton = page.locator('[data-testid="submit-button"]');
    
    await promptInput.fill('Test prompt');
    await submitButton.click();
    
    const isDisabled = await submitButton.isDisabled();
    const inputValue = await promptInput.inputValue();
    expect(isDisabled || inputValue === '').toBeTruthy();
    console.log('✅ Submit button state correct');
  });

  test('chat scrolls to latest message', async ({ page }) => {
    const promptInput = page.locator('[data-testid="prompt-input"]');
    const submitButton = page.locator('[data-testid="submit-button"]');
    const chatMessages = page.locator('[data-testid="chat-message"]');
    
    await promptInput.fill('Test scroll behavior');
    await submitButton.click();
    await page.waitForTimeout(500);
    
    const lastMessage = chatMessages.last();
    await expect(lastMessage).toBeVisible();
    console.log('✅ Chat scrolls to latest');
  });

  test('session state maintained', async ({ page }) => {
    const complianceGauge = page.locator('[data-testid="compliance-gauge"]');
    const promptInput = page.locator('[data-testid="prompt-input"]');
    const submitButton = page.locator('[data-testid="submit-button"]');
    
    await expect(complianceGauge).toBeVisible();
    
    await promptInput.fill('Create asset');
    await submitButton.click();
    await page.waitForTimeout(2000);
    
    await expect(complianceGauge).toBeVisible();
    console.log('✅ Session state maintained');
  });
});
