/**
 * Industrial Oscilloscope Component
 * 
 * A monitoring component that integrates with the existing industrial design system
 * while providing real-time compliance visualization through a radar chart.
 * Uses neumorphic styling consistent with the current aesthetic.
 */

import React, { useEffect, useRef, useState, useMemo } from 'react';
import { industrialTokens, tokenUtils } from '../../design-system/tokens';
import type { ComplianceScores, MonitoringComponentProps } from '../../types/monitoring';

export interface IndustrialOscilloscopeProps extends MonitoringComponentProps {
  complianceScores: ComplianceScores;
  sweepSpeed?: number;
  showLabels?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const IndustrialOscilloscope: React.FC<IndustrialOscilloscopeProps> = ({
  complianceScores,
  sweepSpeed = 3,
  showLabels = true,
  size = 'medium',
  className = '',
  style = {},
  onError,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const [sweepAngle, setSweepAngle] = useState(0);

  // Size configurations
  const sizeConfig = {
    small: { width: 200, height: 200, viewBox: '0 0 200 200', centerX: 100, centerY: 100, maxRadius: 80 },
    medium: { width: 300, height: 300, viewBox: '0 0 300 300', centerX: 150, centerY: 150, maxRadius: 120 },
    large: { width: 400, height: 400, viewBox: '0 0 400 400', centerX: 200, centerY: 200, maxRadius: 160 },
  };

  const config = sizeConfig[size];

  // Radar chart dimensions and configuration
  const radarConfig = {
    ...config,
    dimensions: [
      { key: 'typography', label: 'TYPOGRAPHY', angle: 0 },
      { key: 'voice', label: 'VOICE', angle: 90 },
      { key: 'color', label: 'COLOR', angle: 180 },
      { key: 'logo', label: 'LOGO', angle: 270 },
    ],
  };

  // Calculate radar polygon points
  const calculateRadarPoints = (scores: ComplianceScores): string => {
    const points = radarConfig.dimensions.map(dim => {
      const score = scores[dim.key as keyof ComplianceScores];
      const radius = score * radarConfig.maxRadius;
      const angleRad = (dim.angle * Math.PI) / 180;
      const x = radarConfig.centerX + radius * Math.cos(angleRad);
      const y = radarConfig.centerY + radius * Math.sin(angleRad);
      return `${x},${y}`;
    });
    return points.join(' ');
  };

  // Generate concentric circles for radar grid
  const generateRadarGrid = () => {
    const circles = [];
    for (let i = 1; i <= 4; i++) {
      const radius = (radarConfig.maxRadius / 4) * i;
      circles.push(
        <circle
          key={i}
          cx={radarConfig.centerX}
          cy={radarConfig.centerY}
          r={radius}
          fill="none"
          stroke={industrialTokens.colors.text.muted}
          strokeWidth="1"
          opacity={0.3}
        />
      );
    }
    return circles;
  };

  // Generate radar axis lines
  const generateRadarAxes = () => {
    return radarConfig.dimensions.map(dim => {
      const angleRad = (dim.angle * Math.PI) / 180;
      const endX = radarConfig.centerX + radarConfig.maxRadius * Math.cos(angleRad);
      const endY = radarConfig.centerY + radarConfig.maxRadius * Math.sin(angleRad);
      
      return (
        <g key={dim.key}>
          <line
            x1={radarConfig.centerX}
            y1={radarConfig.centerY}
            x2={endX}
            y2={endY}
            stroke={industrialTokens.colors.text.secondary}
            strokeWidth="1"
            opacity={0.5}
          />
          {showLabels && (
            <text
              x={radarConfig.centerX + (radarConfig.maxRadius + 20) * Math.cos(angleRad)}
              y={radarConfig.centerY + (radarConfig.maxRadius + 20) * Math.sin(angleRad)}
              fill={industrialTokens.colors.text.primary}
              fontSize={size === 'small' ? '8' : size === 'medium' ? '10' : '12'}
              fontFamily={industrialTokens.typography.fontFamily.mono}
              textAnchor="middle"
              dominantBaseline="middle"
              style={{
                textTransform: 'uppercase',
                letterSpacing: '0.025em',
                fontWeight: '500',
              }}
            >
              {dim.label}
            </text>
          )}
        </g>
      );
    });
  };

  // Sweep line animation
  useEffect(() => {
    const animateSweep = () => {
      setSweepAngle(prev => (prev + 1) % 360);
    };

    const interval = setInterval(animateSweep, sweepSpeed * 20);
    return () => clearInterval(interval);
  }, [sweepSpeed]);

  // Calculate sweep line coordinates
  const sweepLineCoords = useMemo(() => {
    const angleRad = (sweepAngle * Math.PI) / 180;
    return {
      x2: radarConfig.centerX + radarConfig.maxRadius * Math.cos(angleRad),
      y2: radarConfig.centerY + radarConfig.maxRadius * Math.sin(angleRad),
    };
  }, [sweepAngle, radarConfig]);

  // Get compliance color based on score
  const getComplianceColor = (score: number) => {
    if (score >= 0.8) return industrialTokens.colors.led.on;
    if (score >= 0.6) return industrialTokens.colors.led.warning;
    return industrialTokens.colors.led.error;
  };

  // Calculate overall compliance score
  const overallScore = (complianceScores.typography + complianceScores.voice + complianceScores.color + complianceScores.logo) / 4;

  return (
    <div
      ref={containerRef}
      className={`industrial-oscilloscope ${className}`}
      style={{
        width: `${config.width}px`,
        height: `${config.height}px`,
        background: industrialTokens.colors.surface.primary,
        borderRadius: '16px',
        boxShadow: tokenUtils.getShadow('normal', 'recessed'),
        border: '1px solid rgba(255, 255, 255, 0.2)',
        position: 'relative',
        overflow: 'hidden',
        ...style,
      }}
    >
      {/* Main display area */}
      <div
        style={{
          position: 'absolute',
          inset: '12px',
          background: industrialTokens.colors.surface.secondary,
          borderRadius: '12px',
          boxShadow: tokenUtils.getShadow('subtle', 'recessed'),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* SVG Radar Chart */}
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          viewBox={config.viewBox}
          style={{
            maxWidth: '100%',
            maxHeight: '100%',
          }}
        >
          {/* Radar Grid */}
          {generateRadarGrid()}
          
          {/* Radar Axes */}
          {generateRadarAxes()}
          
          {/* Compliance Score Polygon */}
          <polygon
            points={calculateRadarPoints(complianceScores)}
            fill={getComplianceColor(overallScore)}
            fillOpacity={0.15}
            stroke={getComplianceColor(overallScore)}
            strokeWidth="2"
            style={{
              transition: 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
              filter: `drop-shadow(0 0 4px ${getComplianceColor(overallScore)}40)`,
            }}
          />
          
          {/* Sweep Line */}
          <line
            x1={radarConfig.centerX}
            y1={radarConfig.centerY}
            x2={sweepLineCoords.x2}
            y2={sweepLineCoords.y2}
            stroke={industrialTokens.colors.led.off}
            strokeWidth="1"
            opacity={0.6}
            style={{
              transition: 'all 0.1s linear',
            }}
          />
          
          {/* Center Dot */}
          <circle
            cx={radarConfig.centerX}
            cy={radarConfig.centerY}
            r="2"
            fill={industrialTokens.colors.text.primary}
          />
          
          {/* Score Values */}
          {showLabels && radarConfig.dimensions.map((dim, index) => {
            const score = complianceScores[dim.key as keyof ComplianceScores];
            const angleRad = (dim.angle * Math.PI) / 180;
            const textX = radarConfig.centerX + (radarConfig.maxRadius + 35) * Math.cos(angleRad);
            const textY = radarConfig.centerY + (radarConfig.maxRadius + 35) * Math.sin(angleRad);
            
            return (
              <text
                key={`score-${dim.key}`}
                x={textX}
                y={textY}
                fill={getComplianceColor(score)}
                fontSize={size === 'small' ? '10' : size === 'medium' ? '12' : '14'}
                fontFamily={industrialTokens.typography.fontFamily.mono}
                textAnchor="middle"
                dominantBaseline="middle"
                fontWeight="600"
              >
                {(score * 100).toFixed(0)}%
              </text>
            );
          })}
        </svg>
      </div>

      {/* Status LED indicator */}
      <div
        style={{
          position: 'absolute',
          top: '8px',
          right: '8px',
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: getComplianceColor(overallScore),
          boxShadow: `0 0 8px ${getComplianceColor(overallScore)}`,
          animation: overallScore < 0.6 ? 'pulse 1s infinite' : 'none',
        }}
      />

      {/* Subtle scanline texture overlay (matching existing RecessedScreen) */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(rgba(18,16,16,0) 50%, rgba(0,0,0,0.02) 50%)',
          backgroundSize: '100% 4px',
          pointerEvents: 'none',
          opacity: 0.1,
          borderRadius: '16px',
        }}
        aria-hidden="true"
      />

      {/* CSS for pulse animation - injected globally */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `
      }} />
    </div>
  );
};

export default IndustrialOscilloscope;