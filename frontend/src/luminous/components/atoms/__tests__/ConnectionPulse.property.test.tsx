/**
 * Property-Based Test: ConnectionPulse Color Mapping
 * 
 * **Feature: luminous-dashboard-v2, Property 1: Connection Status Indicator Correctness**
 * **Validates: Requirements 2.5, 2.6**
 * 
 * Tests that the ConnectionPulse component correctly displays the appropriate
 * color for each connection status: green for connected, red for disconnected,
 * and yellow for connecting.
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { render } from '@testing-library/react';
import { ConnectionPulse } from '../ConnectionPulse';

describe('Property Test: ConnectionPulse Color Mapping', () => {
  /**
   * Property 1: Connection Status Indicator Correctness
   * For any connection status value ('connected', 'disconnected', 'connecting'),
   * the connection pulse dot should display the correct color:
   * - green (bg-green-500) for connected
   * - red (bg-red-500) for disconnected
   * - yellow (bg-yellow-500) for connecting
   */
  it('should display correct color for any connection status', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('connected', 'disconnected', 'connecting'),
        (status: 'connected' | 'disconnected' | 'connecting') => {
          // Render the ConnectionPulse with the generated status
          const { container } = render(<ConnectionPulse status={status} />);
          
          // Get the pulse element
          const pulseElement = container.querySelector('[data-testid="connection-pulse"]') as HTMLElement;
          
          // Verify the element exists
          expect(pulseElement).toBeTruthy();
          
          // Determine the expected color class based on status
          const expectedColorClass = status === 'connected' ? 'bg-green-500'
            : status === 'disconnected' ? 'bg-red-500'
            : 'bg-yellow-500';
          
          // Verify the correct color class is applied
          expect(pulseElement.className).toContain(expectedColorClass);
          
          // Verify the element has the correct base styling
          expect(pulseElement.className).toContain('w-2');
          expect(pulseElement.className).toContain('h-2');
          expect(pulseElement.className).toContain('rounded-full');
          
          // Verify pulse animation is applied for connected and connecting states
          if (status === 'connected' || status === 'connecting') {
            expect(pulseElement.className).toContain('animate-pulse');
          } else {
            // Disconnected should not have pulse animation
            expect(pulseElement.className).not.toContain('animate-pulse');
          }
          
          // Verify accessibility attributes
          expect(pulseElement.getAttribute('role')).toBe('status');
          expect(pulseElement.getAttribute('aria-label')).toContain(status);
          
          return true;
        }
      ),
      { numRuns: 100 } // Run 100 iterations as specified in design document
    );
  });

  /**
   * Additional property test: Pulse animation consistency
   * For any status that should pulse (connected, connecting), verify the animation
   * is consistently applied, and for disconnected, verify it's consistently absent.
   */
  it('should consistently apply pulse animation based on connection state', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('connected', 'disconnected', 'connecting'),
        (status: 'connected' | 'disconnected' | 'connecting') => {
          const { container } = render(<ConnectionPulse status={status} />);
          const pulseElement = container.querySelector('[data-testid="connection-pulse"]') as HTMLElement;
          
          const shouldPulse = status === 'connected' || status === 'connecting';
          const hasPulseClass = pulseElement.className.includes('animate-pulse');
          
          // The pulse animation should match the expected behavior
          expect(hasPulseClass).toBe(shouldPulse);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Additional property test: Aria-label correctness
   * For any connection status, the aria-label should accurately describe the status
   */
  it('should have correct aria-label for any connection status', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('connected', 'disconnected', 'connecting'),
        (status: 'connected' | 'disconnected' | 'connecting') => {
          const { container } = render(<ConnectionPulse status={status} />);
          const pulseElement = container.querySelector('[data-testid="connection-pulse"]') as HTMLElement;
          
          const ariaLabel = pulseElement.getAttribute('aria-label');
          
          // Aria-label should contain the status
          expect(ariaLabel).toContain(status);
          expect(ariaLabel).toContain('Connection status');
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});
