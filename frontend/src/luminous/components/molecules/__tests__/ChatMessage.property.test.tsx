/**
 * Property-Based Tests for ChatMessage Component
 * 
 * These tests verify universal properties that should hold across all valid inputs
 * using fast-check for property-based testing.
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { render } from '@testing-library/react';
import { ChatMessage } from '../ChatMessage';

describe('ChatMessage - Property-Based Tests', () => {
  /**
   * Feature: luminous-dashboard-v2, Property 2: Chat Message Rendering Completeness
   * 
   * For any list of chat messages, all messages should be rendered in the DOM with 
   * correct role-based alignment (user messages right-aligned, system messages left-aligned).
   * 
   * Validates: Requirements 4.1, 4.2
   */
  it('should render all messages with correct role-based alignment for any message list', () => {
    fc.assert(
      fc.property(
        // Generate an array of chat messages with random roles, content, and timestamps
        fc.array(
          fc.record({
            role: fc.constantFrom('user', 'system'),
            content: fc.string({ minLength: 1, maxLength: 500 }),
            timestamp: fc.date({ min: new Date('2020-01-01'), max: new Date('2025-12-31') }),
          }),
          { minLength: 1, maxLength: 20 } // Test with 1-20 messages
        ),
        (messages) => {
          // Render all messages
          const { container } = render(
            <div>
              {messages.map((msg, index) => (
                <ChatMessage
                  key={index}
                  role={msg.role}
                  content={msg.content}
                  timestamp={msg.timestamp}
                />
              ))}
            </div>
          );

          // Get all rendered message containers
          const messageContainers = container.querySelectorAll('[data-testid="chat-message"]');

          // Property 1: All messages should be rendered (completeness)
          expect(messageContainers.length).toBe(messages.length);

          // Property 2: Each message should have correct alignment based on role
          messageContainers.forEach((messageContainer, index) => {
            const expectedRole = messages[index].role;
            const actualRole = messageContainer.getAttribute('data-role');

            // Verify role attribute matches
            expect(actualRole).toBe(expectedRole);

            // Verify alignment class matches role
            if (expectedRole === 'user') {
              expect(messageContainer).toHaveClass('justify-end');
              expect(messageContainer).not.toHaveClass('justify-start');
            } else {
              expect(messageContainer).toHaveClass('justify-start');
              expect(messageContainer).not.toHaveClass('justify-end');
            }
          });

          // Property 3: Each message should contain its content
          messageContainers.forEach((messageContainer, index) => {
            const expectedContent = messages[index].content;
            expect(messageContainer.textContent).toContain(expectedContent);
          });
        }
      ),
      { numRuns: 100 } // Run 100 iterations as specified in design doc
    );
  });

  /**
   * Feature: luminous-dashboard-v2, Property 2 (Styling Consistency)
   * 
   * For any message role, the styling should be consistent:
   * - User messages: purple tint background
   * - System messages: neutral glass background
   * 
   * Validates: Requirements 4.2
   */
  it('should apply consistent styling based on role for any message', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('user', 'system'),
        fc.string({ minLength: 1, maxLength: 200 }),
        fc.date(),
        (role, content, timestamp) => {
          const { container } = render(
            <ChatMessage
              role={role}
              content={content}
              timestamp={timestamp}
            />
          );

          const messageContainer = container.querySelector('[data-testid="chat-message"]');
          expect(messageContainer).toBeInTheDocument();

          // Verify correct background styling based on role
          if (role === 'user') {
            const purpleBackground = container.querySelector('.bg-purple-500\\/10');
            expect(purpleBackground).toBeInTheDocument();
            
            // Should NOT have system message styling
            const glassBackground = container.querySelector('.bg-white\\/5');
            expect(glassBackground).not.toBeInTheDocument();
          } else {
            const glassBackground = container.querySelector('.bg-white\\/5');
            expect(glassBackground).toBeInTheDocument();
            
            // Should NOT have user message styling
            const purpleBackground = container.querySelector('.bg-purple-500\\/10');
            expect(purpleBackground).not.toBeInTheDocument();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Feature: luminous-dashboard-v2, Property 2 (Content Preservation)
   * 
   * For any message content, the rendered message should preserve the exact content
   * without modification or truncation.
   * 
   * Validates: Requirements 4.1
   */
  it('should preserve exact message content for any input string', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('user', 'system'),
        fc.string({ minLength: 1, maxLength: 1000 }),
        fc.date(),
        (role, content, timestamp) => {
          const { container } = render(
            <ChatMessage
              role={role}
              content={content}
              timestamp={timestamp}
            />
          );

          // Find the content paragraph element
          const messageContainer = container.querySelector('[data-testid="chat-message"]');
          const contentParagraph = messageContainer?.querySelector('p.text-sm');

          // Verify content is preserved exactly
          expect(contentParagraph?.textContent).toBe(content);
        }
      ),
      { numRuns: 100 }
    );
  });
});
