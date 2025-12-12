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

  // CRT terminal styling - phosphor green industrial control room aesthetic
  const terminalStyles = useMemo(() => ({
    container: {
      background: 'linear-gradient(145deg, #0a0f0a 0%, #0d1a0d 50%, #0a0f0a 100%)',
      border: '2px solid #1a3d1a',
      borderRadius: '8px',
      boxShadow: `
        0 0 20px rgba(0, 255, 0, 0.1),
        inset 0 0 20px rgba(0, 0, 0, 0.8),
        inset 0 2px 4px rgba(0, 255, 0, 0.05)
      `,
      padding: '1rem',
      fontFamily: 'JetBrains Mono, Courier New, monospace',
      fontSize: '11px',
      lineHeight: '1.4',
      color: '#00ff41',
      height: '100%',
      overflow: 'hidden',
      position: 'relative' as const,
      // CRT curvature effect
      clipPath: 'inset(0 round 8px)',
    },
    scrollArea: {
      height: '100%',
      overflowY: 'auto' as const,
      scrollbarWidth: 'thin' as const,
      scrollbarColor: 'rgba(0, 255, 65, 0.3) rgba(10, 15, 10, 0.8)',
      backgroundColor: 'rgba(0, 0, 0, 0.6)',
      borderRadius: '4px',
      padding: '0.75rem',
      border: '1px solid rgba(0, 255, 65, 0.2)',
      // Phosphor glow effect
      textShadow: '0 0 5px rgba(0, 255, 65, 0.8)',
    },
    logEntry: {
      marginBottom: '4px',
      whiteSpace: 'pre-wrap' as const,
      wordBreak: 'break-word' as const,
      padding: '2px 6px',
      borderRadius: '2px',
      backgroundColor: 'rgba(0, 255, 65, 0.02)',
      // Subtle phosphor glow on each line
      textShadow: '0 0 3px rgba(0, 255, 65, 0.6)',
    }
  }), []);

  // CRT log level styling with phosphor green aesthetics
  const getLogLevelStyles = useCallback((level: ReasoningLog['level'], isFlashing: boolean = false) => {
    const baseStyles = {
      padding: '2px 6px',
      borderRadius: '2px',
      transition: 'all 0.3s ease',
      display: 'inline-block',
      marginRight: '8px',
      minWidth: '60px',
      textAlign: 'center' as const,
      fontSize: '9px',
      fontWeight: '700' as const,
      letterSpacing: '0.1em',
      textTransform: 'uppercase' as const,
      fontFamily: 'JetBrains Mono, Courier New, monospace',
      border: '1px solid',
    };

    const levelStyles = {
      info: {
        backgroundColor: isFlashing ? 'rgba(0, 255, 65, 0.3)' : 'rgba(0, 255, 65, 0.1)',
        color: isFlashing ? '#ffffff' : '#00ff41',
        borderColor: 'rgba(0, 255, 65, 0.5)',
        textShadow: isFlashing 
          ? '0 0 8px rgba(0, 255, 65, 1)' 
          : '0 0 4px rgba(0, 255, 65, 0.8)',
        boxShadow: isFlashing 
          ? '0 0 10px rgba(0, 255, 65, 0.6)' 
          : '0 0 5px rgba(0, 255, 65, 0.3)',
      },
      warning: {
        backgroundColor: isFlashing ? 'rgba(255, 165, 0, 0.3)' : 'rgba(255, 165, 0, 0.1)',
        color: isFlashing ? '#ffffff' : '#ffaa00',
        borderColor: 'rgba(255, 165, 0, 0.5)',
        textShadow: isFlashing 
          ? '0 0 8px rgba(255, 165, 0, 1)' 
          : '0 0 4px rgba(255, 165, 0, 0.8)',
        boxShadow: isFlashing 
          ? '0 0 10px rgba(255, 165, 0, 0.6)' 
          : '0 0 5px rgba(255, 165, 0, 0.3)',
      },
      error: {
        backgroundColor: isFlashing ? 'rgba(255, 0, 0, 0.3)' : 'rgba(255, 0, 0, 0.1)',
        color: isFlashing ? '#ffffff' : '#ff4444',
        borderColor: 'rgba(255, 0, 0, 0.5)',
        textShadow: isFlashing 
          ? '0 0 8px rgba(255, 0, 0, 1)' 
          : '0 0 4px rgba(255, 0, 0, 0.8)',
        boxShadow: isFlashing 
          ? '0 0 10px rgba(255, 0, 0, 0.6)' 
          : '0 0 5px rgba(255, 0, 0, 0.3)',
      },
      success: {
        backgroundColor: isFlashing ? 'rgba(0, 255, 0, 0.3)' : 'rgba(0, 255, 0, 0.1)',
        color: isFlashing ? '#ffffff' : '#00ff00',
        borderColor: 'rgba(0, 255, 0, 0.5)',
        textShadow: isFlashing 
          ? '0 0 8px rgba(0, 255, 0, 1)' 
          : '0 0 4px rgba(0, 255, 0, 0.8)',
        boxShadow: isFlashing 
          ? '0 0 10px rgba(0, 255, 0, 0.6)' 
          : '0 0 5px rgba(0, 255, 0, 0.3)',
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
            color: '#00ff41',
            fontFamily: 'JetBrains Mono, Courier New, monospace',
            textShadow: '0 0 3px rgba(0, 255, 65, 0.6)'
          }}>
            {displayedLog.displayedText}
          </span>
          {!displayedLog.isComplete && (
            <span className="cursor" style={{ 
              marginLeft: '4px',
              color: '#00ff41',
              fontWeight: 'bold',
              textShadow: '0 0 5px rgba(0, 255, 65, 0.8)'
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
        
        /* CRT phosphor green scrollbar styling */
        .terminal-teleprinter div::-webkit-scrollbar {
          width: 6px;
        }
        
        .terminal-teleprinter div::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.8);
          border-radius: 2px;
        }
        
        .terminal-teleprinter div::-webkit-scrollbar-thumb {
          background: rgba(0, 255, 65, 0.3);
          border-radius: 2px;
          box-shadow: 0 0 3px rgba(0, 255, 65, 0.5);
        }
        
        .terminal-teleprinter div::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 255, 65, 0.5);
          box-shadow: 0 0 5px rgba(0, 255, 65, 0.8);
        }
        
        /* CRT scanline effect */
        .terminal-teleprinter::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 255, 65, 0.03) 2px,
            rgba(0, 255, 65, 0.03) 4px
          );
          pointer-events: none;
          z-index: 1;
        }
      `}</style>
    </div>
  );
};

export default TerminalTeleprinter;