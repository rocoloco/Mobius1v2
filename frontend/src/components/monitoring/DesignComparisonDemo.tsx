/**
 * Design Comparison Demo
 * 
 * Shows both the original CRT Oscilloscope and the new Industrial Oscilloscope
 * to demonstrate design system integration.
 */

import React, { useState, useEffect } from 'react';
import CRTOscilloscope from './CRTOscilloscope';
import IndustrialOscilloscope from './IndustrialOscilloscope';
import HybridOscilloscope from './HybridOscilloscope';
import { industrialTokens } from '../../design-system/tokens';
import type { ComplianceScores } from '../../types/monitoring';

const DesignComparisonDemo: React.FC = () => {
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

  return (
    <div style={{ 
      padding: '40px', 
      backgroundColor: industrialTokens.colors.surface.tertiary,
      minHeight: '100vh',
      fontFamily: industrialTokens.typography.fontFamily.primary,
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
      }}>
        <h1 style={{ 
          color: industrialTokens.colors.text.primary,
          fontSize: industrialTokens.typography.scale.display.fontSize,
          fontWeight: industrialTokens.typography.scale.display.fontWeight,
          textAlign: 'center',
          marginBottom: '20px',
          letterSpacing: industrialTokens.typography.scale.display.letterSpacing,
        }}>
          MONITORING COMPONENT DESIGN COMPARISON
        </h1>
        
        <p style={{
          color: industrialTokens.colors.text.secondary,
          fontSize: industrialTokens.typography.scale.body.fontSize,
          textAlign: 'center',
          marginBottom: '40px',
          maxWidth: '800px',
          margin: '0 auto 40px',
          lineHeight: industrialTokens.typography.scale.body.lineHeight,
        }}>
          Comparing the original CRT-style oscilloscope with the new industrial design system integrated version.
          The industrial version maintains monitoring functionality while matching your existing aesthetic.
        </p>
        
        <div style={{ 
          display: 'flex', 
          gap: '20px', 
          justifyContent: 'center',
          alignItems: 'center',
          marginBottom: '40px',
          flexWrap: 'wrap',
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
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '30px',
          marginBottom: '40px',
        }}>
          {/* Original CRT Style */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '20px',
          }}>
            <h2 style={{
              color: industrialTokens.colors.text.primary,
              fontSize: industrialTokens.typography.scale.heading.fontSize,
              fontWeight: industrialTokens.typography.scale.heading.fontWeight,
              textAlign: 'center',
              marginBottom: '10px',
            }}>
              Original CRT Style
            </h2>
            <p style={{
              color: industrialTokens.colors.text.secondary,
              fontSize: industrialTokens.typography.scale.caption.fontSize,
              textAlign: 'center',
              marginBottom: '20px',
              maxWidth: '300px',
            }}>
              Authentic retro CRT monitor aesthetic with phosphor green styling and scanline effects.
            </p>
            <div style={{ 
              padding: '20px',
              backgroundColor: '#000',
              borderRadius: '12px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}>
              <CRTOscilloscope
                complianceScores={complianceScores}
                sweepSpeed={3}
                phosphorIntensity={0.8}
                scanlineOpacity={0.1}
              />
            </div>
          </div>

          {/* Hybrid Design - Recommended */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '20px',
          }}>
            <h2 style={{
              color: industrialTokens.colors.text.primary,
              fontSize: industrialTokens.typography.scale.heading.fontSize,
              fontWeight: industrialTokens.typography.scale.heading.fontWeight,
              textAlign: 'center',
              marginBottom: '10px',
            }}>
              Hybrid Design ⭐ RECOMMENDED
            </h2>
            <p style={{
              color: industrialTokens.colors.text.secondary,
              fontSize: industrialTokens.typography.scale.caption.fontSize,
              textAlign: 'center',
              marginBottom: '20px',
              maxWidth: '300px',
            }}>
              Perfect balance: maintains design system consistency while providing clear, engaging monitoring visualization.
            </p>
            <HybridOscilloscope
              complianceScores={complianceScores}
              sweepSpeed={3}
              showLabels={true}
              size="medium"
              intensity="normal"
            />
          </div>

          {/* Industrial Design System Integrated */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '20px',
          }}>
            <h2 style={{
              color: industrialTokens.colors.text.primary,
              fontSize: industrialTokens.typography.scale.heading.fontSize,
              fontWeight: industrialTokens.typography.scale.heading.fontWeight,
              textAlign: 'center',
              marginBottom: '10px',
            }}>
              Industrial Design System
            </h2>
            <p style={{
              color: industrialTokens.colors.text.secondary,
              fontSize: industrialTokens.typography.scale.caption.fontSize,
              textAlign: 'center',
              marginBottom: '20px',
              maxWidth: '300px',
            }}>
              Fully integrated with neumorphic design system but may be too subtle for monitoring.
            </p>
            <IndustrialOscilloscope
              complianceScores={complianceScores}
              sweepSpeed={3}
              showLabels={true}
              size="medium"
            />
          </div>
        </div>

        {/* Hybrid Oscilloscope Variations */}
        <div style={{
          marginTop: '60px',
          textAlign: 'center',
        }}>
          <h2 style={{
            color: industrialTokens.colors.text.primary,
            fontSize: industrialTokens.typography.scale.heading.fontSize,
            fontWeight: industrialTokens.typography.scale.heading.fontWeight,
            marginBottom: '30px',
          }}>
            Hybrid Oscilloscope - Size & Intensity Variations
          </h2>
          
          {/* Size Variations */}
          <h3 style={{
            color: industrialTokens.colors.text.secondary,
            fontSize: industrialTokens.typography.scale.subheading.fontSize,
            marginBottom: '20px',
          }}>Size Variations</h3>
          <div style={{
            display: 'flex',
            gap: '30px',
            justifyContent: 'center',
            alignItems: 'center',
            flexWrap: 'wrap',
            marginBottom: '40px',
          }}>
            <div style={{ textAlign: 'center' }}>
              <h4 style={{
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.caption.fontSize,
                marginBottom: '10px',
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
              }}>Small</h4>
              <HybridOscilloscope
                complianceScores={complianceScores}
                size="small"
                showLabels={false}
                intensity="normal"
              />
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <h4 style={{
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.caption.fontSize,
                marginBottom: '10px',
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
              }}>Medium</h4>
              <HybridOscilloscope
                complianceScores={complianceScores}
                size="medium"
                showLabels={true}
                intensity="normal"
              />
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <h4 style={{
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.caption.fontSize,
                marginBottom: '10px',
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
              }}>Large</h4>
              <HybridOscilloscope
                complianceScores={complianceScores}
                size="large"
                showLabels={true}
                intensity="normal"
              />
            </div>
          </div>

          {/* Intensity Variations */}
          <h3 style={{
            color: industrialTokens.colors.text.secondary,
            fontSize: industrialTokens.typography.scale.subheading.fontSize,
            marginBottom: '20px',
          }}>Intensity Variations</h3>
          <div style={{
            display: 'flex',
            gap: '30px',
            justifyContent: 'center',
            alignItems: 'center',
            flexWrap: 'wrap',
          }}>
            <div style={{ textAlign: 'center' }}>
              <h4 style={{
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.caption.fontSize,
                marginBottom: '10px',
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
              }}>Subtle</h4>
              <HybridOscilloscope
                complianceScores={complianceScores}
                size="medium"
                showLabels={true}
                intensity="subtle"
              />
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <h4 style={{
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.caption.fontSize,
                marginBottom: '10px',
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
              }}>Normal</h4>
              <HybridOscilloscope
                complianceScores={complianceScores}
                size="medium"
                showLabels={true}
                intensity="normal"
              />
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <h4 style={{
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.caption.fontSize,
                marginBottom: '10px',
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
              }}>High</h4>
              <HybridOscilloscope
                complianceScores={complianceScores}
                size="medium"
                showLabels={true}
                intensity="high"
              />
            </div>
          </div>
        </div>

        {/* Current Compliance Scores */}
        <div style={{
          marginTop: '60px',
          padding: '30px',
          backgroundColor: industrialTokens.colors.surface.primary,
          borderRadius: '16px',
          boxShadow: '8px 8px 16px #babecc, -8px -8px 16px #ffffff',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        }}>
          <h3 style={{
            color: industrialTokens.colors.text.primary,
            fontSize: industrialTokens.typography.scale.subheading.fontSize,
            fontWeight: industrialTokens.typography.scale.subheading.fontWeight,
            textAlign: 'center',
            marginBottom: '20px',
          }}>
            Current Compliance Scores
          </h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '20px',
            fontFamily: industrialTokens.typography.fontFamily.mono,
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ 
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.label.fontSize,
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
                marginBottom: '5px',
              }}>Typography</div>
              <div style={{ 
                color: industrialTokens.colors.text.primary,
                fontSize: industrialTokens.typography.scale.heading.fontSize,
                fontWeight: '600',
              }}>{(complianceScores.typography * 100).toFixed(1)}%</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ 
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.label.fontSize,
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
                marginBottom: '5px',
              }}>Voice</div>
              <div style={{ 
                color: industrialTokens.colors.text.primary,
                fontSize: industrialTokens.typography.scale.heading.fontSize,
                fontWeight: '600',
              }}>{(complianceScores.voice * 100).toFixed(1)}%</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ 
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.label.fontSize,
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
                marginBottom: '5px',
              }}>Color</div>
              <div style={{ 
                color: industrialTokens.colors.text.primary,
                fontSize: industrialTokens.typography.scale.heading.fontSize,
                fontWeight: '600',
              }}>{(complianceScores.color * 100).toFixed(1)}%</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ 
                color: industrialTokens.colors.text.secondary,
                fontSize: industrialTokens.typography.scale.label.fontSize,
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
                marginBottom: '5px',
              }}>Logo</div>
              <div style={{ 
                color: industrialTokens.colors.text.primary,
                fontSize: industrialTokens.typography.scale.heading.fontSize,
                fontWeight: '600',
              }}>{(complianceScores.logo * 100).toFixed(1)}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DesignComparisonDemo;