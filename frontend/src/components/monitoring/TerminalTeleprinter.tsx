/**
 * Terminal Teleprinter Component
 * 
 * A monitoring component that displays real-time reasoning logs with typewriter animation
 * and CRT terminal aesthetics. Features monospace text, auto-scrolling, and phosphor green styling.
 */

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import type { ReasoningLog, MonitoringComponentProps } from '../../types/monitoring';

export interface TerminalTeleprinterProps extends MonitoringComponentProps {
  logs: ReasoningLog[];
  maxLines?: number;
  typewriterSpeed?: number;
  autoScroll?: boolean;
  audioFeedback?: boolean;
}

interface TypewriterState {
  displayedLogs: Array<{
    log: ReasoningLog;
    displayedText: string;
    isComplete: boolean;
  }>;
  currentlyTyping: boolean;
}

const TerminalTeleprinter: React.FC<TerminalTeleprinterProps> = ({
  logs,
  maxLines = 50,
  typewriterSpeed = 30, // characters per second
  autoScroll = true,
  audioFeedback = false,
  className = '',
  style
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const typewriterTimeoutRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  
  const [typewriterState, setTypewriterState] = useState<TypewriterState>({
    displayedLogs: [],
    currentlyTyping: false
  });
  
  const [flashingLogId, setFlashingLogId] = useState<string | null>(null);

  // Industrial terminal styling - matches existing design system
  const terminalStyles = useMemo(() => ({
    container: {
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: '10px',
      lineHeight: '1.4',
      color: '#2d3436',
      height: '100%',
      overflow: 'hidden',
      position: 'relative' as const,
    },
    scrollArea: {
      height: '100%',
      overflowY: 'auto' as const,
      scrollbarWidth: 'thin' as const,
      scrollbarColor: 'rgba(45, 52, 54, 0.3) rgba(224, 229, 236, 0.5)',
      backgroundColor: 'rgba(255, 255, 255, 0.2)',
      borderRadius: '0.5rem',
      padding: '0.75rem',
      boxShadow: 'inset 2px 2px 8px rgba(140, 155, 175, 0.3), inset -1px -1px 4px rgba(255, 255, 255, 0.8)',
    },
    logEntry: {
      marginBottom: '3px',
      whiteSpace: 'pre-wrap' as const,
      wordBreak: 'break-word' as const,
      padding: '2px 4px',
      borderRadius: '2px',
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
      border: '1px solid rgba(140, 155, 175, 0.1)',
    }
  }), []);

  // Industrial log level styling - matches existing design system
  const getLogLevelStyles = useCallback((level: ReasoningLog['level'], isFlashing: boolean = false) => {
    const baseStyles = {
      padding: '2px 4px',
      borderRadius: '3px',
      transition: 'all 0.3s ease',
      display: 'inline-block',
      marginRight: '6px',
      minWidth: '50px',
      textAlign: 'center' as const,
      fontSize: '8px',
      fontWeight: '600' as const,
      letterSpacing: '0.05em',
      textTransform: 'uppercase' as const,
      fontFamily: 'Space Grotesk, system-ui, sans-serif',
    };

    const levelStyles = {
      info: {
        background: isFlashing 
          ? 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)'
          : 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
        color: isFlashing ? '#ffffff' : '#1e40af',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        boxShadow: isFlashing 
          ? 'inset 1px 1px 2px rgba(255, 255, 255, 0.3), 0 2px 8px rgba(59, 130, 246, 0.4)'
          : 'inset 1px 1px 2px rgba(255, 255, 255, 0.8), inset -1px -1px 2px rgba(59, 130, 246, 0.1)',
      },
      warning: {
        background: isFlashing 
          ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
          : 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
        color: isFlashing ? '#ffffff' : '#92400e',
        border: '1px solid rgba(245, 158, 11, 0.3)',
        boxShadow: isFlashing 
          ? 'inset 1px 1px 2px rgba(255, 255, 255, 0.3), 0 2px 8px rgba(245, 158, 11, 0.4)'
          : 'inset 1px 1px 2px rgba(255, 255, 255, 0.8), inset -1px -1px 2px rgba(245, 158, 11, 0.1)',
      },
      error: {
        background: isFlashing 
          ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
          : 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)',
        color: isFlashing ? '#ffffff' : '#991b1b',
        border: '1px solid rgba(239, 68, 68, 0.3)',
        boxShadow: isFlashing 
          ? 'inset 1px 1px 2px rgba(255, 255, 255, 0.3), 0 2px 8px rgba(239, 68, 68, 0.4)'
          : 'inset 1px 1px 2px rgba(255, 255, 255, 0.8), inset -1px -1px 2px rgba(239, 68, 68, 0.1)',
      },
      success: {
        background: isFlashing 
          ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
          : 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)',
        color: isFlashing ? '#ffffff' : '#065f46',
        border: '1px solid rgba(16, 185, 129, 0.3)',
        boxShadow: isFlashing 
          ? 'inset 1px 1px 2px rgba(255, 255, 255, 0.3), 0 2px 8px rgba(16, 185, 129, 0.4)'
          : 'inset 1px 1px 2px rgba(255, 255, 255, 0.8), inset -1px -1px 2px rgba(16, 185, 129, 0.1)',
      }
    };

    return { ...baseStyles, ...levelStyles[level] };
  }, []);

  // Audio feedback for important log entries
  const playAudioFeedback = useCallback((level: ReasoningLog['level']) => {
    if (!audioFeedback) return;

    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      const ctx = audioContextRef.current;
      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);

      // Different tones for different log levels
      const frequencies = {
        info: 800,
        warning: 600,
        error: 400,
        success: 1000
      };

      oscillator.frequency.setValueAtTime(frequencies[level], ctx.currentTime);
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0, ctx.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.1, ctx.currentTime + 0.01);
      gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);

      oscillator.start(ctx.currentTime);
      oscillator.stop(ctx.currentTime + 0.1);
    } catch (error) {
      console.warn('Audio feedback failed:', error);
    }
  }, [audioFeedback]);

  // Visual flash effect for important log entries
  const triggerFlashEffect = useCallback((logId: string, level: ReasoningLog['level']) => {
    if (level === 'warning' || level === 'error') {
      setFlashingLogId(logId);
      setTimeout(() => setFlashingLogId(null), 500);
    }
  }, []);

  // Typewriter animation effect
  const animateTypewriter = useCallback((newLogs: ReasoningLog[]) => {
    if (typewriterTimeoutRef.current) {
      clearTimeout(typewriterTimeoutRef.current);
    }

    // Process new logs
    setTypewriterState(prevState => {
      const existingLogIds = new Set(prevState.displayedLogs.map(dl => dl.log.id));
      const logsToAdd = newLogs.filter(log => !existingLogIds.has(log.id));
      
      if (logsToAdd.length === 0) return prevState;

      // Start with existing complete logs and new logs with empty text
      const updatedLogs = [
        ...prevState.displayedLogs,
        ...logsToAdd.map(log => ({
          log,
          displayedText: '',
          isComplete: false
        }))
      ];

      // Keep only the most recent logs
      const trimmedLogs = updatedLogs.slice(-maxLines);

      return {
        displayedLogs: trimmedLogs,
        currentlyTyping: true
      };
    });

    // Start animation after state update
    setTimeout(() => {
      animateNextCharacter(0);
    }, 50);

    // Animate the typewriter effect for new logs
    function animateNextCharacter(currentLogIndex: number) {
      setTypewriterState(prevState => {
        const newState = { ...prevState };
        
        // Find the next incomplete log starting from currentLogIndex
        let logIndex = currentLogIndex;
        while (logIndex < newState.displayedLogs.length && newState.displayedLogs[logIndex].isComplete) {
          logIndex++;
        }
        
        if (logIndex >= newState.displayedLogs.length) {
          // All logs are complete
          newState.currentlyTyping = false;
          return newState;
        }

        const logToUpdate = newState.displayedLogs[logIndex];
        const fullText = `[${logToUpdate.log.timestamp.toLocaleTimeString()}] ${logToUpdate.log.step}: ${logToUpdate.log.message}`;
        const currentLength = logToUpdate.displayedText.length;
        
        if (currentLength < fullText.length) {
          // Add next character
          logToUpdate.displayedText = fullText.substring(0, currentLength + 1);
          
          // Schedule next character
          typewriterTimeoutRef.current = setTimeout(() => {
            animateNextCharacter(logIndex);
          }, 1000 / typewriterSpeed);
        } else {
          // Log is complete
          logToUpdate.isComplete = true;
          
          // Trigger effects for completed log
          playAudioFeedback(logToUpdate.log.level);
          triggerFlashEffect(logToUpdate.log.id, logToUpdate.log.level);
          
          // Move to next log
          typewriterTimeoutRef.current = setTimeout(() => {
            animateNextCharacter(logIndex + 1);
          }, 100);
        }

        return newState;
      });
    }
  }, [maxLines, typewriterSpeed, playAudioFeedback, triggerFlashEffect]);

  // Handle new logs
  useEffect(() => {
    if (logs.length > 0) {
      animateTypewriter(logs);
    }
  }, [logs, animateTypewriter]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [typewriterState.displayedLogs, autoScroll]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (typewriterTimeoutRef.current) {
        clearTimeout(typewriterTimeoutRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // Performance optimization: memoize rendered logs
  const renderedLogs = useMemo(() => {
    return typewriterState.displayedLogs.map((displayedLog) => {
      const isFlashing = flashingLogId === displayedLog.log.id;
      
      return (
        <div key={displayedLog.log.id} style={terminalStyles.logEntry}>
          <span style={getLogLevelStyles(displayedLog.log.level, isFlashing)}>
            {displayedLog.log.level.toUpperCase()}
          </span>
          <span style={{ 
            opacity: displayedLog.isComplete ? 1 : 0.9,
            color: '#374151',
            fontFamily: 'JetBrains Mono, monospace'
          }}>
            {displayedLog.displayedText}
          </span>
          {!displayedLog.isComplete && (
            <span className="cursor" style={{ 
              marginLeft: '4px',
              color: '#3b82f6',
              fontWeight: 'bold'
            }}>
              ▊
            </span>
          )}
        </div>
      );
    });
  }, [typewriterState.displayedLogs, flashingLogId, terminalStyles.logEntry, getLogLevelStyles]);

  return (
    <div 
      ref={containerRef}
      className={`terminal-teleprinter ${className}`}
      style={{ ...terminalStyles.container, ...style }}
    >
      <div ref={scrollRef} style={terminalStyles.scrollArea}>
        {renderedLogs}
      </div>
      
      <style>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0.3; }
        }
        
        .terminal-teleprinter .cursor {
          animation: blink 1.2s infinite ease-in-out;
        }
        
        /* Industrial scrollbar styling */
        .terminal-teleprinter div::-webkit-scrollbar {
          width: 6px;
        }
        
        .terminal-teleprinter div::-webkit-scrollbar-track {
          background: rgba(224, 229, 236, 0.5);
          border-radius: 3px;
        }
        
        .terminal-teleprinter div::-webkit-scrollbar-thumb {
          background: rgba(45, 52, 54, 0.3);
          border-radius: 3px;
        }
        
        .terminal-teleprinter div::-webkit-scrollbar-thumb:hover {
          background: rgba(45, 52, 54, 0.5);
        }
      `}</style>
    </div>
  );
};

export default TerminalTeleprinter;