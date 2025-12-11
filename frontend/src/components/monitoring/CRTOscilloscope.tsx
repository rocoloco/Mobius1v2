/**
 * CRT Oscilloscope Component
 * 
 * Displays compliance scores as an animated radar chart with authentic CRT aesthetics.
 * Features phosphor green styling, scanline overlays, and smooth 60fps animations.
 */

import React, { useEffect, useRef, useState, useMemo } from 'react';
import { 
  generateCRTStyles, 
  crtSVGFilters, 
  CRTPerformanceOptimizer, 
  injectCRTStyles,
  defaultCRTConfig,
  type CRTEffectsConfig 
} from './CRTEffects';

export interface ComplianceScores {
  typography: number;    // 0-1 compliance score
  voice: number;        // 0-1 compliance score
  color: number;        // 0-1 compliance score
  logo: number;         // 0-1 compliance score
}

export interface CRTOscilloscopeProps {
  complianceScores: ComplianceScores;
  sweepSpeed?: number;
  phosphorIntensity?: number;
  scanlineOpacity?: number;
  className?: string;
  style?: React.CSSProperties;
  onError?: (error: Error) => void;
}

const CRTOscilloscope: React.FC<CRTOscilloscopeProps> = ({
  complianceScores,
  sweepSpeed = 3,
  phosphorIntensity = 0.8,
  scanlineOpacity = 0.1,
  className = '',
  style = {},
  onError,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const performanceMonitor = useRef<CRTPerformanceOptimizer>(new CRTPerformanceOptimizer());
  const [currentFPS, setCurrentFPS] = useState(60);
  const [sweepAngle, setSweepAngle] = useState(0);

  // Industrial configuration - blue theme to match design system
  const crtConfig: CRTEffectsConfig = useMemo(() => ({
    ...defaultCRTConfig,
    phosphorColor: '#3b82f6', // Blue instead of green
    scanlineOpacity: scanlineOpacity * 0.3, // Much more subtle
    glowIntensity: phosphorIntensity * 0.4, // Reduced glow
    noiseLevel: 0.01, // Minimal noise
    flickerIntensity: 0.005, // Minimal flicker
  }), [scanlineOpacity, phosphorIntensity]);

  // Generate CRT styles
  const crtStyles = useMemo(() => generateCRTStyles(crtConfig), [crtConfig]);

  // Radar chart dimensions and configuration
  const radarConfig = {
    centerX: 150,
    centerY: 150,
    maxRadius: 120,
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
          stroke={crtConfig.phosphorColor}
          strokeWidth="1"
          opacity={0.3}
          filter="url(#phosphor-glow)"
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
            stroke={crtConfig.phosphorColor}
            strokeWidth="1"
            opacity={0.5}
            filter="url(#phosphor-glow)"
          />
          <text
            x={radarConfig.centerX + (radarConfig.maxRadius + 20) * Math.cos(angleRad)}
            y={radarConfig.centerY + (radarConfig.maxRadius + 20) * Math.sin(angleRad)}
            fill={crtConfig.phosphorColor}
            fontSize="10"
            fontFamily="JetBrains Mono, monospace"
            textAnchor="middle"
            dominantBaseline="middle"
            filter="url(#phosphor-glow)"
          >
            {dim.label}
          </text>
        </g>
      );
    });
  };

  // Sweep line animation
  useEffect(() => {
    const animateSweep = () => {
      setSweepAngle(prev => (prev + 2) % 360);
    };

    const interval = setInterval(animateSweep, sweepSpeed * 10);
    return () => clearInterval(interval);
  }, [sweepSpeed]);

  // Initialize CRT effects and performance monitoring
  useEffect(() => {
    try {
      injectCRTStyles();
      
      performanceMonitor.current.startPerformanceMonitoring((fps) => {
        setCurrentFPS(fps);
        if (fps < 30 && onError) {
          onError(new Error(`Performance degradation detected: ${fps} FPS`));
        }
      });

      return () => {
        performanceMonitor.current.stopPerformanceMonitoring();
      };
    } catch (error) {
      if (onError) {
        onError(error as Error);
      }
    }
  }, [onError]);

  // Calculate sweep line coordinates
  const sweepLineCoords = useMemo(() => {
    const angleRad = (sweepAngle * Math.PI) / 180;
    return {
      x2: radarConfig.centerX + radarConfig.maxRadius * Math.cos(angleRad),
      y2: radarConfig.centerY + radarConfig.maxRadius * Math.sin(angleRad),
    };
  }, [sweepAngle]);

  return (
    <div
      ref={containerRef}
      className={`crt-oscilloscope ${className}`}
      style={{
        ...crtStyles.crtContainer,
        width: '300px',
        height: '300px',
        ...style,
      }}
    >
      {/* Phosphor screen */}
      <div style={crtStyles.phosphorScreen}>
        {/* SVG Radar Chart */}
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          viewBox="0 0 300 300"
          style={crtStyles.glowContent}
        >
          {/* SVG Filters */}
          <defs dangerouslySetInnerHTML={{ __html: crtSVGFilters }} />
          
          {/* Radar Grid */}
          {generateRadarGrid()}
          
          {/* Radar Axes */}
          {generateRadarAxes()}
          
          {/* Compliance Score Polygon */}
          <polygon
            points={calculateRadarPoints(complianceScores)}
            fill={crtConfig.phosphorColor}
            fillOpacity={0.2}
            stroke={crtConfig.phosphorColor}
            strokeWidth="2"
            filter="url(#phosphor-glow)"
            style={{
              transition: 'points 0.5s ease-in-out',
            }}
          />
          
          {/* Sweep Line */}
          <line
            x1={radarConfig.centerX}
            y1={radarConfig.centerY}
            x2={sweepLineCoords.x2}
            y2={sweepLineCoords.y2}
            stroke={crtConfig.phosphorColor}
            strokeWidth="2"
            opacity={0.8}
            filter="url(#phosphor-glow)"
            style={{
              transition: 'all 0.1s linear',
            }}
          />
          
          {/* Center Dot */}
          <circle
            cx={radarConfig.centerX}
            cy={radarConfig.centerY}
            r="3"
            fill={crtConfig.phosphorColor}
            filter="url(#phosphor-glow)"
          />
          
          {/* Score Values */}
          {radarConfig.dimensions.map((dim, index) => {
            const score = complianceScores[dim.key as keyof ComplianceScores];
            const angleRad = (dim.angle * Math.PI) / 180;
            const textX = radarConfig.centerX + (radarConfig.maxRadius + 40) * Math.cos(angleRad);
            const textY = radarConfig.centerY + (radarConfig.maxRadius + 40) * Math.sin(angleRad);
            
            return (
              <text
                key={`score-${dim.key}`}
                x={textX}
                y={textY}
                fill={crtConfig.phosphorColor}
                fontSize="12"
                fontFamily="JetBrains Mono, monospace"
                textAnchor="middle"
                dominantBaseline="middle"
                filter="url(#phosphor-glow)"
              >
                {(score * 100).toFixed(0)}%
              </text>
            );
          })}
        </svg>
        
        {/* Performance indicator */}
        <div
          style={{
            position: 'absolute',
            bottom: '8px',
            right: '8px',
            fontSize: '10px',
            color: crtConfig.phosphorColor,
            fontFamily: 'JetBrains Mono, monospace',
            opacity: 0.6,
          }}
        >
          {currentFPS} FPS
        </div>
      </div>
      
      {/* Scanlines overlay */}
      <div className="crt-scanlines" style={crtStyles.scanlines} />
      
      {/* CRT noise overlay */}
      <div style={crtStyles.noiseOverlay} />
    </div>
  );
};

export default CRTOscilloscope;