import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Toast } from '../Toast';

describe('Toast Component', () => {
  const defaultProps = {
    type: 'success' as const,
    message: 'Test message',
    onClose: vi.fn(),
  };

  it('should render toast with correct message', () => {
    render(<Toast {...defaultProps} />);
    
    expect(screen.getByTestId('toast')).toBeInTheDocument();
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  it('should render success toast with correct styling', () => {
    render(<Toast {...defaultProps} type="success" />);
    
    const toast = screen.getByTestId('toast');
    expect(toast).toHaveAttribute('data-type', 'success');
  });

  it('should render warning toast with correct styling', () => {
    render(<Toast {...defaultProps} type="warning" />);
    
    const toast = screen.getByTestId('toast');
    expect(toast).toHaveAttribute('data-type', 'warning');
  });

  it('should render error toast with correct styling', () => {
    render(<Toast {...defaultProps} type="error" />);
    
    const toast = screen.getByTestId('toast');
    expect(toast).toHaveAttribute('data-type', 'error');
  });

  it('should call onClose when close button is clicked', async () => {
    const onClose = vi.fn();
    render(<Toast {...defaultProps} onClose={onClose} />);
    
    const closeButton = screen.getByLabelText('Close notification');
    fireEvent.click(closeButton);
    
    // Wait for animation delay (300ms)
    await new Promise(resolve => setTimeout(resolve, 350));
    
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});