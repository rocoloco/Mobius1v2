/**
 * Industrial Indicator Component
 * 
 * LED-style status indicators with glow effects and industrial color coding
 */

import React from 'react';
import { industrialTokens } from '../tokens';

/**
 * Industrial Indicator component interface
 */
export interface IndustrialIndicatorProps {
  status: 'off' | 'on' | 'error' | 'warning' | 'success';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  glow?: boolean;
  pulse?: boolean;
  label?: string;
  shape?: 'circle' | 'square' | 'diamond';
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
  'aria-label'?: string;
}

/**
 * Industrial Indicator Component
 */
export const IndustrialIndicator: React.FC<IndustrialIndicatorProps> = ({
  status,
  size = 'md',
  glow = true,
  pulse = false,
  label,
  shape = 'circle',
  className = '',
  style,
  onClick,
  'aria-label': ariaLabel,
}) => {
  // Size configurations
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
    xl: 'w-6 h-6',
  };

  const labelSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
    xl: 'text-lg',
  };

  // Shape configurations
  const shapeClasses = {
    circle: 'rounded-full',
    square: 'rounded-sm',
    diamond: 'rotate-45 rounded-sm',
  };

  // Status color mapping following industrial standards
  const getStatusColor = () => {
    switch (status) {
      case 'off': return industrialTokens.colors.led.off;
      case 'on': return industrialTokens.colors.led.on;
      case 'success': return industrialTokens.colors.led.on; // Green for success
      case 'error': return industrialTokens.colors.led.error; // Red for error
      case 'warning': return industrialTokens.colors.led.warning; // Amber for warning
      default: return industrialTokens.colors.led.off;
    }
  };

  // Generate LED glow styles
  const getLEDStyles = (): React.CSSProperties => {
    const color = getStatusColor();
    const isActive = status !== 'off';
    const glowIntensity = glow && isActive ? 1 : 0;
    
    const baseStyles: React.CSSProperties = {
      backgroundColor: color,
      transition: `all ${industrialTokens.animations.mechanical.duration.normal} ${industrialTokens.animations.mechanical.easing}`,
    };

    // Add glow effect for active states
    if (glowIntensity > 0) {
      baseStyles.boxShadow = `
        0 0 ${8 * glowIntensity}px ${color}, 
        0 0 ${16 * glowIntensity}px ${color}, 
        0 0 ${24 * glowIntensity}px ${color}
      `;
    }

    // Add pulse animation if enabled
    if (pulse && isActive) {
      baseStyles.animation = `ledPulse 2000ms ${industrialTokens.animations.mechanical.easing} infinite`;
    }

    return baseStyles;
  };

  // Get accessibility attributes
  const getAccessibilityProps = () => {
    const statusText = status === 'off' ? 'inactive' : status;
    
    return {
      role: onClick ? 'button' : 'status',
      'aria-label': ariaLabel || `${label ? `${label}: ` : ''}Status ${statusText}`,
      'aria-live': 'polite' as const,
      tabIndex: onClick ? 0 : undefined,
    };
  };

  // Event handlers
  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (onClick && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      onClick();
    }
  };

  const ledStyles = getLEDStyles();
  const accessibilityProps = getAccessibilityProps();

  const indicatorStyle: React.CSSProperties = {
    ...ledStyles,
    cursor: onClick ? 'pointer' : 'default',
    ...style,
  };

  // Container for indicator and label
  const IndicatorContainer = ({ children }: { children: React.ReactNode }) => {
    if (label) {
      return (
        <div className={`flex items-center space-x-2 ${onClick ? 'cursor-pointer' : ''}`}>
          {children}
          <span 
            className={labelSizeClasses[size]}
            style={{ color: industrialTokens.colors.text.primary }}
          >
            {label}
          </span>
        </div>
      );
    }
    return <>{children}</>;
  };

  return (
    <IndicatorContainer>
      <div
        className={`
          ${sizeClasses[size]} 
          ${shapeClasses[shape]}
          ${onClick ? 'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50' : ''}
          ${className}
        `}
        style={indicatorStyle}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        {...accessibilityProps}
      />
    </IndicatorContainer>
  );
};

/**
 * Industrial Indicator Group Component
 * For displaying multiple related indicators
 */
export interface IndustrialIndicatorGroupProps {
  indicators: Array<{
    id: string;
    status: IndustrialIndicatorProps['status'];
    label?: string;
    onClick?: () => void;
  }>;
  size?: IndustrialIndicatorProps['size'];
  glow?: boolean;
  pulse?: boolean;
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

export const IndustrialIndicatorGroup: React.FC<IndustrialIndicatorGroupProps> = ({
  indicators,
  size = 'md',
  glow = true,
  pulse = false,
  orientation = 'horizontal',
  className = '',
}) => {
  const orientationClasses = {
    horizontal: 'flex flex-row space-x-3',
    vertical: 'flex flex-col space-y-3',
  };

  return (
    <div className={`${orientationClasses[orientation]} ${className}`}>
      {indicators.map((indicator) => (
        <IndustrialIndicator
          key={indicator.id}
          status={indicator.status}
          size={size}
          glow={glow}
          pulse={pulse}
          label={indicator.label}
          onClick={indicator.onClick}
        />
      ))}
    </div>
  );
};

export default IndustrialIndicator;