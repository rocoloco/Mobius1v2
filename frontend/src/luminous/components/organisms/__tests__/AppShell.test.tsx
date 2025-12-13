/**
 * Unit Test: AppShell Component
 * 
 * Tests the AppShell organism component to verify:
 * - Fixed header renders with correct height
 * - Logo and branding text are present
 * - Utilities section contains connection pulse, settings, and avatar
 * - Children are rendered with correct offset
 * - Glassmorphism styling is applied
 * 
 * Validates: Requirements 2.1-2.10
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AppShell } from '../AppShell';

describe('AppShell Component', () => {
  it('should render fixed header with correct height', () => {
    render(
      <AppShell connectionStatus="connected">
        <div>Test Content</div>
      </AppShell>
    );

    const header = screen.getByTestId('app-shell-header');
    expect(header).toBeTruthy();
    expect(header.className).toContain('h-16');
    expect(header.className).toContain('fixed');
  });

  it('should render logo and branding text', () => {
    const { container } = render(
      <AppShell connectionStatus="connected">
        <div>Test Content</div>
      </AppShell>
    );

    // Check for branding text (now an h1 for accessibility)
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toBeTruthy();
    expect(heading.textContent).toBe('Brand Governance Engine');
    
    // Check for logo image (aria-hidden for decorative image)
    const logo = container.querySelector('img[src="/mobius-icon-dark.svg"]');
    expect(logo).toBeTruthy();
    expect(logo?.getAttribute('aria-hidden')).toBe('true');
  });

  it('should render connection pulse in utilities section', () => {
    render(
      <AppShell connectionStatus="connected">
        <div>Test Content</div>
      </AppShell>
    );

    const connectionPulse = screen.getByTestId('connection-pulse');
    expect(connectionPulse).toBeTruthy();
  });

  it('should render settings button in utilities section', () => {
    const handleSettingsClick = vi.fn();
    
    render(
      <AppShell connectionStatus="connected" onSettingsClick={handleSettingsClick}>
        <div>Test Content</div>
      </AppShell>
    );

    const settingsButton = screen.getByTestId('settings-button');
    expect(settingsButton).toBeTruthy();
    expect(settingsButton.getAttribute('aria-label')).toBe('Settings');
  });

  it('should call onSettingsClick when settings button is clicked', () => {
    const handleSettingsClick = vi.fn();
    
    render(
      <AppShell connectionStatus="connected" onSettingsClick={handleSettingsClick}>
        <div>Test Content</div>
      </AppShell>
    );

    const settingsButton = screen.getByTestId('settings-button');
    fireEvent.click(settingsButton);
    
    expect(handleSettingsClick).toHaveBeenCalledOnce();
  });

  it('should render user avatar in utilities section', () => {
    render(
      <AppShell connectionStatus="connected">
        <div>Test Content</div>
      </AppShell>
    );

    const avatar = screen.getByTestId('user-avatar');
    expect(avatar).toBeTruthy();
    expect(avatar.getAttribute('aria-label')).toBe('User profile');
  });

  it('should render custom user avatar image when provided', () => {
    const avatarUrl = 'https://example.com/avatar.jpg';
    
    render(
      <AppShell connectionStatus="connected" userAvatar={avatarUrl}>
        <div>Test Content</div>
      </AppShell>
    );

    const avatarImg = screen.getByAltText('User avatar');
    expect(avatarImg).toBeTruthy();
    expect(avatarImg.getAttribute('src')).toBe(avatarUrl);
  });

  it('should render children with 64px offset', () => {
    const { container } = render(
      <AppShell connectionStatus="connected">
        <div data-testid="child-content">Test Content</div>
      </AppShell>
    );

    const main = container.querySelector('main');
    expect(main).toBeTruthy();
    // Main content uses marginTop instead of paddingTop for offset
    expect(main?.style.marginTop).toBe('64px');
    
    const childContent = screen.getByTestId('child-content');
    expect(childContent).toBeTruthy();
  });

  it('should apply glassmorphism styling to header', () => {
    render(
      <AppShell connectionStatus="connected">
        <div>Test Content</div>
      </AppShell>
    );

    const header = screen.getByTestId('app-shell-header');
    
    // Check for glassmorphism classes
    expect(header.className).toContain('bg-white/5');
    expect(header.className).toContain('backdrop-blur-md');
    expect(header.className).toContain('border-b');
    expect(header.className).toContain('border-white/10');
  });

  it('should pass connection status to ConnectionPulse', () => {
    const { rerender } = render(
      <AppShell connectionStatus="connected">
        <div>Test Content</div>
      </AppShell>
    );

    let connectionPulse = screen.getByTestId('connection-pulse');
    expect(connectionPulse.className).toContain('bg-green-500');

    // Test with different status
    rerender(
      <AppShell connectionStatus="disconnected">
        <div>Test Content</div>
      </AppShell>
    );

    connectionPulse = screen.getByTestId('connection-pulse');
    expect(connectionPulse.className).toContain('bg-red-500');
  });

  it('should apply deep charcoal background to container', () => {
    const { container } = render(
      <AppShell connectionStatus="connected">
        <div>Test Content</div>
      </AppShell>
    );

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('bg-[#101012]');
  });
});
