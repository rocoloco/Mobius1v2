/**
 * Unit Test: Director Component
 * 
 * Tests the Director organism component to verify:
 * - Chat history renders correctly
 * - Quick action chips are present and functional
 * - Input field enforces character limit
 * - Submit callback is triggered correctly
 * - Generating status indicator displays when isGenerating is true
 * 
 * Validates: Requirements 4.1-4.11
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Director } from '../Director';

describe('Director Component', () => {
  const mockOnSubmit = vi.fn();
  const defaultProps = {
    sessionId: 'test-session-123',
    onSubmit: mockOnSubmit,
    isGenerating: false,
  };

  beforeEach(() => {
    mockOnSubmit.mockClear();
    
    // Mock scrollIntoView for JSDOM
    Element.prototype.scrollIntoView = vi.fn();
  });

  it('should render the Director component', () => {
    render(<Director {...defaultProps} />);
    
    const director = screen.getByTestId('director');
    expect(director).toBeTruthy();
  });

  it('should display empty state message when no messages', () => {
    render(<Director {...defaultProps} />);
    
    expect(screen.getByText('Start a conversation to generate brand assets')).toBeTruthy();
  });

  it('should render chat messages when provided', () => {
    const messages = [
      {
        role: 'user' as const,
        content: 'Create a logo',
        timestamp: new Date('2024-01-01T10:00:00'),
      },
      {
        role: 'system' as const,
        content: 'Generating your logo...',
        timestamp: new Date('2024-01-01T10:00:05'),
      },
    ];

    render(<Director {...defaultProps} messages={messages} />);
    
    expect(screen.getByText('Create a logo')).toBeTruthy();
    expect(screen.getByText('Generating your logo...')).toBeTruthy();
  });

  it('should render Quick Action chips', () => {
    render(<Director {...defaultProps} />);
    
    expect(screen.getByTestId('quick-action-fix-red')).toBeTruthy();
    expect(screen.getByTestId('quick-action-make-witty')).toBeTruthy();
    expect(screen.getByText('Fix Red Violations')).toBeTruthy();
    expect(screen.getByText('Make it Witty')).toBeTruthy();
  });

  it('should populate input field when Quick Action is clicked', () => {
    render(<Director {...defaultProps} />);
    
    const quickActionButton = screen.getByTestId('quick-action-fix-red');
    fireEvent.click(quickActionButton);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    expect(input.value).toBe('Please fix all critical violations marked in red');
  });

  it('should render input field with placeholder', () => {
    render(<Director {...defaultProps} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    expect(input.placeholder).toBe('Describe the asset you want to generate...');
  });

  it('should display character counter', () => {
    render(<Director {...defaultProps} />);
    
    const counter = screen.getByTestId('character-counter');
    expect(counter.textContent).toBe('0 / 1000');
  });

  it('should update character counter as user types', () => {
    render(<Director {...defaultProps} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    fireEvent.change(input, { target: { value: 'Hello world' } });
    
    const counter = screen.getByTestId('character-counter');
    expect(counter.textContent).toBe('11 / 1000');
  });

  it('should enforce 1000 character limit', () => {
    render(<Director {...defaultProps} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    
    // First add text up to the limit
    const limitText = 'a'.repeat(1000);
    fireEvent.change(input, { target: { value: limitText } });
    expect(input.value.length).toBe(1000);
    
    // Try to add more text - should be rejected
    const overLimitText = 'a'.repeat(1100);
    fireEvent.change(input, { target: { value: overLimitText } });
    
    // Should still be capped at 1000 (the component prevents values > 1000)
    expect(input.value.length).toBeLessThanOrEqual(1000);
  });

  it('should display warning when approaching character limit', () => {
    render(<Director {...defaultProps} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    const nearLimitText = 'a'.repeat(950);
    
    fireEvent.change(input, { target: { value: nearLimitText } });
    
    expect(screen.getByText('Approaching character limit')).toBeTruthy();
  });

  it('should render submit button', () => {
    render(<Director {...defaultProps} />);
    
    const submitButton = screen.getByTestId('submit-button');
    expect(submitButton).toBeTruthy();
    expect(submitButton.getAttribute('aria-label')).toBe('Send message');
  });

  it('should disable submit button when input is empty', () => {
    render(<Director {...defaultProps} />);
    
    const submitButton = screen.getByTestId('submit-button') as HTMLButtonElement;
    expect(submitButton.disabled).toBe(true);
  });

  it('should enable submit button when input has text', () => {
    render(<Director {...defaultProps} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    fireEvent.change(input, { target: { value: 'Create a logo' } });
    
    const submitButton = screen.getByTestId('submit-button') as HTMLButtonElement;
    expect(submitButton.disabled).toBe(false);
  });

  it('should call onSubmit when submit button is clicked', () => {
    render(<Director {...defaultProps} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    fireEvent.change(input, { target: { value: 'Create a logo' } });
    
    const submitButton = screen.getByTestId('submit-button');
    fireEvent.click(submitButton);
    
    expect(mockOnSubmit).toHaveBeenCalledWith('Create a logo');
  });

  it('should clear input after submission', () => {
    render(<Director {...defaultProps} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    fireEvent.change(input, { target: { value: 'Create a logo' } });
    
    const submitButton = screen.getByTestId('submit-button');
    fireEvent.click(submitButton);
    
    expect(input.value).toBe('');
  });

  it('should trim whitespace from input before submission', () => {
    render(<Director {...defaultProps} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    fireEvent.change(input, { target: { value: '  Create a logo  ' } });
    
    const submitButton = screen.getByTestId('submit-button');
    fireEvent.click(submitButton);
    
    expect(mockOnSubmit).toHaveBeenCalledWith('Create a logo');
  });

  it('should not submit when input is only whitespace', () => {
    render(<Director {...defaultProps} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    fireEvent.change(input, { target: { value: '   ' } });
    
    const submitButton = screen.getByTestId('submit-button');
    fireEvent.click(submitButton);
    
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('should display generating status when isGenerating is true', () => {
    render(<Director {...defaultProps} isGenerating={true} />);
    
    const status = screen.getByTestId('generating-status');
    expect(status).toBeTruthy();
    expect(screen.getByText('Gemini 3 Pro - Thinking...')).toBeTruthy();
  });

  it('should not display generating status when isGenerating is false', () => {
    render(<Director {...defaultProps} isGenerating={false} />);
    
    const status = screen.queryByTestId('generating-status');
    expect(status).toBeNull();
  });

  it('should disable input and buttons when isGenerating is true', () => {
    render(<Director {...defaultProps} isGenerating={true} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    const submitButton = screen.getByTestId('submit-button') as HTMLButtonElement;
    const quickActionButton = screen.getByTestId('quick-action-fix-red') as HTMLButtonElement;
    
    expect(input.disabled).toBe(true);
    expect(submitButton.disabled).toBe(true);
    expect(quickActionButton.disabled).toBe(true);
  });

  it('should not call onSubmit when isGenerating is true', () => {
    render(<Director {...defaultProps} isGenerating={true} />);
    
    const input = screen.getByTestId('prompt-input') as HTMLTextAreaElement;
    fireEvent.change(input, { target: { value: 'Create a logo' } });
    
    const submitButton = screen.getByTestId('submit-button');
    fireEvent.click(submitButton);
    
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('should apply glassmorphism styling', () => {
    render(<Director {...defaultProps} />);
    
    const director = screen.getByTestId('director');
    
    expect(director.className).toContain('bg-white/5');
    expect(director.className).toContain('backdrop-blur-md');
    expect(director.className).toContain('border');
    expect(director.className).toContain('border-white/10');
    expect(director.className).toContain('rounded-2xl');
  });
});
