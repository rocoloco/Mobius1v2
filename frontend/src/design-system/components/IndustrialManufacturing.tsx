/**
 * Industrial Manufacturing Details
 * 
 * Professional-grade manufacturing elements using SVG patterns and realistic textures
 */

import React from 'react';

interface ManufacturingProps {
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Professional Vent Grille Component
 */
export const VentGrille: React.FC<ManufacturingProps & { 
  orientation?: 'horizontal' | 'vertical';
  density?: 'sparse' | 'normal' | 'dense';
}> = ({ 
  className = '', 
  style = {},
  orientation = 'horizontal', // Currently only horizontal is implemented
  density = 'normal'
}) => {
  // Note: orientation parameter reserved for future vertical implementation
  void orientation; // Suppress unused parameter warning
  const slotCount = density === 'sparse' ? 8 : density === 'normal' ? 12 : 16;
  const slotSpacing = 100 / slotCount;

  return (
    <div className={className} style={{ position: 'relative', ...style }}>
      <svg 
        width="100%" 
        height="100%" 
        viewBox="0 0 100 20" 
        preserveAspectRatio="none"
        style={{ display: 'block' }}
      >
        <defs>
          <linearGradient id="ventGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(0,0,0,0.4)" />
            <stop offset="50%" stopColor="rgba(0,0,0,0.2)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.1)" />
          </linearGradient>
          
          <filter id="ventShadow">
            <feDropShadow dx="0" dy="1" stdDeviation="0.5" floodColor="rgba(0,0,0,0.3)" />
          </filter>
        </defs>
        
        {/* Background panel */}
        <rect 
          width="100" 
          height="20" 
          fill="#d1d9e6" 
          stroke="rgba(0,0,0,0.1)" 
          strokeWidth="0.5"
        />
        
        {/* Vent slots */}
        {Array.from({ length: slotCount }, (_, i) => (
          <rect
            key={i}
            x={i * slotSpacing + 2}
            y="4"
            width={slotSpacing * 0.6}
            height="12"
            fill="url(#ventGradient)"
            rx="1"
            filter="url(#ventShadow)"
          />
        ))}
        
        {/* Rim highlight */}
        <rect 
          width="100" 
          height="20" 
          fill="none" 
          stroke="rgba(255,255,255,0.3)" 
          strokeWidth="0.5"
        />
      </svg>
    </div>
  );
};

/**
 * Industrial Connector Port
 */
export const ConnectorPort: React.FC<ManufacturingProps & {
  type?: 'ethernet' | 'usb' | 'power' | 'data';
  size?: 'sm' | 'md' | 'lg';
}> = ({ 
  className = '', 
  style = {},
  type = 'data',
  size = 'md'
}) => {
  const dimensions = {
    sm: { width: 16, height: 8 },
    md: { width: 24, height: 12 },
    lg: { width: 32, height: 16 },
  };

  const { width, height } = dimensions[size];

  const getPortColor = () => {
    switch (type) {
      case 'ethernet': return '#ff6b35';
      case 'usb': return '#4a90e2';
      case 'power': return '#f39c12';
      default: return '#6c7b7f';
    }
  };

  return (
    <div className={className} style={{ position: 'relative', ...style }}>
      <svg 
        width={width} 
        height={height} 
        viewBox="0 0 24 12" 
        style={{ display: 'block' }}
      >
        <defs>
          <linearGradient id="portGradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={getPortColor()} />
            <stop offset="100%" stopColor="#2c3e50" />
          </linearGradient>
          
          <filter id="portInset">
            <feOffset dx="0" dy="1" />
            <feGaussianBlur stdDeviation="1" />
            <feComposite operator="over" />
          </filter>
        </defs>
        
        {/* Port housing */}
        <rect 
          x="2" 
          y="2" 
          width="20" 
          height="8" 
          fill="url(#portGradient)"
          rx="1"
          stroke="rgba(0,0,0,0.4)"
          strokeWidth="0.5"
          filter="url(#portInset)"
        />
        
        {/* Port opening */}
        <rect 
          x="4" 
          y="4" 
          width="16" 
          height="4" 
          fill="rgba(0,0,0,0.8)"
          rx="0.5"
        />
        
        {/* Connection pins/contacts */}
        {type === 'ethernet' && (
          <>
            <rect x="6" y="5" width="1" height="2" fill="#ffd700" />
            <rect x="8" y="5" width="1" height="2" fill="#ffd700" />
            <rect x="10" y="5" width="1" height="2" fill="#ffd700" />
            <rect x="12" y="5" width="1" height="2" fill="#ffd700" />
            <rect x="14" y="5" width="1" height="2" fill="#ffd700" />
            <rect x="16" y="5" width="1" height="2" fill="#ffd700" />
            <rect x="18" y="5" width="1" height="2" fill="#ffd700" />
          </>
        )}
        
        {/* Status LED */}
        <circle 
          cx="20" 
          cy="3" 
          r="0.8" 
          fill={type === 'power' ? '#00ff00' : '#ff4757'}
          opacity="0.8"
        />
      </svg>
    </div>
  );
};

/**
 * Industrial Surface Texture Generator
 */
export const SurfaceTexture: React.FC<ManufacturingProps & {
  pattern?: 'brushed' | 'diamond-plate' | 'perforated' | 'carbon-fiber';
  intensity?: number;
}> = ({ 
  className = '', 
  style = {},
  pattern = 'brushed',
  intensity = 0.3
}) => {
  const getPatternSVG = () => {
    switch (pattern) {
      case 'diamond-plate':
        return (
          <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0 }}>
            <defs>
              <pattern id="diamondPlate" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                <rect width="20" height="20" fill="rgba(255,255,255,0.05)" />
                <polygon 
                  points="10,2 18,10 10,18 2,10" 
                  fill="rgba(255,255,255,0.1)" 
                  stroke="rgba(0,0,0,0.1)" 
                  strokeWidth="0.5"
                />
                <polygon 
                  points="10,4 16,10 10,16 4,10" 
                  fill="rgba(255,255,255,0.05)" 
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#diamondPlate)" opacity={intensity} />
          </svg>
        );
      
      case 'perforated':
        return (
          <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0 }}>
            <defs>
              <pattern id="perforated" x="0" y="0" width="12" height="12" patternUnits="userSpaceOnUse">
                <rect width="12" height="12" fill="rgba(255,255,255,0.02)" />
                <circle 
                  cx="6" 
                  cy="6" 
                  r="2" 
                  fill="rgba(0,0,0,0.2)" 
                  stroke="rgba(0,0,0,0.1)" 
                  strokeWidth="0.5"
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#perforated)" opacity={intensity} />
          </svg>
        );
      
      case 'carbon-fiber':
        return (
          <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0 }}>
            <defs>
              <pattern id="carbonFiber" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
                <rect width="8" height="8" fill="#1a1a1a" />
                <rect x="0" y="0" width="4" height="4" fill="#2a2a2a" />
                <rect x="4" y="4" width="4" height="4" fill="#2a2a2a" />
                <rect x="0" y="0" width="8" height="1" fill="rgba(255,255,255,0.1)" />
                <rect x="0" y="4" width="8" height="1" fill="rgba(255,255,255,0.05)" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#carbonFiber)" opacity={intensity} />
          </svg>
        );
      
      default: // brushed
        return (
          <div 
            style={{
              position: 'absolute',
              inset: 0,
              background: `linear-gradient(90deg, 
                rgba(255,255,255,${intensity * 0.3}) 0%, 
                rgba(255,255,255,${intensity * 0.1}) 50%, 
                rgba(255,255,255,${intensity * 0.3}) 100%
              )`,
              backgroundSize: '4px 100%',
            }}
          />
        );
    }
  };

  return (
    <div className={className} style={{ position: 'relative', ...style }}>
      {getPatternSVG()}
    </div>
  );
};

