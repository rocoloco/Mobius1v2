import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ColorSwatch } from '../ColorSwatch';

describe('ColorSwatch', () => {
  it('renders with detected and brand colors', () => {
    render(
      <ColorSwatch
        detected="#2664EC"
        brand="#2563EB"
        distance={1.2}
        pass={true}
      />
    );
    
    const swatch = screen.getByTestId('color-swatch');
    expect(swatch).toBeInTheDocument();
  });
  
  it('displays hex codes in uppercase', () => {
    render(
      <ColorSwatch
        detected="#2664ec"
        brand="#2563eb"
        distance={1.2}
        pass={true}
      />
    );
    
    expect(screen.getByText('#2664EC')).toBeInTheDocument();
    expect(screen.getByText('#2563EB')).toBeInTheDocument();
  });
  
  it('renders color dots with correct background colors', () => {
    render(
      <ColorSwatch
        detected="#FF0000"
        brand="#00FF00"
        distance={50.0}
        pass={false}
      />
    );
    
    const detectedDot = screen.getByTestId('detected-color-dot');
    const brandDot = screen.getByTestId('brand-color-dot');
    
    expect(detectedDot).toHaveStyle({ backgroundColor: '#FF0000' });
    expect(brandDot).toHaveStyle({ backgroundColor: '#00FF00' });
  });
  
  it('displays tooltip with distance and pass status', () => {
    render(
      <ColorSwatch
        detected="#2664EC"
        brand="#2563EB"
        distance={1.2}
        pass={true}
      />
    );
    
    const swatch = screen.getByTestId('color-swatch');
    expect(swatch).toHaveAttribute('title', 'Distance: 1.2 (Pass)');
  });
  
  it('displays fail status in tooltip when pass is false', () => {
    render(
      <ColorSwatch
        detected="#FF0000"
        brand="#00FF00"
        distance={50.0}
        pass={false}
      />
    );
    
    const swatch = screen.getByTestId('color-swatch');
    expect(swatch).toHaveAttribute('title', 'Distance: 50.0 (Fail)');
  });
  
  it('formats distance to one decimal place', () => {
    render(
      <ColorSwatch
        detected="#2664EC"
        brand="#2563EB"
        distance={1.23456}
        pass={true}
      />
    );
    
    const swatch = screen.getByTestId('color-swatch');
    expect(swatch).toHaveAttribute('title', 'Distance: 1.2 (Pass)');
  });
});
