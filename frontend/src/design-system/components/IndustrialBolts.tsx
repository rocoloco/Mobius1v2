/**
 * Industrial Bolt Components
 * 
 * Photorealistic SVG-based screw head components with proper industrial styling
 */

import React from 'react';

interface BoltProps {
  className?: string;
  style?: React.CSSProperties;
  size?: number;
}

/**
 * Phillips Head Bolt - Photorealistic SVG implementation
 */
export const PhillipsHeadBolt: React.FC<BoltProps> = ({ 
  className = '', 
  style = {},
  size = 12
}) => {
  return (
    <div className={className} style={{ position: 'relative', ...style }}>
      <svg 
        width={size} 
        height={size} 
        viewBox="0 0 24 24" 
        style={{ display: 'block' }}
      >
        <defs>
          {/* Metallic gradient for bolt body */}
          <radialGradient id="boltGradient" cx="0.3" cy="0.3" r="0.8">
            <stop offset="0%" stopColor="#c8d4e1" />
            <stop offset="40%" stopColor="#a8b5c7" />
            <stop offset="70%" stopColor="#8e9aaf" />
            <stop offset="100%" stopColor="#6c7b7f" />
          </radialGradient>
          
          {/* Shadow gradient for depth */}
          <radialGradient id="shadowGradient" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0%" stopColor="rgba(0,0,0,0.1)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.3)" />
          </radialGradient>
          
          {/* Cross slot gradient */}
          <linearGradient id="slotGradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="rgba(0,0,0,0.8)" />
            <stop offset="50%" stopColor="rgba(0,0,0,0.6)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.4)" />
          </linearGradient>
        </defs>
        
        {/* Drop shadow */}
        <circle 
          cx="12.5" 
          cy="12.5" 
          r="10" 
          fill="url(#shadowGradient)" 
          opacity="0.3"
        />
        
        {/* Main bolt body */}
        <circle 
          cx="12" 
          cy="12" 
          r="10" 
          fill="url(#boltGradient)"
          stroke="#5a6b70"
          strokeWidth="0.5"
        />
        
        {/* Rim highlight */}
        <circle 
          cx="12" 
          cy="12" 
          r="9.5" 
          fill="none"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth="0.5"
        />
        
        {/* Phillips cross - vertical slot */}
        <rect 
          x="11.2" 
          y="5" 
          width="1.6" 
          height="14" 
          fill="url(#slotGradient)"
          rx="0.3"
        />
        
        {/* Phillips cross - horizontal slot */}
        <rect 
          x="5" 
          y="11.2" 
          width="14" 
          height="1.6" 
          fill="url(#slotGradient)"
          rx="0.3"
        />
        
        {/* Inner shadow for slots */}
        <rect 
          x="11.3" 
          y="5.2" 
          width="1.4" 
          height="13.6" 
          fill="none"
          stroke="rgba(0,0,0,0.3)"
          strokeWidth="0.2"
          rx="0.2"
        />
        <rect 
          x="5.2" 
          y="11.3" 
          width="13.6" 
          height="1.4" 
          fill="none"
          stroke="rgba(0,0,0,0.3)"
          strokeWidth="0.2"
          rx="0.2"
        />
      </svg>
    </div>
  );
};

/**
 * Flathead Bolt - Single slot design
 */
export const FlatheadBolt: React.FC<BoltProps> = ({ 
  className = '', 
  style = {},
  size = 12
}) => {
  return (
    <div className={className} style={{ position: 'relative', ...style }}>
      <svg 
        width={size} 
        height={size} 
        viewBox="0 0 24 24" 
        style={{ display: 'block' }}
      >
        <defs>
          <radialGradient id="flatheadGradient" cx="0.3" cy="0.3" r="0.8">
            <stop offset="0%" stopColor="#c8d4e1" />
            <stop offset="40%" stopColor="#a8b5c7" />
            <stop offset="70%" stopColor="#8e9aaf" />
            <stop offset="100%" stopColor="#6c7b7f" />
          </radialGradient>
          
          <linearGradient id="flatSlotGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(0,0,0,0.8)" />
            <stop offset="50%" stopColor="rgba(0,0,0,0.6)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.4)" />
          </linearGradient>
        </defs>
        
        {/* Drop shadow */}
        <circle cx="12.5" cy="12.5" r="10" fill="rgba(0,0,0,0.2)" opacity="0.3" />
        
        {/* Main bolt body */}
        <circle 
          cx="12" 
          cy="12" 
          r="10" 
          fill="url(#flatheadGradient)"
          stroke="#5a6b70"
          strokeWidth="0.5"
        />
        
        {/* Rim highlight */}
        <circle 
          cx="12" 
          cy="12" 
          r="9.5" 
          fill="none"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth="0.5"
        />
        
        {/* Single horizontal slot */}
        <rect 
          x="4" 
          y="11" 
          width="16" 
          height="2" 
          fill="url(#flatSlotGradient)"
          rx="0.5"
        />
        
        {/* Slot inner shadow */}
        <rect 
          x="4.2" 
          y="11.2" 
          width="15.6" 
          height="1.6" 
          fill="none"
          stroke="rgba(0,0,0,0.4)"
          strokeWidth="0.2"
          rx="0.3"
        />
      </svg>
    </div>
  );
};

