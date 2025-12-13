import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TwinData } from '../TwinData';

describe('TwinData', () => {
  const mockDetectedColors = ['#2664EC', '#10B981', '#F59E0B'];
  const mockBrandColors = ['#2563EB', '#10B981', '#F59E0B'];
  const mockDetectedFonts = [
    { family: 'Inter', weight: 'Bold', allowed: true },
    { family: 'Comic Sans', weight: 'Regular', allowed: false },
    { family: 'JetBrains Mono', weight: 'Medium', allowed: true },
  ];

  it('renders the component with header', () => {
    render(
      <TwinData
        detectedColors={mockDetectedColors}
        brandColors={mockBrandColors}
        detectedFonts={mockDetectedFonts}
      />
    );

    expect(screen.getByTestId('twin-data')).toBeInTheDocument();
    expect(screen.getByText('Compressed Digital Twin')).toBeInTheDocument();
    expect(screen.getByText('Detected visual tokens')).toBeInTheDocument();
  });

  it('renders color section header', () => {
    render(
      <TwinData
        detectedColors={mockDetectedColors}
        brandColors={mockBrandColors}
        detectedFonts={mockDetectedFonts}
      />
    );

    expect(screen.getByText('Colors')).toBeInTheDocument();
  });

  it('renders fonts section header', () => {
    render(
      <TwinData
        detectedColors={mockDetectedColors}
        brandColors={mockBrandColors}
        detectedFonts={mockDetectedFonts}
      />
    );

    expect(screen.getByText('Fonts')).toBeInTheDocument();
  });

  it('renders color swatches for detected colors', () => {
    render(
      <TwinData
        detectedColors={mockDetectedColors}
        brandColors={mockBrandColors}
        detectedFonts={mockDetectedFonts}
      />
    );

    const colorSwatches = screen.getAllByTestId('color-swatch');
    expect(colorSwatches).toHaveLength(mockDetectedColors.length);
  });

  it('renders font items with family and weight', () => {
    render(
      <TwinData
        detectedColors={mockDetectedColors}
        brandColors={mockBrandColors}
        detectedFonts={mockDetectedFonts}
      />
    );

    expect(screen.getByText('Inter-Bold')).toBeInTheDocument();
    expect(screen.getByText('Comic Sans-Regular')).toBeInTheDocument();
    expect(screen.getByText('JetBrains Mono-Medium')).toBeInTheDocument();
  });

  it('displays correct compliance status for allowed fonts', () => {
    render(
      <TwinData
        detectedColors={mockDetectedColors}
        brandColors={mockBrandColors}
        detectedFonts={mockDetectedFonts}
      />
    );

    const complianceStatuses = screen.getAllByTestId('font-compliance-status');
    
    // First font (Inter-Bold) should be allowed
    expect(complianceStatuses[0]).toHaveTextContent('(Allowed)');
    
    // Second font (Comic Sans) should be forbidden
    expect(complianceStatuses[1]).toHaveTextContent('(Forbidden)');
    
    // Third font (JetBrains Mono) should be allowed
    expect(complianceStatuses[2]).toHaveTextContent('(Allowed)');
  });

  it('displays "No colors detected" when colors array is empty', () => {
    render(
      <TwinData
        detectedColors={[]}
        brandColors={mockBrandColors}
        detectedFonts={mockDetectedFonts}
      />
    );

    expect(screen.getByText('No colors detected')).toBeInTheDocument();
  });

  it('displays "No fonts detected" when fonts array is empty', () => {
    render(
      <TwinData
        detectedColors={mockDetectedColors}
        brandColors={mockBrandColors}
        detectedFonts={[]}
      />
    );

    expect(screen.getByText('No fonts detected')).toBeInTheDocument();
  });

  it('renders all font items', () => {
    render(
      <TwinData
        detectedColors={mockDetectedColors}
        brandColors={mockBrandColors}
        detectedFonts={mockDetectedFonts}
      />
    );

    const fontItems = screen.getAllByTestId('font-item');
    expect(fontItems).toHaveLength(mockDetectedFonts.length);
  });

  it('handles empty arrays gracefully', () => {
    render(
      <TwinData
        detectedColors={[]}
        brandColors={[]}
        detectedFonts={[]}
      />
    );

    expect(screen.getByText('No colors detected')).toBeInTheDocument();
    expect(screen.getByText('No fonts detected')).toBeInTheDocument();
  });
});
