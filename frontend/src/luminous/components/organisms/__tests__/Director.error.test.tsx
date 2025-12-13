import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Director } from '../Director';

describe('Director Error Handling', () => {
  const defaultProps = {
    sessionId: 'test-session',
    onSubmit: vi.fn(),
    isGenerating: false,
    messages: [],
  };

  it('should display error message when error prop is provided', () => {
    const error = new Error('Generation failed: Network error');
    
    render(
      <Director 
        {...defaultProps} 
        error={error}
      />
    );

    expect(screen.getByTestId('error-message')).toBeInTheDocument();
    expect(screen.getByText('Generation Failed')).toBeInTheDocument();
    expect(screen.getByText('Generation failed: Network error')).toBeInTheDocument();
  });

  it('should display retry button when onRetry is provided', () => {
    const error = new Error('Generation failed');
    const onRetry = vi.fn();
    
    render(
      <Director 
        {...defaultProps} 
        error={error}
        onRetry={onRetry}
      />
    );

    const retryButton = screen.getByTestId('retry-button');
    expect(retryButton).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('should call onRetry and onClearError when retry button is clicked', () => {
    const error = new Error('Generation failed');
    const onRetry = vi.fn();
    const onClearError = vi.fn();
    
    render(
      <Director 
        {...defaultProps} 
        error={error}
        onRetry={onRetry}
        onClearError={onClearError}
      />
    );

    const retryButton = screen.getByTestId('retry-button');
    fireEvent.click(retryButton);

    expect(onClearError).toHaveBeenCalledTimes(1);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('should call onClearError when submitting new prompt with existing error', () => {
    const error = new Error('Previous error');
    const onSubmit = vi.fn();
    const onClearError = vi.fn();
    
    render(
      <Director 
        {...defaultProps} 
        error={error}
        onSubmit={onSubmit}
        onClearError={onClearError}
      />
    );

    const input = screen.getByTestId('prompt-input');
    const submitButton = screen.getByTestId('submit-button');

    fireEvent.change(input, { target: { value: 'New prompt' } });
    fireEvent.click(submitButton);

    expect(onClearError).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith('New prompt');
  });

  it('should not display error message when error is null', () => {
    render(
      <Director 
        {...defaultProps} 
        error={null}
      />
    );

    expect(screen.queryByTestId('error-message')).not.toBeInTheDocument();
  });
});