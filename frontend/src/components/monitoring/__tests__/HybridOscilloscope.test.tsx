/**
 * Hybrid Oscilloscope Component Tests
 * 
 * Unit tests for the Hybrid Oscilloscope component that balances
 * design system integration with monitoring visibility.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import HybridOscilloscope from '../HybridOscilloscope';
import type { ComplianceScores } from '../../../types/monitoring';

describe('HybridOscilloscope', () => {
  const mockComplianceScores: ComplianceScores = {
    typography: 0.85,
    voice: 0.72,
    color: 0.91,
    logo: 0.68,
  };

  beforeEach(() => {
    // Mock requestAnimationFrame
    global.requestAnimationFrame = vi.fn((cb) => {
      setTimeout(cb, 16);
      return 1;
    });
    
    // Mock cancelAnimationFrame
    global.cancelAnimationFrame = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<HybridOscilloscope complianceScores={mockComplianceScores} />);
    
    // Check if the main container is rendered
    const oscilloscope = document.querySelector('.hybrid-oscilloscope');
    expect(oscilloscope).toBeInTheDocument();
  });

  it('displays compliance scores correctly when labels are shown', () => {
    render(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores} 
        showLabels={true}
      />
    );
    
    // Check if score percentages are displayed
    expect(screen.getByText('85%')).toBeInTheDocument(); // typography
    expect(screen.getByText('72%')).toBeInTheDocument(); // voice
    expect(screen.getByText('91%')).toBeInTheDocument(); // color
    expect(screen.getByText('68%')).toBeInTheDocument(); // logo
  });

  it('hides labels when showLabels is false', () => {
    render(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores} 
        showLabels={false}
      />
    );
    
    // Labels should not be present
    expect(screen.queryByText('TYPOGRAPHY')).not.toBeInTheDocument();
    expect(screen.queryByText('VOICE')).not.toBeInTheDocument();
    expect(screen.queryByText('COLOR')).not.toBeInTheDocument();
    expect(screen.queryByText('LOGO')).not.toBeInTheDocument();
  });

  it('renders SVG radar chart elements', () => {
    render(<HybridOscilloscope complianceScores={mockComplianceScores} />);
    
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
    
    // Check for radar grid circles
    const circles = svg?.querySelectorAll('circle');
    expect(circles?.length).toBeGreaterThan(0);
    
    // Check for radar axes lines
    const lines = svg?.querySelectorAll('line');
    expect(lines?.length).toBeGreaterThan(0);
    
    // Check for compliance polygon
    const polygon = svg?.querySelector('polygon');
    expect(polygon).toBeInTheDocument();
  });

  it('displays dimension labels when showLabels is true', () => {
    render(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores} 
        showLabels={true}
      />
    );
    
    expect(screen.getByText('TYPOGRAPHY')).toBeInTheDocument();
    expect(screen.getByText('VOICE')).toBeInTheDocument();
    expect(screen.getByText('COLOR')).toBeInTheDocument();
    expect(screen.getByText('LOGO')).toBeInTheDocument();
  });

  it('applies different sizes correctly', () => {
    const { rerender } = render(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores} 
        size="small"
      />
    );
    
    let container = document.querySelector('.hybrid-oscilloscope');
    expect(container).toHaveStyle('width: 200px');
    expect(container).toHaveStyle('height: 200px');
    
    rerender(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores} 
        size="medium"
      />
    );
    
    container = document.querySelector('.hybrid-oscilloscope');
    expect(container).toHaveStyle('width: 300px');
    expect(container).toHaveStyle('height: 300px');
    
    rerender(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores} 
        size="large"
      />
    );
    
    container = document.querySelector('.hybrid-oscilloscope');
    expect(container).toHaveStyle('width: 400px');
    expect(container).toHaveStyle('height: 400px');
  });

  it('applies different intensity levels', () => {
    const { rerender } = render(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores} 
        intensity="subtle"
      />
    );
    
    // Component should render with subtle intensity
    let container = document.querySelector('.hybrid-oscilloscope');
    expect(container).toBeInTheDocument();
    
    rerender(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores} 
        intensity="normal"
      />
    );
    
    container = document.querySelector('.hybrid-oscilloscope');
    expect(container).toBeInTheDocument();
    
    rerender(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores} 
        intensity="high"
      />
    );
    
    container = document.querySelector('.hybrid-oscilloscope');
    expect(container).toBeInTheDocument();
  });

  it('applies custom styling props', () => {
    const customClass = 'custom-hybrid-oscilloscope';
    
    render(
      <HybridOscilloscope 
        complianceScores={mockComplianceScores}
        className={customClass}
      />
    );
    
    const container = document.querySelector('.hybrid-oscilloscope');
    expect(container).toHaveClass(customClass);
    expect(container).toHaveClass('hybrid-oscilloscope');
  });

  it('displays enhanced status LED indicator', () => {
    render(<HybridOscilloscope complianceScores={mockComplianceScores} />);
    
    // Should have a status LED with led-indicator class
    const container = document.querySelector('.hybrid-oscilloscope');
    const statusLed = container?.querySelector('.led-indicator');
    expect(statusLed).toBeInTheDocument();
  });

  it('uses enhanced monitoring colors', () => {
    render(<HybridOscilloscope complianceScores={mockComplianceScores} />);
    
    const container = document.querySelector('.hybrid-oscilloscope');
    
    // Should use Tailwind bg-surface class (which maps to the industrial color)
    expect(container).toHaveClass('bg-surface');
  });

  it('includes enhanced scanline texture overlay', () => {
    render(<HybridOscilloscope complianceScores={mockComplianceScores} />);
    
    // Should have enhanced scanline texture overlay
    const overlay = document.querySelector('[style*="linear-gradient"]');
    expect(overlay).toBeInTheDocument();
  });

  it('includes outer glow effect', () => {
    render(<HybridOscilloscope complianceScores={mockComplianceScores} />);
    
    // Should have outer glow effect
    const container = document.querySelector('.hybrid-oscilloscope');
    const glowEffect = container?.querySelector('[style*="radial-gradient"]');
    expect(glowEffect).toBeInTheDocument();
  });

  it('handles zero compliance scores', () => {
    const zeroScores: ComplianceScores = {
      typography: 0,
      voice: 0,
      color: 0,
      logo: 0,
    };
    
    render(
      <HybridOscilloscope 
        complianceScores={zeroScores} 
        showLabels={true}
      />
    );
    
    // Should have multiple 0% scores (one for each dimension)
    expect(screen.getAllByText('0%')).toHaveLength(4);
    
    // Polygon should still be rendered (at center point)
    const polygon = document.querySelector('polygon');
    expect(polygon).toBeInTheDocument();
  });

  it('handles maximum compliance scores', () => {
    const maxScores: ComplianceScores = {
      typography: 1,
      voice: 1,
      color: 1,
      logo: 1,
    };
    
    render(
      <HybridOscilloscope 
        complianceScores={maxScores} 
        showLabels={true}
      />
    );
    
    expect(screen.getAllByText('100%')).toHaveLength(4);
    
    // Polygon should be at maximum radius
    const polygon = document.querySelector('polygon');
    expect(polygon).toBeInTheDocument();
  });

  it('applies sweep animation with enhanced glow', () => {
    render(<HybridOscilloscope complianceScores={mockComplianceScores} />);
    
    // Should have a sweep line with enhanced styling
    const svg = document.querySelector('svg');
    const sweepLine = svg?.querySelector('line[stroke-width="2"]');
    expect(sweepLine).toBeInTheDocument();
  });

  it('updates radar polygon when scores change', () => {
    const { rerender } = render(
      <HybridOscilloscope complianceScores={mockComplianceScores} />
    );
    
    const polygon = document.querySelector('polygon');
    const initialPoints = polygon?.getAttribute('points');
    
    // Update scores
    const newScores: ComplianceScores = {
      typography: 0.95,
      voice: 0.82,
      color: 0.71,
      logo: 0.88,
    };
    
    rerender(<HybridOscilloscope complianceScores={newScores} />);
    
    const updatedPoints = polygon?.getAttribute('points');
    expect(updatedPoints).not.toBe(initialPoints);
  });
});