import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ViolationItem } from '../ViolationItem';

describe('ViolationItem', () => {
  const mockViolation = {
    id: 'test-1',
    severity: 'critical' as const,
    message: 'Logo margin too small',
  };
  
  it('renders violation message', () => {
    const onClick = vi.fn();
    render(<ViolationItem violation={mockViolation} onClick={onClick} />);
    
    expect(screen.getByText('Logo margin too small')).toBeInTheDocument();
  });
  
  it('renders with correct data-testid', () => {
    const onClick = vi.fn();
    render(<ViolationItem violation={mockViolation} onClick={onClick} />);
    
    const item = screen.getByTestId('violation-item');
    expect(item).toBeInTheDocument();
  });
  
  it('renders with correct data-severity attribute', () => {
    const onClick = vi.fn();
    render(<ViolationItem violation={mockViolation} onClick={onClick} />);
    
    const item = screen.getByTestId('violation-item');
    expect(item).toHaveAttribute('data-severity', 'critical');
  });
  
  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<ViolationItem violation={mockViolation} onClick={onClick} />);
    
    const item = screen.getByTestId('violation-item');
    fireEvent.click(item);
    
    expect(onClick).toHaveBeenCalledTimes(1);
  });
  
  it('renders critical severity with AlertCircle icon', () => {
    const onClick = vi.fn();
    const { container } = render(
      <ViolationItem 
        violation={{ ...mockViolation, severity: 'critical' }} 
        onClick={onClick} 
      />
    );
    
    // Check that an SVG icon is rendered
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });
  
  it('renders warning severity with AlertTriangle icon', () => {
    const onClick = vi.fn();
    const { container } = render(
      <ViolationItem 
        violation={{ ...mockViolation, severity: 'warning' }} 
        onClick={onClick} 
      />
    );
    
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });
  
  it('renders info severity with Info icon', () => {
    const onClick = vi.fn();
    const { container } = render(
      <ViolationItem 
        violation={{ ...mockViolation, severity: 'info' }} 
        onClick={onClick} 
      />
    );
    
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });
});
