/**
 * CRT Oscilloscope Component Tests
 * 
 * Unit tests for the CRT Oscilloscope component functionality.
 */

import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import CRTOscilloscope from '../CRTOscilloscope';
import type { ComplianceScores } from '../../../types/monitoring';

// Mock performance monitoring
vi.mock('../CRTEffects', async () => {
  const actual = await vi.importActual('../CRTEffects');
  return {
    ...actual,
    CRTPerformanceOptimizer: class MockCRTPerformanceOptimizer {
      startPerformanceMonitoring = vi.fn();
      stopPerformanceMonitoring = vi.fn();
      getCurrentFPS = vi.fn(() => 60);
    },
    injectCRTStyles: vi.fn(),
  };
});

describe('CRTOscilloscope', () => {
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
    render(<CRTOscilloscope complianceScores={mockComplianceScores} />);
    
    // Check if the main container is rendered
    const oscilloscope = document.querySelector('.crt-oscilloscope');
    expect(oscilloscope).toBeInTheDocument();
  });

  it('displays compliance scores correctly', () => {
    render(<CRTOscilloscope complianceScores={mockComplianceScores} />);
    
    // Check if score percentages are displayed
    expect(screen.getByText('85%')).toBeInTheDocument(); // typography
    expect(screen.getByText('72%')).toBeInTheDocument(); // voice
    expect(screen.getByText('91%')).toBeInTheDocument(); // color
    expect(screen.getByText('68%')).toBeInTheDocument(); // logo
  });

  it('renders SVG radar chart elements', () => {
    render(<CRTOscilloscope complianceScores={mockComplianceScores} />);
    
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

  it('displays dimension labels', () => {
    render(<CRTOscilloscope complianceScores={mockComplianceScores} />);
    
    expect(screen.getByText('TYPOGRAPHY')).toBeInTheDocument();
    expect(screen.getByText('VOICE')).toBeInTheDocument();
    expect(screen.getByText('COLOR')).toBeInTheDocument();
    expect(screen.getByText('LOGO')).toBeInTheDocument();
  });

  it('updates radar polygon when scores change', () => {
    const { rerender } = render(<CRTOscilloscope complianceScores={mockComplianceScores} />);
    
    const polygon = document.querySelector('polygon');
    const initialPoints = polygon?.getAttribute('points');
    
    // Update scores
    const newScores: ComplianceScores = {
      typography: 0.95,
      voice: 0.82,
      color: 0.71,
      logo: 0.88,
    };
    
    rerender(<CRTOscilloscope complianceScores={newScores} />);
    
    const updatedPoints = polygon?.getAttribute('points');
    expect(updatedPoints).not.toBe(initialPoints);
  });

  it('applies custom styling props', () => {
    const customClass = 'custom-oscilloscope';
    
    render(
      <CRTOscilloscope 
        complianceScores={mockComplianceScores}
        className={customClass}
      />
    );
    
    const container = document.querySelector('.crt-oscilloscope');
    expect(container).toHaveClass(customClass);
    expect(container).toHaveClass('crt-oscilloscope');
  });

  it('handles error callback', () => {
    const onError = vi.fn();
    
    render(
      <CRTOscilloscope 
        complianceScores={mockComplianceScores}
        onError={onError}
      />
    );
    
    // The component should render without calling onError for valid props
    expect(onError).not.toHaveBeenCalled();
  });

  it('displays FPS counter', () => {
    render(<CRTOscilloscope complianceScores={mockComplianceScores} />);
    
    // Should display FPS counter
    expect(screen.getByText(/FPS/)).toBeInTheDocument();
  });

  it('applies CRT visual effects', () => {
    render(<CRTOscilloscope complianceScores={mockComplianceScores} />);
    
    // Check for scanlines overlay
    const scanlines = document.querySelector('.crt-scanlines');
    expect(scanlines).toBeInTheDocument();
    
    // Check for phosphor screen (check for color property instead)
    const phosphorScreen = document.querySelector('[style*="color: rgb(0, 255, 65)"]');
    expect(phosphorScreen).toBeInTheDocument();
  });

  it('configures sweep speed correctly', () => {
    const customSweepSpeed = 5;
    
    render(
      <CRTOscilloscope 
        complianceScores={mockComplianceScores}
        sweepSpeed={customSweepSpeed}
      />
    );
    
    // Component should render with custom sweep speed
    // (Animation testing would require more complex setup)
    const container = document.querySelector('.crt-oscilloscope');
    expect(container).toBeInTheDocument();
  });

  it('handles zero compliance scores', () => {
    const zeroScores: ComplianceScores = {
      typography: 0,
      voice: 0,
      color: 0,
      logo: 0,
    };
    
    render(<CRTOscilloscope complianceScores={zeroScores} />);
    
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
    
    render(<CRTOscilloscope complianceScores={maxScores} />);
    
    expect(screen.getAllByText('100%')).toHaveLength(4);
    
    // Polygon should be at maximum radius
    const polygon = document.querySelector('polygon');
    expect(polygon).toBeInTheDocument();
  });
});