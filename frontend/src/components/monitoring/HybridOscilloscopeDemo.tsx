/**
 * Hybrid Oscilloscope Demo Component
 * 
 * Demonstrates the Hybrid Oscilloscope with sample compliance data
 * for testing visibility and functionality.
 */

import React, { useState, useEffect } from 'react';
import HybridOscilloscope from './HybridOscilloscope';
import { industrialTokens } from '../../design-system/tokens';
import type { ComplianceScores } from '../../types/monitoring';

const HybridOscilloscopeDemo: React.FC = () => {
  const [complianceScores, setComplianceScores] = useState<ComplianceScores>({
    typography: 0.85,
    voice: 0.72,
    color: 0.91,
    logo: 0.68,
  });

  const [isAnimating, setIsAnimating] = useState(false);
  const [intensity, setIntensity] = useState<'subtle' | 'normal' | 'high'>('normal');

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
    console.error('Hybrid Oscilloscope Error:', error);
  };

  return (
    <div style={{ 
      padding: '40px', 
      backgroundColor: industrialTokens.colors.surface.tertiary,
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '30px',
      fontFamily: industrialTokens.typography.fontFamily.primary,
    }}>
      <h1 style={{ 
        color: industrialTokens.colors.text.primary,
        fontSize: industrialTokens.typography.scale.display.fontSize,
        fontWeight: industrialTokens.typography.scale.display.fontWeight,
        textAlign: 'center',
        textShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '10px',
      }}>
        HYBRID OSCILLOSCOPE DEMO
      </h1>
      
      <p style={{
        color: industrialTokens.colors.text.secondary,
        fontSize: industrialTokens.typography.scale.body.fontSize,
        textAlign: 'center',
        maxWidth: '600px',
        lineHeight: '1.6',
        marginBottom: '20px',
      }}>
        Testing the enhanced visibility and design system integration of the Hybrid Oscilloscope component.
      </p>
      
      <div style={{ 
        display: 'flex', 
        gap: '20px', 
        alignItems: 'center',
        flexWrap: 'wrap',
        justifyContent: 'center',
      }}>
        <button
          onClick={() => setIsAnimating(!isAnimating)}
          style={{
            padding: '12px 24px',
            backgroundColor: isAnimating ? industrialTokens.colors.led.error : industrialTokens.colors.led.on,
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontFamily: industrialTokens.typography.fontFamily.mono,
            fontWeight: '600',
            cursor: 'pointer',
            textTransform: 'uppercase',
            letterSpacing: '0.025em',
            boxShadow: isAnimating 
              ? `0 0 15px ${industrialTokens.colors.led.error}` 
              : `0 0 15px ${industrialTokens.colors.led.on}`,
            transition: 'all 0.3s ease',
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
            padding: '12px 24px',
            backgroundColor: industrialTokens.colors.led.off,
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontFamily: industrialTokens.typography.fontFamily.mono,
            fontWeight: '600',
            cursor: 'pointer',
            textTransform: 'uppercase',
            letterSpacing: '0.025em',
            boxShadow: `0 0 15px ${industrialTokens.colors.led.off}`,
            transition: 'all 0.3s ease',
          }}
        >
          Random Scores
        </button>

        <select
          value={intensity}
          onChange={(e) => setIntensity(e.target.value as 'subtle' | 'normal' | 'high')}
          style={{
            padding: '12px 16px',
            backgroundColor: industrialTokens.colors.surface.primary,
            color: industrialTokens.colors.text.primary,
            border: `1px solid ${industrialTokens.colors.text.muted}`,
            borderRadius: '8px',
            fontFamily: industrialTokens.typography.fontFamily.mono,
            fontWeight: '500',
            cursor: 'pointer',
            textTransform: 'uppercase',
            letterSpacing: '0.025em',
          }}
        >
          <option value="subtle">Subtle</option>
          <option value="normal">Normal</option>
          <option value="high">High</option>
        </select>
      </div>

      <HybridOscilloscope
        complianceScores={complianceScores}
        sweepSpeed={3}
        intensity={intensity}
        showLabels={true}
        size="medium"
        onError={handleError}
      />

      <div style={{
        color: industrialTokens.colors.text.primary,
        fontFamily: industrialTokens.typography.fontFamily.mono,
        fontSize: '14px',
        textAlign: 'center',
        maxWidth: '500px',
        lineHeight: '1.6',
        backgroundColor: industrialTokens.colors.surface.primary,
        padding: '20px',
        borderRadius: '12px',
        boxShadow: '4px 4px 8px #babecc, -4px -4px 8px #ffffff',
      }}>
        <h3 style={{ marginBottom: '15px', color: industrialTokens.colors.text.primary }}>
          Current Settings
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '15px' }}>
          <div><strong>Intensity:</strong> {intensity.toUpperCase()}</div>
          <div><strong>Animation:</strong> {isAnimating ? 'ON' : 'OFF'}</div>
        </div>
        <h4 style={{ marginBottom: '10px' }}>Compliance Scores:</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          <div>TYPOGRAPHY: {(complianceScores.typography * 100).toFixed(1)}%</div>
          <div>VOICE: {(complianceScores.voice * 100).toFixed(1)}%</div>
          <div>COLOR: {(complianceScores.color * 100).toFixed(1)}%</div>
          <div>LOGO: {(complianceScores.logo * 100).toFixed(1)}%</div>
        </div>
      </div>
    </div>
  );
};

export default HybridOscilloscopeDemo;