/**
 * CRT Oscilloscope Demo Component
 * 
 * Demonstrates the CRT Oscilloscope with sample compliance data
 * for testing and development purposes.
 */

import React, { useState, useEffect } from 'react';
import CRTOscilloscope from './CRTOscilloscope';
import type { ComplianceScores } from '../../types/monitoring';

const CRTOscilloscopeDemo: React.FC = () => {
  const [complianceScores, setComplianceScores] = useState<ComplianceScores>({
    typography: 0.85,
    voice: 0.72,
    color: 0.91,
    logo: 0.68,
  });

  const [isAnimating, setIsAnimating] = useState(false);

  // Simulate real-time compliance score updates
  useEffect(() => {
    if (!isAnimating) return;

    const interval = setInterval(() => {
      setComplianceScores(prev => ({
        typography: Math.max(0.1, Math.min(1.0, prev.typography + (Math.random() - 0.5) * 0.1)),
        voice: Math.max(0.1, Math.min(1.0, prev.voice + (Math.random() - 0.5) * 0.1)),
        color: Math.max(0.1, Math.min(1.0, prev.color + (Math.random() - 0.5) * 0.1)),
        logo: Math.max(0.1, Math.min(1.0, prev.logo + (Math.random() - 0.5) * 0.1)),
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, [isAnimating]);

  const handleError = (error: Error) => {
    console.error('CRT Oscilloscope Error:', error);
  };

  return (
    <div style={{ 
      padding: '20px', 
      backgroundColor: '#000', 
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '20px'
    }}>
      <h1 style={{ 
        color: '#00ff41', 
        fontFamily: 'JetBrains Mono, monospace',
        textAlign: 'center',
        textShadow: '0 0 10px #00ff41'
      }}>
        CRT OSCILLOSCOPE DEMO
      </h1>
      
      <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
        <button
          onClick={() => setIsAnimating(!isAnimating)}
          style={{
            padding: '10px 20px',
            backgroundColor: isAnimating ? '#ff4757' : '#00ff41',
            color: '#000',
            border: 'none',
            borderRadius: '4px',
            fontFamily: 'JetBrains Mono, monospace',
            fontWeight: 'bold',
            cursor: 'pointer',
            textTransform: 'uppercase',
          }}
        >
          {isAnimating ? 'Stop Animation' : 'Start Animation'}
        </button>
        
        <button
          onClick={() => setComplianceScores({
            typography: Math.random(),
            voice: Math.random(),
            color: Math.random(),
            logo: Math.random(),
          })}
          style={{
            padding: '10px 20px',
            backgroundColor: '#74b9ff',
            color: '#000',
            border: 'none',
            borderRadius: '4px',
            fontFamily: 'JetBrains Mono, monospace',
            fontWeight: 'bold',
            cursor: 'pointer',
            textTransform: 'uppercase',
          }}
        >
          Random Scores
        </button>
      </div>

      <CRTOscilloscope
        complianceScores={complianceScores}
        sweepSpeed={3}
        phosphorIntensity={0.8}
        scanlineOpacity={0.1}
        onError={handleError}
      />

      <div style={{
        color: '#00ff41',
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: '14px',
        textAlign: 'center',
        maxWidth: '400px',
        lineHeight: '1.6',
      }}>
        <h3>Current Compliance Scores:</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '10px' }}>
          <div>TYPOGRAPHY: {(complianceScores.typography * 100).toFixed(1)}%</div>
          <div>VOICE: {(complianceScores.voice * 100).toFixed(1)}%</div>
          <div>COLOR: {(complianceScores.color * 100).toFixed(1)}%</div>
          <div>LOGO: {(complianceScores.logo * 100).toFixed(1)}%</div>
        </div>
      </div>
    </div>
  );
};

export default CRTOscilloscopeDemo;