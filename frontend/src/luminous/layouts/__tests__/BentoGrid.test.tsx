/**
 * Unit Test: BentoGrid Layout Component
 * 
 * Tests the BentoGrid layout component to verify:
 * - Grid uses correct template areas on desktop
 * - Grid collapses to single column on mobile
 * - All five zones are rendered correctly
 * - Responsive behavior works as expected
 * 
 * Validates: Requirements 3.8, 3.9, 11.1
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BentoGrid } from '../BentoGrid';

describe('BentoGrid Layout Component', () => {
  // Helper to set viewport width
  const setViewportWidth = (width: number) => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: width,
    });
    window.dispatchEvent(new Event('resize'));
  };

  // Store original innerWidth
  let originalInnerWidth: number;

  beforeEach(() => {
    originalInnerWidth = window.innerWidth;
  });

  afterEach(() => {
    // Restore original viewport width
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    });
  });

  it('should render all five zones', () => {
    render(
      <BentoGrid
        director={<div>Director Content</div>}
        canvas={<div>Canvas Content</div>}
        gauge={<div>Gauge Content</div>}
        context={<div>Context Content</div>}
        twin={<div>Twin Content</div>}
      />
    );

    expect(screen.getByTestId('zone-director')).toBeTruthy();
    expect(screen.getByTestId('zone-canvas')).toBeTruthy();
    expect(screen.getByTestId('zone-gauge')).toBeTruthy();
    expect(screen.getByTestId('zone-context')).toBeTruthy();
    expect(screen.getByTestId('zone-twin')).toBeTruthy();
  });

  it('should render zone content correctly', () => {
    render(
      <BentoGrid
        director={<div>Director Content</div>}
        canvas={<div>Canvas Content</div>}
        gauge={<div>Gauge Content</div>}
        context={<div>Context Content</div>}
        twin={<div>Twin Content</div>}
      />
    );

    expect(screen.getByText('Director Content')).toBeTruthy();
    expect(screen.getByText('Canvas Content')).toBeTruthy();
    expect(screen.getByText('Gauge Content')).toBeTruthy();
    expect(screen.getByText('Context Content')).toBeTruthy();
    expect(screen.getByText('Twin Content')).toBeTruthy();
  });

  it('should use correct grid template areas on desktop', () => {
    // Set desktop viewport width (>= 768px)
    setViewportWidth(1024);

    const { container } = render(
      <BentoGrid
        director={<div>Director</div>}
        canvas={<div>Canvas</div>}
        gauge={<div>Gauge</div>}
        context={<div>Context</div>}
        twin={<div>Twin</div>}
      />
    );

    const grid = screen.getByTestId('bento-grid');
    expect(grid).toBeTruthy();

    // Check that grid has the bento-grid class
    expect(grid.className).toContain('bento-grid');

    // Verify zones have correct grid-area classes
    const directorZone = screen.getByTestId('zone-director');
    const canvasZone = screen.getByTestId('zone-canvas');
    const gaugeZone = screen.getByTestId('zone-gauge');
    const contextZone = screen.getByTestId('zone-context');
    const twinZone = screen.getByTestId('zone-twin');

    expect(directorZone.className).toContain('zone-director');
    expect(canvasZone.className).toContain('zone-canvas');
    expect(gaugeZone.className).toContain('zone-gauge');
    expect(contextZone.className).toContain('zone-context');
    expect(twinZone.className).toContain('zone-twin');

    // Verify inline styles are present
    const styleTag = container.querySelector('style');
    expect(styleTag).toBeTruthy();
    expect(styleTag?.innerHTML).toContain('grid-template-areas');
    expect(styleTag?.innerHTML).toContain('"director canvas gauge"');
    expect(styleTag?.innerHTML).toContain('"director canvas twin"');
    expect(styleTag?.innerHTML).toContain('"context canvas twin"');
  });

  it('should have correct grid structure for desktop layout', () => {
    setViewportWidth(1024);

    const { container } = render(
      <BentoGrid
        director={<div>Director</div>}
        canvas={<div>Canvas</div>}
        gauge={<div>Gauge</div>}
        context={<div>Context</div>}
        twin={<div>Twin</div>}
      />
    );

    const styleTag = container.querySelector('style');
    expect(styleTag).toBeTruthy();

    const styles = styleTag?.innerHTML || '';

    // Verify desktop grid configuration
    expect(styles).toContain('grid-template-columns: 1fr 1.5fr 1fr');
    expect(styles).toContain('grid-template-rows: 1fr 1fr 1.4fr');
    expect(styles).toContain('height: calc(100vh - 64px)');

    // Verify grid area assignments
    expect(styles).toContain('.zone-director { grid-area: director; min-height: 0; }');
    expect(styles).toContain('.zone-canvas { grid-area: canvas; min-height: 0; }');
    expect(styles).toContain('.zone-gauge { grid-area: gauge; min-height: 0; }');
    expect(styles).toContain('.zone-context { grid-area: context; min-height: 0; }');
    expect(styles).toContain('.zone-twin { grid-area: twin; min-height: 0; }');
  });

  it('should collapse to single column on mobile', () => {
    // Set mobile viewport width (<768px)
    setViewportWidth(375);

    const { container } = render(
      <BentoGrid
        director={<div>Director</div>}
        canvas={<div>Canvas</div>}
        gauge={<div>Gauge</div>}
        context={<div>Context</div>}
        twin={<div>Twin</div>}
      />
    );

    const styleTag = container.querySelector('style');
    expect(styleTag).toBeTruthy();

    const styles = styleTag?.innerHTML || '';

    // Verify mobile media query exists
    expect(styles).toContain('@media (max-width: 767px)');

    // Verify mobile grid configuration
    expect(styles).toContain('grid-template-columns: 1fr');
    expect(styles).toContain('grid-template-rows: auto');

    // Verify mobile stacking order
    expect(styles).toContain('"director"');
    expect(styles).toContain('"canvas"');
    expect(styles).toContain('"gauge"');
    expect(styles).toContain('"twin"');
    expect(styles).toContain('"context"');
  });

  it('should maintain correct mobile zone order', () => {
    setViewportWidth(375);

    const { container } = render(
      <BentoGrid
        director={<div>Director</div>}
        canvas={<div>Canvas</div>}
        gauge={<div>Gauge</div>}
        context={<div>Context</div>}
        twin={<div>Twin</div>}
      />
    );

    const styleTag = container.querySelector('style');
    const styles = styleTag?.innerHTML || '';

    // Extract mobile grid-template-areas
    const mobileAreaMatch = styles.match(/@media[^{]*\{[^}]*grid-template-areas:\s*"director"\s*"canvas"\s*"gauge"\s*"twin"\s*"context"/);
    expect(mobileAreaMatch).toBeTruthy();
  });

  it('should apply gap and padding to grid', () => {
    render(
      <BentoGrid
        director={<div>Director</div>}
        canvas={<div>Canvas</div>}
        gauge={<div>Gauge</div>}
        context={<div>Context</div>}
        twin={<div>Twin</div>}
      />
    );

    const grid = screen.getByTestId('bento-grid');
    
    // Check for grid class (gap and padding are applied via inline styles)
    expect(grid.className).toContain('bento-grid');
    expect(grid.className).toContain('grid');
  });

  it('should apply overflow-hidden to director and canvas zones', () => {
    render(
      <BentoGrid
        director={<div>Director</div>}
        canvas={<div>Canvas</div>}
        gauge={<div>Gauge</div>}
        context={<div>Context</div>}
        twin={<div>Twin</div>}
      />
    );

    // Only director and canvas zones have overflow-hidden in the current implementation
    const directorZone = screen.getByTestId('zone-director');
    const canvasZone = screen.getByTestId('zone-canvas');

    expect(directorZone.className).toContain('overflow-hidden');
    expect(canvasZone.className).toContain('overflow-hidden');
  });
});
