/**
 * Hybrid Oscilloscope Component
 * 
 * A middle ground between CRT and Industrial styles that maintains design system
 * consistency while providing clear, engaging monitoring visualization.
 * Features enhanced contrast and visibility while respecting the neumorphic aesthetic.
 */

import React, { useEffect, useRef, useState, useMemo } from 'react';
import { industrialTokens, tokenUtils } from '../../design-system/tokens';
import type { ComplianceScores, MonitoringComponentProps } from '../../types/monitoring';

export interface HybridOscilloscopeProps extends MonitoringComponentProps {
  complianceScores: ComplianceScores;
  sweepSpeed?: number;
  showLabels?: boolean;
  size?: 'small' | 'medium' | 'large';
  intensity?: 'subtle' | 'normal' | 'high';
}

const HybridOscilloscope: React.FC<HybridOscilloscopeProps> = ({
  complianceScores,
  sweepSpeed = 3,
  showLabels = true,
  size = 'medium',
  intensity = 'normal',
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

  // Intensity configurations for enhanced visibility
  const intensityConfig = {
    subtle: {
      screenBg: '#2a3441',
      gridOpacity: 0.4,
      sweepOpacity: 0.7,
      glowIntensity: 0.5,
      scanlineOpacity: 0.06,
    },
    normal: {
      screenBg: '#1e2832',
      gridOpacity: 0.6,
      sweepOpacity: 0.9,
      glowIntensity: 0.7,
      scanlineOpacity: 0.1,
    },
    high: {
      screenBg: '#0f1419',
      gridOpacity: 0.8,
      sweepOpacity: 1.0,
      glowIntensity: 0.9,
      scanlineOpacity: 0.15,
    },
  };

  const config = sizeConfig[size];
  const intensitySettings = intensityConfig[intensity];

  // Enhanced color system - more vibrant while respecting design tokens
  const monitoringColors = {
    primary: '#00ff88',      // Brighter green for better visibility
    secondary: '#66b3ff',    // Brighter blue for sweep line
    warning: '#ffdd44',      // Brighter yellow
    error: '#ff7777',        // Brighter red
    grid: '#4a90e2',         // Brighter grid color
    text: '#ffffff',         // Pure white text for maximum contrast
  };

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
          stroke={monitoringColors.grid}
          strokeWidth="2"
          opacity={intensitySettings.gridOpacity}
          filter="url(#monitor-glow)"
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
            stroke={monitoringColors.grid}
            strokeWidth="2"
            opacity={intensitySettings.gridOpacity}
            filter="url(#monitor-glow)"
          />
          {showLabels && (
            <text
              x={radarConfig.centerX + (radarConfig.maxRadius + 20) * Math.cos(angleRad)}
              y={radarConfig.centerY + (radarConfig.maxRadius + 20) * Math.sin(angleRad)}
              fill={monitoringColors.text}
              fontSize={size === 'small' ? '8' : size === 'medium' ? '10' : '12'}
              fontFamily={industrialTokens.typography.fontFamily.mono}
              textAnchor="middle"
              dominantBaseline="middle"
              filter="url(#text-glow)"
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
    if (score >= 0.8) return monitoringColors.primary;
    if (score >= 0.6) return monitoringColors.warning;
    return monitoringColors.error;
  };

  // Calculate overall compliance score
  const overallScore = (complianceScores.typography + complianceScores.voice + complianceScores.color + complianceScores.logo) / 4;

  return (
    <div
      ref={containerRef}
      className={`
        hybrid-oscilloscope
        bg-surface
        rounded-2xl
        shadow-soft
        overflow-hidden
        relative
        border border-white/20
        ${className}
      `}
      style={{
        width: `${config.width}px`,
        height: `${config.height}px`,
        position: 'relative',
        ...style,
      }}
    >
      {/* Enhanced monitor screen with better contrast */}
      <div
        className="
          absolute inset-3
          rounded-xl
          shadow-recessed
          border border-white/10
          flex items-center justify-center
          overflow-hidden
        "
        style={{
          background: `linear-gradient(135deg, ${intensitySettings.screenBg} 0%, ${intensitySettings.screenBg}dd 100%)`,
        }}
      >
        {/* SVG Radar Chart with enhanced visibility */}
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
          {/* Enhanced SVG filters */}
          <defs>
            <filter id="monitor-glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge> 
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            <filter id="text-glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge> 
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            <filter id="sweep-glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge> 
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Radar Grid */}
          {generateRadarGrid()}
          
          {/* Radar Axes */}
          {generateRadarAxes()}
          
          {/* Compliance Score Polygon with enhanced visibility */}
          <polygon
            points={calculateRadarPoints(complianceScores)}
            fill={getComplianceColor(overallScore)}
            fillOpacity={0.4}
            stroke={getComplianceColor(overallScore)}
            strokeWidth="3"
            filter="url(#monitor-glow)"
            style={{
              transition: 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
            }}
          />
          
          {/* Enhanced Sweep Line */}
          <line
            x1={radarConfig.centerX}
            y1={radarConfig.centerY}
            x2={sweepLineCoords.x2}
            y2={sweepLineCoords.y2}
            stroke={monitoringColors.secondary}
            strokeWidth="3"
            opacity={intensitySettings.sweepOpacity}
            filter="url(#sweep-glow)"
            style={{
              transition: 'all 0.1s linear',
            }}
          />
          
          {/* Center Dot with glow */}
          <circle
            cx={radarConfig.centerX}
            cy={radarConfig.centerY}
            r="4"
            fill={monitoringColors.primary}
            filter="url(#monitor-glow)"
          />
          
          {/* Score Values with enhanced visibility */}
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
                filter="url(#text-glow)"
              >
                {(score * 100).toFixed(0)}%
              </text>
            );
          })}
        </svg>
      </div>

      {/* Enhanced status LED indicator */}
      <div
        className={`
          absolute top-2 right-2 w-3 h-3
          led-indicator
          ${overallScore < 0.6 ? 'animate-led-pulse' : ''}
        `}
        style={{
          backgroundColor: getComplianceColor(overallScore),
          boxShadow: `0 0 12px ${getComplianceColor(overallScore)}, 0 0 24px ${getComplianceColor(overallScore)}40`,
        }}
      />

      {/* Enhanced scanline texture overlay */}
      <div
        className="
          absolute inset-3
          rounded-xl
          pointer-events-none
          animate-pulse
        "
        style={{
          background: `
            linear-gradient(
              0deg,
              transparent 0%,
              rgba(0, 212, 170, ${intensitySettings.scanlineOpacity}) 1px,
              transparent 2px,
              transparent 100%
            )
          `,
          backgroundSize: '100% 4px',
          animation: 'scanline-drift 3s infinite linear',
        }}
        aria-hidden="true"
      />

      {/* Manufacturing screws for authentic industrial look */}
      <div className="screw screw-tl" aria-hidden="true" />
      <div className="screw screw-tr" aria-hidden="true" />
      <div className="screw screw-bl" aria-hidden="true" />
      <div className="screw screw-br" aria-hidden="true" />

      {/* Subtle outer glow for the entire component */}
      <div
        className="absolute -inset-0.5 rounded-2xl pointer-events-none -z-10"
        style={{
          background: `radial-gradient(ellipse at center, ${getComplianceColor(overallScore)}10 0%, transparent 70%)`,
        }}
        aria-hidden="true"
      />

      {/* CSS animations */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes scanline-drift {
            0% { transform: translateY(0px); }
            100% { transform: translateY(4px); }
          }
        `
      }} />
    </div>
  );
};

export default HybridOscilloscope;