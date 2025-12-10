/**
 * Industrial Card Component
 * 
 * Bolted module styling with corner screws and manufacturing details
 */

import React from 'react';
import { BaseIndustrialComponent, type IndustrialComponentProps } from './base';
import { industrialTokens } from '../tokens';

/**
 * Industrial Card component interface
 */
export interface IndustrialCardProps extends IndustrialComponentProps {
  title?: string;
  subtitle?: string;
  status?: 'active' | 'inactive' | 'error' | 'warning';
  bolted?: boolean; // Show corner screws
  ventilated?: boolean; // Show vent slots
  size?: 'sm' | 'md' | 'lg' | 'xl';
  onClick?: () => void;
}

/**
 * Status indicator for cards
 */
const StatusIndicator: React.FC<{ status: IndustrialCardProps['status'] }> = ({ status }) => {
  if (!status || status === 'inactive') return null;

  const getStatusColor = () => {
    switch (status) {
      case 'active': return industrialTokens.colors.led.on;
      case 'error': return industrialTokens.colors.led.error;
      case 'warning': return industrialTokens.colors.led.warning;
      default: return industrialTokens.colors.led.off;
    }
  };

  const statusColor = getStatusColor();
  const shouldGlow = status === 'active' || status === 'error' || status === 'warning';

  return (
    <div 
      className="absolute top-3 right-3 w-2 h-2 rounded-full"
      style={{
        backgroundColor: statusColor,
        boxShadow: shouldGlow ? `0 0 8px ${statusColor}, 0 0 16px ${statusColor}` : 'none',
      }}
    />
  );
};

/**
 * Industrial Card Component
 */
export const IndustrialCard: React.FC<IndustrialCardProps> = ({
  title,
  subtitle,
  status,
  bolted = true,
  ventilated = false,
  size = 'md',
  onClick,
  variant = 'raised',
  depth = 'normal',
  manufacturing,
  className = '',
  children,
  style,
  ...props
}) => {
  // Size configurations
  const sizeClasses = {
    sm: 'p-4 min-h-[120px]',
    md: 'p-6 min-h-[160px]',
    lg: 'p-8 min-h-[200px]',
    xl: 'p-10 min-h-[240px]',
  };

  // Merge manufacturing props with defaults
  const cardManufacturing = {
    screws: bolted,
    vents: ventilated,
    texture: 'smooth' as const,
    ...manufacturing,
  };

  const cardStyle: React.CSSProperties = {
    cursor: onClick ? 'pointer' : 'default',
    transition: `all ${industrialTokens.animations.mechanical.duration.normal} ${industrialTokens.animations.mechanical.easing}`,
    ...style,
  };

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

  return (
    <BaseIndustrialComponent
      variant={variant}
      depth={depth}
      manufacturing={cardManufacturing}
      className={`
        rounded-lg 
        ${sizeClasses[size]} 
        ${onClick ? 'hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50' : ''}
        ${className}
      `}
      style={cardStyle}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={onClick ? 0 : undefined}
      role={onClick ? 'button' : undefined}
      aria-label={title ? `Industrial card: ${title}` : 'Industrial card'}
      {...props}
    >
      {/* Status indicator */}
      <StatusIndicator status={status} />
      
      {/* Card header */}
      {(title || subtitle) && (
        <div className={`mb-4 ${bolted ? 'mt-2' : ''}`}>
          {title && (
            <h3 
              className="text-lg font-semibold mb-1"
              style={{ color: industrialTokens.colors.text.primary }}
            >
              {title}
            </h3>
          )}
          {subtitle && (
            <p 
              className="text-sm"
              style={{ color: industrialTokens.colors.text.secondary }}
            >
              {subtitle}
            </p>
          )}
        </div>
      )}
      
      {/* Card content */}
      <div className="relative z-10">
        {children}
      </div>
    </BaseIndustrialComponent>
  );
};

export default IndustrialCard;