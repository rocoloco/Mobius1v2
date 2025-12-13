import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ChatMessage } from '../ChatMessage';

describe('ChatMessage', () => {
  const mockTimestamp = new Date('2024-01-15T10:30:00');

  it('renders user message with correct alignment', () => {
    const { container } = render(
      <ChatMessage
        role="user"
        content="Generate a logo for my brand"
        timestamp={mockTimestamp}
      />
    );

    const messageContainer = container.querySelector('[data-testid="chat-message"]');
    expect(messageContainer).toHaveClass('justify-end');
    expect(messageContainer?.getAttribute('data-role')).toBe('user');
  });

  it('renders system message with correct alignment', () => {
    const { container } = render(
      <ChatMessage
        role="system"
        content="I'll create a logo for you"
        timestamp={mockTimestamp}
      />
    );

    const messageContainer = container.querySelector('[data-testid="chat-message"]');
    expect(messageContainer).toHaveClass('justify-start');
    expect(messageContainer?.getAttribute('data-role')).toBe('system');
  });

  it('displays message content', () => {
    const content = 'Test message content';
    render(
      <ChatMessage
        role="user"
        content={content}
        timestamp={mockTimestamp}
      />
    );

    expect(screen.getByText(content)).toBeInTheDocument();
  });

  it('displays formatted timestamp', () => {
    render(
      <ChatMessage
        role="user"
        content="Test message"
        timestamp={mockTimestamp}
      />
    );

    // Timestamp should be formatted as HH:MM
    expect(screen.getByText('10:30')).toBeInTheDocument();
  });

  it('applies purple tint background for user messages', () => {
    const { container } = render(
      <ChatMessage
        role="user"
        content="User message"
        timestamp={mockTimestamp}
      />
    );

    const messageBox = container.querySelector('.bg-purple-500\\/10');
    expect(messageBox).toBeInTheDocument();
  });

  it('applies neutral glass background for system messages', () => {
    const { container } = render(
      <ChatMessage
        role="system"
        content="System message"
        timestamp={mockTimestamp}
      />
    );

    const messageBox = container.querySelector('.bg-white\\/5');
    expect(messageBox).toBeInTheDocument();
  });
});
