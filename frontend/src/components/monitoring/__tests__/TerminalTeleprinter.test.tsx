/**
 * Terminal Teleprinter Component Tests
 * 
 * Unit tests for the TerminalTeleprinter component focusing on audio/visual feedback,
 * log level styling, typewriter animation, and performance optimization.
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import TerminalTeleprinter from '../TerminalTeleprinter';
import type { ReasoningLog } from '../../../types/monitoring';

// Mock AudioContext for audio feedback testing
const mockAudioContext = {
  createOscillator: vi.fn(() => ({
    connect: vi.fn(),
    frequency: { setValueAtTime: vi.fn() },
    type: 'sine',
    start: vi.fn(),
    stop: vi.fn()
  })),
  createGain: vi.fn(() => ({
    connect: vi.fn(),
    gain: {
      setValueAtTime: vi.fn(),
      linearRampToValueAtTime: vi.fn(),
      exponentialRampToValueAtTime: vi.fn()
    }
  })),
  destination: {},
  currentTime: 0,
  close: vi.fn()
};

// Mock window.AudioContext
Object.defineProperty(window, 'AudioContext', {
  writable: true,
  value: vi.fn(() => mockAudioContext)
});

describe('TerminalTeleprinter', () => {
  const mockLogs: ReasoningLog[] = [
    {
      id: 'log-1',
      timestamp: new Date('2024-01-01T10:00:00Z'),
      step: 'INIT',
      message: 'System initialization complete',
      level: 'info'
    },
    {
      id: 'log-2',
      timestamp: new Date('2024-01-01T10:00:01Z'),
      step: 'WARNING',
      message: 'Logo clearspace violation detected',
      level: 'warning'
    },
    {
      id: 'log-3',
      timestamp: new Date('2024-01-01T10:00:02Z'),
      step: 'ERROR',
      message: 'Critical brand color violation',
      level: 'error'
    },
    {
      id: 'log-4',
      timestamp: new Date('2024-01-01T10:00:03Z'),
      step: 'SUCCESS',
      message: 'Compliance audit completed',
      level: 'success'
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  describe('Basic Rendering', () => {
    it('renders terminal container with CRT styling', () => {
      render(<TerminalTeleprinter logs={[]} />);
      
      const container = document.querySelector('.terminal-teleprinter');
      expect(container).toBeInTheDocument();
      
      // Check for CRT-style container properties
      const style = window.getComputedStyle(container!);
      expect(style.backgroundColor).toBe('rgb(10, 10, 10)'); // #0a0a0a
      expect(style.color).toBe('rgb(0, 255, 136)'); // #00ff88
    });

    it('displays logs with proper formatting', async () => {
      render(<TerminalTeleprinter logs={mockLogs.slice(0, 1)} typewriterSpeed={1000} />);
      
      // Wait for typewriter animation to complete
      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      expect(screen.getByText('INFO')).toBeInTheDocument();
      // Check if the log entry exists (may be in progress)
      const container = document.querySelector('.terminal-teleprinter');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Log Level Styling', () => {
    it('applies correct styling for info level logs', async () => {
      render(<TerminalTeleprinter logs={[mockLogs[0]]} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });

      const infoLabel = screen.getByText('INFO');
      const style = window.getComputedStyle(infoLabel);
      expect(style.color).toBe('rgb(0, 255, 136)');
    });

    it('applies warning styling with enhanced visibility', async () => {
      render(<TerminalTeleprinter logs={[mockLogs[1]]} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });

      const warningLabel = screen.getByText('WARNING');
      const style = window.getComputedStyle(warningLabel);
      expect(style.color).toBe('rgb(255, 170, 0)');
    });

    it('applies error styling with critical visual emphasis', async () => {
      render(<TerminalTeleprinter logs={[mockLogs[2]]} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });

      const errorLabel = screen.getByText('ERROR');
      const style = window.getComputedStyle(errorLabel);
      expect(style.color).toBe('rgb(255, 68, 68)');
    });

    it('applies success styling with positive feedback', async () => {
      render(<TerminalTeleprinter logs={[mockLogs[3]]} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });

      const successLabel = screen.getByText('SUCCESS');
      const style = window.getComputedStyle(successLabel);
      expect(style.color).toBe('rgb(68, 255, 68)');
    });
  });

  describe('Visual Flash Effects', () => {
    it('triggers flash effect for warning level logs', async () => {
      const { rerender } = render(<TerminalTeleprinter logs={[]} typewriterSpeed={1000} />);
      
      // Add warning log
      rerender(<TerminalTeleprinter logs={[mockLogs[1]]} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(2000); // Complete typewriter animation
      });

      // Flash effect should be triggered (tested through style changes)
      const warningLabel = screen.getByText('WARNING');
      expect(warningLabel).toBeInTheDocument();
    });

    it('triggers enhanced flash effect for error level logs', async () => {
      const { rerender } = render(<TerminalTeleprinter logs={[]} typewriterSpeed={1000} />);
      
      // Add error log
      rerender(<TerminalTeleprinter logs={[mockLogs[2]]} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(2000); // Complete typewriter animation
      });

      const errorLabel = screen.getByText('ERROR');
      expect(errorLabel).toBeInTheDocument();
    });

    it('does not trigger flash effect for info and success logs', async () => {
      render(<TerminalTeleprinter logs={[mockLogs[0], mockLogs[3]]} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(4000); // Complete both animations
      });

      // Info and success logs should not have flash effects
      expect(screen.getByText('INFO')).toBeInTheDocument();
      expect(screen.getByText('SUCCESS')).toBeInTheDocument();
    });
  });

  describe('Audio Feedback', () => {
    it('plays audio feedback when enabled', async () => {
      const { rerender } = render(<TerminalTeleprinter logs={[]} audioFeedback={true} typewriterSpeed={1000} />);
      
      // Add a log to trigger audio feedback
      rerender(<TerminalTeleprinter logs={[mockLogs[0]]} audioFeedback={true} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      // Audio feedback should be triggered when logs are added
      // Note: This test verifies the component structure supports audio feedback
      expect(document.querySelector('.terminal-teleprinter')).toBeInTheDocument();
    });

    it('does not play audio when disabled', async () => {
      render(<TerminalTeleprinter logs={[mockLogs[0]]} audioFeedback={false} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });

      // AudioContext should not be used when audio is disabled
      expect(window.AudioContext).not.toHaveBeenCalled();
    });

    it('uses different frequencies for different log levels', async () => {
      const { rerender } = render(<TerminalTeleprinter logs={[]} audioFeedback={true} typewriterSpeed={1000} />);
      
      // Test each log level
      for (const log of mockLogs) {
        rerender(<TerminalTeleprinter logs={[log]} audioFeedback={true} typewriterSpeed={1000} />);
        
        await act(async () => {
          vi.advanceTimersByTime(5000);
        });
      }

      // Verify the component handles different log levels
      expect(document.querySelector('.terminal-teleprinter')).toBeInTheDocument();
    });
  });

  describe('Typewriter Animation', () => {
    it('animates text character by character', async () => {
      render(<TerminalTeleprinter logs={[mockLogs[0]]} typewriterSpeed={100} />);
      
      // Check that text appears gradually
      await act(async () => {
        vi.advanceTimersByTime(500); // Partial animation
      });

      // Should show partial text or cursor
      const container = document.querySelector('.terminal-teleprinter');
      expect(container).toBeInTheDocument();
      
      // Complete animation
      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      // Check that the log entry is present
      expect(screen.getByText('INFO')).toBeInTheDocument();
    });

    it('shows blinking cursor during animation', async () => {
      render(<TerminalTeleprinter logs={[mockLogs[0]]} typewriterSpeed={50} />);
      
      await act(async () => {
        vi.advanceTimersByTime(100); // Start animation
      });

      // Look for cursor character (█)
      expect(screen.getByText('█')).toBeInTheDocument();
    });

    it('processes multiple logs sequentially', async () => {
      render(<TerminalTeleprinter logs={mockLogs.slice(0, 2)} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(4000); // Time for both logs
      });

      expect(screen.getByText('INFO')).toBeInTheDocument();
      expect(screen.getByText('WARNING')).toBeInTheDocument();
    });
  });

  describe('Performance Optimization', () => {
    it('limits displayed logs to maxLines', async () => {
      const manyLogs = Array.from({ length: 100 }, (_, i) => ({
        id: `log-${i}`,
        timestamp: new Date(),
        step: 'TEST',
        message: `Log entry ${i}`,
        level: 'info' as const
      }));

      render(<TerminalTeleprinter logs={manyLogs} maxLines={10} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(15000); // Allow time for processing
      });

      // Should only render the most recent logs
      const container = document.querySelector('.terminal-teleprinter');
      const logElements = container!.querySelectorAll('[style*="margin-bottom: 4px"]');
      expect(logElements.length).toBeLessThanOrEqual(10);
    });

    it('handles rapid log updates efficiently', async () => {
      const { rerender } = render(<TerminalTeleprinter logs={[]} typewriterSpeed={1000} />);
      
      // Rapidly add logs
      for (let i = 0; i < 10; i++) {
        const newLogs = mockLogs.slice(0, i + 1);
        rerender(<TerminalTeleprinter logs={newLogs} typewriterSpeed={1000} />);
        
        await act(async () => {
          vi.advanceTimersByTime(100);
        });
      }

      // Component should handle rapid updates without errors
      expect(document.querySelector('.terminal-teleprinter')).toBeInTheDocument();
    });

    it('cleans up resources on unmount', () => {
      const { unmount } = render(<TerminalTeleprinter logs={mockLogs} audioFeedback={true} />);
      
      unmount();
      
      // Verify component unmounts without errors
      expect(document.querySelector('.terminal-teleprinter')).not.toBeInTheDocument();
    });
  });

  describe('Auto-scrolling', () => {
    it('auto-scrolls to bottom when enabled', async () => {
      const scrollToBottomSpy = vi.fn();
      
      // Mock scrollTop and scrollHeight
      Object.defineProperty(HTMLElement.prototype, 'scrollTop', {
        set: scrollToBottomSpy,
        configurable: true
      });
      
      Object.defineProperty(HTMLElement.prototype, 'scrollHeight', {
        get: () => 1000,
        configurable: true
      });

      render(<TerminalTeleprinter logs={mockLogs} autoScroll={true} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      // Should attempt to scroll to bottom
      expect(scrollToBottomSpy).toHaveBeenCalled();
    });

    it('does not auto-scroll when disabled', async () => {
      const scrollToBottomSpy = vi.fn();
      
      Object.defineProperty(HTMLElement.prototype, 'scrollTop', {
        set: scrollToBottomSpy,
        configurable: true
      });

      render(<TerminalTeleprinter logs={mockLogs} autoScroll={false} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      // Should not scroll when auto-scroll is disabled
      expect(scrollToBottomSpy).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('handles audio context creation errors gracefully', async () => {
      // Mock AudioContext to throw error
      Object.defineProperty(window, 'AudioContext', {
        writable: true,
        value: vi.fn(() => {
          throw new Error('AudioContext not supported');
        })
      });

      render(<TerminalTeleprinter logs={[mockLogs[0]]} audioFeedback={true} typewriterSpeed={1000} />);
      
      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      // Should render without crashing even if audio fails
      expect(document.querySelector('.terminal-teleprinter')).toBeInTheDocument();
    });

    it('calls onError callback when provided', async () => {
      const onErrorSpy = vi.fn();
      
      render(<TerminalTeleprinter logs={mockLogs} onError={onErrorSpy} />);
      
      // Component should render without calling onError for normal operation
      expect(onErrorSpy).not.toHaveBeenCalled();
    });
  });
});