/**
 * Terminal Teleprinter Demo Component
 * 
 * Demonstrates the TerminalTeleprinter component with simulated reasoning logs
 * and various log levels to showcase audio/visual feedback features.
 */

import React, { useState, useEffect } from 'react';
import TerminalTeleprinter from './TerminalTeleprinter';
import type { ReasoningLog } from '../../types/monitoring';
import { industrialTokens } from '../../design-system/tokens';

const TerminalTeleprinterDemo: React.FC = () => {
  const [logs, setLogs] = useState<ReasoningLog[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(false);

  // Sample reasoning logs for demonstration
  const sampleLogs: Omit<ReasoningLog, 'id' | 'timestamp'>[] = [
    {
      step: 'INIT',
      message: 'Initializing brand compliance audit system...',
      level: 'info'
    },
    {
      step: 'LOAD',
      message: 'Loading brand guidelines from Neo4j database',
      level: 'info'
    },
    {
      step: 'SCAN',
      message: 'Scanning visual elements for compliance violations',
      level: 'info'
    },
    {
      step: 'ANALYZE',
      message: 'Typography analysis: Helvetica Neue detected (brand compliant)',
      level: 'success'
    },
    {
      step: 'ANALYZE',
      message: 'Color analysis: Primary brand color #FF6B35 found in 78% of elements',
      level: 'success'
    },
    {
      step: 'WARNING',
      message: 'Logo placement violates minimum clearspace requirements',
      level: 'warning'
    },
    {
      step: 'ANALYZE',
      message: 'Voice tone analysis: Detected informal language in formal context',
      level: 'warning'
    },
    {
      step: 'ERROR',
      message: 'Critical violation: Unauthorized color #FF0000 detected in brand elements',
      level: 'error'
    },
    {
      step: 'CORRECT',
      message: 'Applying automatic color correction to #FF6B35',
      level: 'info'
    },
    {
      step: 'VALIDATE',
      message: 'Re-validating compliance after corrections...',
      level: 'info'
    },
    {
      step: 'COMPLETE',
      message: 'Brand compliance audit completed successfully',
      level: 'success'
    },
    {
      step: 'REPORT',
      message: 'Generating compliance report with 87% overall score',
      level: 'success'
    }
  ];

  // Simulate real-time log streaming
  useEffect(() => {
    let timeoutId: number;
    let logIndex = 0;

    const addNextLog = () => {
      if (isRunning && logIndex < sampleLogs.length) {
        const newLog: ReasoningLog = {
          ...sampleLogs[logIndex],
          id: `log-${Date.now()}-${logIndex}`,
          timestamp: new Date()
        };

        setLogs(prevLogs => [...prevLogs, newLog]);
        logIndex++;

        // Random delay between 1-3 seconds for realistic timing
        const delay = Math.random() * 2000 + 1000;
        timeoutId = setTimeout(addNextLog, delay);
      } else if (logIndex >= sampleLogs.length) {
        setIsRunning(false);
        logIndex = 0;
      }
    };

    if (isRunning) {
      addNextLog();
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [isRunning, sampleLogs]);

  const handleStart = () => {
    setLogs([]);
    setIsRunning(true);
  };

  const handleStop = () => {
    setIsRunning(false);
  };

  const handleClear = () => {
    setLogs([]);
    setIsRunning(false);
  };

  const handleAddSingleLog = (level: ReasoningLog['level']) => {
    const messages = {
      info: 'Manual info log entry for testing',
      warning: 'Manual warning log entry with flash effect',
      error: 'Manual error log entry with enhanced flash effect',
      success: 'Manual success log entry for testing'
    };

    const newLog: ReasoningLog = {
      id: `manual-${Date.now()}`,
      timestamp: new Date(),
      step: 'MANUAL',
      message: messages[level],
      level
    };

    setLogs(prevLogs => [...prevLogs, newLog]);
  };

  return (
    <div style={{
      padding: '24px',
      backgroundColor: industrialTokens.colors.surface.primary,
      minHeight: '100vh',
      fontFamily: industrialTokens.typography.fontFamily.primary
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <h1 style={{
          color: industrialTokens.colors.text.primary,
          fontSize: industrialTokens.typography.scale.display.fontSize,
          fontWeight: industrialTokens.typography.scale.display.fontWeight,
          marginBottom: '8px',
          textAlign: 'center'
        }}>
          TERMINAL TELEPRINTER DEMO
        </h1>
        
        <p style={{
          color: industrialTokens.colors.text.secondary,
          fontSize: industrialTokens.typography.scale.body.fontSize,
          textAlign: 'center',
          marginBottom: '32px',
          maxWidth: '600px',
          margin: '0 auto 32px'
        }}>
          Real-time reasoning log display with typewriter animation, CRT aesthetics, 
          and audio/visual feedback for different log levels.
        </p>

        {/* Control Panel */}
        <div style={{
          display: 'flex',
          gap: '16px',
          marginBottom: '24px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <button
            onClick={handleStart}
            disabled={isRunning}
            style={{
              padding: '12px 24px',
              backgroundColor: isRunning ? '#666' : '#00ff88',
              color: isRunning ? '#ccc' : '#000',
              border: 'none',
              borderRadius: '4px',
              fontFamily: industrialTokens.typography.fontFamily.mono,
              fontWeight: 'bold',
              cursor: isRunning ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            {isRunning ? 'RUNNING...' : 'START SIMULATION'}
          </button>

          <button
            onClick={handleStop}
            disabled={!isRunning}
            style={{
              padding: '12px 24px',
              backgroundColor: !isRunning ? '#666' : '#ffaa00',
              color: !isRunning ? '#ccc' : '#000',
              border: 'none',
              borderRadius: '4px',
              fontFamily: industrialTokens.typography.fontFamily.mono,
              fontWeight: 'bold',
              cursor: !isRunning ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            STOP
          </button>

          <button
            onClick={handleClear}
            style={{
              padding: '12px 24px',
              backgroundColor: '#ff4444',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              fontFamily: industrialTokens.typography.fontFamily.mono,
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            CLEAR
          </button>

          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: industrialTokens.colors.text.primary,
            fontFamily: industrialTokens.typography.fontFamily.mono
          }}>
            <input
              type="checkbox"
              checked={audioEnabled}
              onChange={(e) => setAudioEnabled(e.target.checked)}
              style={{ transform: 'scale(1.2)' }}
            />
            AUDIO FEEDBACK
          </label>
        </div>

        {/* Manual Log Level Testing */}
        <div style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '24px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <span style={{
            color: industrialTokens.colors.text.secondary,
            fontFamily: industrialTokens.typography.fontFamily.mono,
            alignSelf: 'center'
          }}>
            TEST LOG LEVELS:
          </span>
          
          {(['info', 'success', 'warning', 'error'] as const).map(level => (
            <button
              key={level}
              onClick={() => handleAddSingleLog(level)}
              style={{
                padding: '8px 16px',
                backgroundColor: {
                  info: '#00ff88',
                  success: '#44ff44',
                  warning: '#ffaa00',
                  error: '#ff4444'
                }[level],
                color: level === 'info' || level === 'success' ? '#000' : '#fff',
                border: 'none',
                borderRadius: '4px',
                fontFamily: industrialTokens.typography.fontFamily.mono,
                fontSize: '12px',
                fontWeight: 'bold',
                cursor: 'pointer',
                textTransform: 'uppercase',
                transition: 'all 0.2s ease'
              }}
            >
              {level}
            </button>
          ))}
        </div>

        {/* Terminal Display */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '24px',
          maxWidth: '800px',
          margin: '0 auto'
        }}>
          <div>
            <h3 style={{
              color: industrialTokens.colors.text.primary,
              fontFamily: industrialTokens.typography.fontFamily.mono,
              marginBottom: '16px',
              textAlign: 'center'
            }}>
              REASONING LOG TERMINAL
            </h3>
            
            <TerminalTeleprinter
              logs={logs}
              maxLines={20}
              typewriterSpeed={50}
              autoScroll={true}
              audioFeedback={audioEnabled}
            />
          </div>
        </div>

        {/* Status Information */}
        <div style={{
          marginTop: '24px',
          padding: '16px',
          backgroundColor: 'rgba(0, 255, 136, 0.1)',
          border: '1px solid rgba(0, 255, 136, 0.3)',
          borderRadius: '8px',
          maxWidth: '800px',
          margin: '24px auto 0'
        }}>
          <h4 style={{
            color: industrialTokens.colors.text.primary,
            fontFamily: industrialTokens.typography.fontFamily.mono,
            marginBottom: '12px'
          }}>
            TERMINAL STATUS
          </h4>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
            fontFamily: industrialTokens.typography.fontFamily.mono,
            fontSize: '14px'
          }}>
            <div>
              <span style={{ color: industrialTokens.colors.text.secondary }}>Status: </span>
              <span style={{ color: isRunning ? '#00ff88' : '#ffaa00' }}>
                {isRunning ? 'ACTIVE' : 'STANDBY'}
              </span>
            </div>
            
            <div>
              <span style={{ color: industrialTokens.colors.text.secondary }}>Log Count: </span>
              <span style={{ color: '#00ff88' }}>{logs.length}</span>
            </div>
            
            <div>
              <span style={{ color: industrialTokens.colors.text.secondary }}>Audio: </span>
              <span style={{ color: audioEnabled ? '#00ff88' : '#666' }}>
                {audioEnabled ? 'ENABLED' : 'DISABLED'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TerminalTeleprinterDemo;