/**
 * Torx (Star) Head Bolt - 6-point star design
 */
export const TorxHeadBolt: React.FC<BoltProps> = ({ 
  className = '', 
  style = {},
  size = 12
}) => {
  return (
    <div className={className} style={{ position: 'relative', ...style }}>
      <svg 
        width={size} 
        height={size} 
        viewBox="0 0 24 24" 
        style={{ display: 'block' }}
      >
        <defs>
          <radialGradient id="torxGradient" cx="0.3" cy="0.3" r="0.8">
            <stop offset="0%" stopColor="#c8d4e1" />
            <stop offset="40%" stopColor="#a8b5c7" />
            <stop offset="70%" stopColor="#8e9aaf" />
            <stop offset="100%" stopColor="#6c7b7f" />
          </radialGradient>
          
          <radialGradient id="starGradient" cx="0.5" cy="0.5" r="0.6">
            <stop offset="0%" stopColor="rgba(0,0,0,0.7)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.9)" />
          </radialGradient>
        </defs>
        
        {/* Drop shadow */}
        <circle cx="12.5" cy="12.5" r="10" fill="rgba(0,0,0,0.2)" opacity="0.3" />
        
        {/* Main bolt body */}
        <circle 
          cx="12" 
          cy="12" 
          r="10" 
          fill="url(#torxGradient)"
          stroke="#5a6b70"
          strokeWidth="0.5"
        />
        
        {/* Rim highlight */}
        <circle 
          cx="12" 
          cy="12" 
          r="9.5" 
          fill="none"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth="0.5"
        />
        
        {/* 6-point Torx star */}
        <path 
          d="M12 7 L13.5 9.5 L16 9 L14.5 11.5 L16 14 L13.5 13.5 L12 16 L10.5 13.5 L8 14 L9.5 11.5 L8 9 L10.5 9.5 Z" 
          fill="url(#starGradient)"
          stroke="rgba(0,0,0,0.3)"
          strokeWidth="0.2"
        />
        
        {/* Star inner details */}
        <circle 
          cx="12" 
          cy="12" 
          r="2" 
          fill="rgba(0,0,0,0.5)"
        />
      </svg>
    </div>
  );
};

/**
 * Hex Head Bolt - Industrial hex socket
 */
export const HexHeadBolt: React.FC<BoltProps> = ({ 
  className = '', 
  style = {},
  size = 12
}) => {
  return (
    <div className={className} style={{ position: 'relative', ...style }}>
      <svg 
        width={size} 
        height={size} 
        viewBox="0 0 24 24" 
        style={{ display: 'block' }}
      >
        <defs>
          <radialGradient id="hexGradient" cx="0.3" cy="0.3" r="0.8">
            <stop offset="0%" stopColor="#c8d4e1" />
            <stop offset="40%" stopColor="#a8b5c7" />
            <stop offset="70%" stopColor="#8e9aaf" />
            <stop offset="100%" stopColor="#6c7b7f" />
          </radialGradient>
          
          <linearGradient id="hexSocketGradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="rgba(0,0,0,0.8)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.5)" />
          </linearGradient>
        </defs>
        
        {/* Drop shadow */}
        <circle cx="12.5" cy="12.5" r="10" fill="rgba(0,0,0,0.2)" opacity="0.3" />
        
        {/* Main bolt body */}
        <circle 
          cx="12" 
          cy="12" 
          r="10" 
          fill="url(#hexGradient)"
          stroke="#5a6b70"
          strokeWidth="0.5"
        />
        
        {/* Rim highlight */}
        <circle 
          cx="12" 
          cy="12" 
          r="9.5" 
          fill="none"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth="0.5"
        />
        
        {/* Hexagonal socket */}
        <polygon 
          points="12,8 15,9.5 15,14.5 12,16 9,14.5 9,9.5" 
          fill="url(#hexSocketGradient)"
          stroke="rgba(0,0,0,0.4)"
          strokeWidth="0.3"
        />
        
        {/* Hex socket inner highlight */}
        <polygon 
          points="12,8.5 14.5,10 14.5,14 12,15.5 9.5,14 9.5,10" 
          fill="none"
          stroke="rgba(0,0,0,0.6)"
          strokeWidth="0.2"
        />
      </svg>
    </div>
  );
};

export default PhillipsHeadBolt;