import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ConstraintCard } from '../ConstraintCard';
import { Linkedin, EyeOff, Mic } from 'lucide-react';

describe('ConstraintCard', () => {
  it('renders label text', () => {
    render(
      <ConstraintCard
        type="channel"
        label="LinkedIn Professional"
        icon={<Linkedin className="w-5 h-5" />}
      />
    );
    
    expect(screen.getByText('LinkedIn Professional')).toBeInTheDocument();
  });
  
  it('renders with correct data-testid', () => {
    render(
      <ConstraintCard
        type="channel"
        label="Test Constraint"
        icon={<Linkedin className="w-5 h-5" />}
      />
    );
    
    const card = screen.getByTestId('constraint-card');
    expect(card).toBeInTheDocument();
  });
  
  it('renders with correct data-type attribute', () => {
    render(
      <ConstraintCard
        type="negative"
        label="Test Constraint"
        icon={<EyeOff className="w-5 h-5" />}
      />
    );
    
    const card = screen.getByTestId('constraint-card');
    expect(card).toHaveAttribute('data-type', 'negative');
  });
  
  it('renders with data-active=false by default', () => {
    render(
      <ConstraintCard
        type="channel"
        label="Test Constraint"
        icon={<Linkedin className="w-5 h-5" />}
      />
    );
    
    const card = screen.getByTestId('constraint-card');
    expect(card).toHaveAttribute('data-active', 'false');
  });
  
  it('renders with data-active=true when active prop is true', () => {
    render(
      <ConstraintCard
        type="channel"
        label="Test Constraint"
        icon={<Linkedin className="w-5 h-5" />}
        active={true}
      />
    );
    
    const card = screen.getByTestId('constraint-card');
    expect(card).toHaveAttribute('data-active', 'true');
  });
  
  it('renders icon', () => {
    const { container } = render(
      <ConstraintCard
        type="channel"
        label="Test Constraint"
        icon={<Linkedin className="w-5 h-5" data-testid="test-icon" />}
      />
    );
    
    // Check that an SVG icon is rendered
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });
  
  it('renders radar chart for voice constraints with voiceVectors', () => {
    const { container } = render(
      <ConstraintCard
        type="voice"
        label="Brand Voice"
        icon={<Mic className="w-5 h-5" />}
        metadata={{
          voiceVectors: {
            formal: 0.8,
            witty: 0.3,
            technical: 0.6,
            urgent: 0.2,
          },
        }}
      />
    );
    
    // Check that multiple SVGs are rendered (icon + radar chart)
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBeGreaterThan(1);
  });
  
  it('does not render radar chart for non-voice constraints', () => {
    const { container } = render(
      <ConstraintCard
        type="channel"
        label="LinkedIn"
        icon={<Linkedin className="w-5 h-5" />}
      />
    );
    
    // Should only have one SVG (the icon)
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBe(1);
  });
  
  it('does not render radar chart for voice constraints without voiceVectors', () => {
    const { container } = render(
      <ConstraintCard
        type="voice"
        label="Brand Voice"
        icon={<Mic className="w-5 h-5" />}
      />
    );
    
    // Should only have one SVG (the icon)
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBe(1);
  });
});