/**
 * Industrial Warning Label
 */
export const WarningLabel: React.FC<ManufacturingProps & {
  text?: string;
  type?: 'caution' | 'danger' | 'warning' | 'notice';
}> = ({ 
  className = '', 
  style = {},
  text = 'CAUTION',
  type = 'caution'
}) => {
  const getColors = () => {
    switch (type) {
      case 'danger': return { bg: '#ff4757', text: '#ffffff' };
      case 'warning': return { bg: '#ffa502', text: '#000000' };
      case 'notice': return { bg: '#3742fa', text: '#ffffff' };
      default: return { bg: '#fffa65', text: '#000000' };
    }
  };

  const colors = getColors();

  return (
    <div 
      className={`px-2 py-1 text-xs font-bold uppercase tracking-wider ${className}`}
      style={{
        backgroundColor: colors.bg,
        color: colors.text,
        border: '1px solid rgba(0,0,0,0.2)',
        borderRadius: '2px',
        boxShadow: '0 1px 2px rgba(0,0,0,0.2)',
        fontFamily: 'monospace',
        ...style,
      }}
    >
      {text}
    </div>
  );
};

/**
 * Industrial Serial Number Plate
 */
export const SerialPlate: React.FC<ManufacturingProps & {
  serialNumber?: string;
  model?: string;
}> = ({ 
  className = '', 
  style = {},
  serialNumber = 'SN: 2024-IND-001',
  model = 'Model: MX-2000'
}) => {
  return (
    <div 
      className={`p-2 text-xs font-mono ${className}`}
      style={{
        backgroundColor: '#e8e8e8',
        border: '1px solid #999',
        borderRadius: '2px',
        boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.1)',
        color: '#333',
        lineHeight: 1.2,
        ...style,
      }}
    >
      <div>{model}</div>
      <div>{serialNumber}</div>
      <div style={{ fontSize: '10px', color: '#666' }}>CE • UL • FCC</div>
    </div>
  );
};

export default VentGrille;