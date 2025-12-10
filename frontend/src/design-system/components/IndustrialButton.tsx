/**
 * Industrial Button Component
 * 
 * Tactile button with press physics and shadow inversion
 */

import React, { useState, useCallback } from 'react';
import { BaseIndustrialComponent, type IndustrialComponentProps } from './base';
import { industrialTokens } from '../tokens';
import { NeumorphicUtils } from '../neumorphic';

/**
 * Industrial Button component interface
 */
export interface IndustrialButtonProps extends Omit<IndustrialComponentProps, 'variant'> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  type?: 'primary' | 'secondary' | 'danger' | 'success';
  pressed?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  haptic?: boolean; // Enable press physics
  children: React.ReactNode;
  'aria-label'?: string;
}

/**
 * Industrial Button Component
 */
export const IndustrialButton: React.FC<IndustrialButtonProps> = ({
  size = 'md',
  type = 'primary',
  pressed: controlledPressed,
  disabled = false,
  onClick,
  haptic = true,
  depth = 'normal',
  manufacturing,
  className = '',
  children,
  style,
  'aria-label': ariaLabel,
  ...props
}) => {
  const [internalPressed, setInternalPressed] = useState(false);
  
  // Use controlled pressed state if provided, otherwise use internal state
  const isPressed = controlledPressed !== undefined ? controlledPressed : internalPressed;

  // Size configurations
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm min-h-[32px]',
    md: 'px-4 py-2 text-base min-h-[40px]',
    lg: 'px-6 py-3 text-lg min-h-[48px]',
    xl: 'px-8 py-4 text-xl min-h-[56px]',
  };

  // Type-based styling
  const getTypeStyles = () => {
    const baseColor = industrialTokens.colors.surface.primary;
    
    switch (type) {
      case 'primary':
        return {
          backgroundColor: baseColor,
          color: industrialTokens.colors.text.primary,
          borderColor: industrialTokens.colors.shadows.dark,
        };
      case 'secondary':
        return {
          backgroundColor: industrialTokens.colors.surface.secondary,
          color: industrialTokens.colors.text.secondary,
          borderColor: industrialTokens.colors.shadows.dark,
        };
      case 'danger':
        return {
          backgroundColor: industrialTokens.colors.led.error,
          color: '#ffffff',
          borderColor: industrialTokens.colors.led.error,
        };
      case 'success':
        return {
          backgroundColor: industrialTokens.colors.led.on,
          color: '#ffffff',
          borderColor: industrialTokens.colors.led.on,
        };
      default:
        return {
          backgroundColor: baseColor,
          color: industrialTokens.colors.text.primary,
          borderColor: industrialTokens.colors.shadows.dark,
        };
    }
  };

  // Press physics styles
  const getPressStyles = () => {
    if (!haptic) return {};
    
    const pressStyles = NeumorphicUtils.getPressStyles();
    return isPressed ? pressStyles.pressed : pressStyles.default;
  };

  // Event handlers
  const handleMouseDown = useCallback(() => {
    if (!disabled && controlledPressed === undefined) {
      setInternalPressed(true);
    }
  }, [disabled, controlledPressed]);

  const handleMouseUp = useCallback(() => {
    if (!disabled && controlledPressed === undefined) {
      setInternalPressed(false);
    }
  }, [disabled, controlledPressed]);

  const handleMouseLeave = useCallback(() => {
    if (!disabled && controlledPressed === undefined) {
      setInternalPressed(false);
    }
  }, [disabled, controlledPressed]);

  const handleClick = useCallback(() => {
    if (!disabled && onClick) {
      onClick();
    }
  }, [disabled, onClick]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (!disabled && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      if (controlledPressed === undefined) {
        setInternalPressed(true);
      }
      if (onClick) {
        onClick();
      }
    }
  }, [disabled, onClick, controlledPressed]);

  const handleKeyUp = useCallback((event: React.KeyboardEvent) => {
    if (!disabled && (event.key === 'Enter' || event.key === ' ')) {
      if (controlledPressed === undefined) {
        setInternalPressed(false);
      }
    }
  }, [disabled, controlledPressed]);

  // Combine styles
  const typeStyles = getTypeStyles();
  const pressStyles = getPressStyles();
  
  const buttonStyle: React.CSSProperties = {
    ...typeStyles,
    ...pressStyles,
    opacity: disabled ? 0.6 : 1,
    cursor: disabled ? 'not-allowed' : 'pointer',
    border: '1px solid',
    userSelect: 'none',
    ...style,
  };

  // Default manufacturing for buttons
  const buttonManufacturing = {
    screws: false,
    vents: false,
    texture: 'smooth' as const,
    ...manufacturing,
  };

  return (
    <BaseIndustrialComponent
      as="button"
      variant={isPressed ? 'recessed' : 'raised'}
      depth={depth}
      manufacturing={buttonManufacturing}
      className={`
        rounded-md 
        font-medium 
        focus:outline-none 
        focus:ring-2 
        focus:ring-blue-500 
        focus:ring-opacity-50
        active:outline-none
        ${sizeClasses[size]} 
        ${className}
      `}
      style={buttonStyle}
      onClick={handleClick}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
      onKeyDown={handleKeyDown}
      onKeyUp={handleKeyUp}
      disabled={disabled}
      aria-label={ariaLabel || (typeof children === 'string' ? children : 'Industrial button')}
      {...props}
    >
      <span className="relative z-10 flex items-center justify-center">
        {children}
      </span>
    </BaseIndustrialComponent>
  );
};

export default IndustrialButton;