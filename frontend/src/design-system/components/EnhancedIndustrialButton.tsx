/**
 * Enhanced Industrial Button Component
 * 
 * Professional-grade industrial button with realistic physics using Framer Motion
 */

import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { type IndustrialComponentProps } from './base';
import { industrialTokens } from '../tokens';
import { NeumorphicUtils } from '../neumorphic';

/**
 * Enhanced Industrial Button component interface
 */
export interface EnhancedIndustrialButtonProps extends Omit<IndustrialComponentProps, 'variant'> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  type?: 'primary' | 'secondary' | 'danger' | 'success' | 'emergency';
  pressed?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  haptic?: boolean;
  children: React.ReactNode;
  'aria-label'?: string;
  glowOnHover?: boolean;
  tactileFeedback?: boolean;
}

/**
 * Enhanced Industrial Button Component with Professional Physics
 */
export const EnhancedIndustrialButton: React.FC<EnhancedIndustrialButtonProps> = ({
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
  glowOnHover = false,
  tactileFeedback = true,
  'aria-label': ariaLabel,
  ...props
}) => {
  const [internalPressed, setInternalPressed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  
  // Use controlled pressed state if provided, otherwise use internal state
  const isPressed = controlledPressed !== undefined ? controlledPressed : internalPressed;

  // Animation state tracking

  // Size configurations
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm min-h-[32px]',
    md: 'px-4 py-2 text-base min-h-[40px]',
    lg: 'px-6 py-3 text-lg min-h-[48px]',
    xl: 'px-8 py-4 text-xl min-h-[56px]',
  };

  // Enhanced type-based styling with professional colors
  const getTypeStyles = () => {
    const baseColor = industrialTokens.colors.surface.primary;
    
    switch (type) {
      case 'primary':
        return {
          backgroundColor: baseColor,
          color: industrialTokens.colors.text.primary,
          borderColor: industrialTokens.colors.shadows.dark,
          glowColor: '#4a90e2',
        };
      case 'secondary':
        return {
          backgroundColor: industrialTokens.colors.surface.secondary,
          color: industrialTokens.colors.text.secondary,
          borderColor: industrialTokens.colors.shadows.dark,
          glowColor: '#7b68ee',
        };
      case 'danger':
        return {
          backgroundColor: industrialTokens.colors.led.error,
          color: '#ffffff',
          borderColor: industrialTokens.colors.led.error,
          glowColor: industrialTokens.colors.led.error,
        };
      case 'success':
        return {
          backgroundColor: industrialTokens.colors.led.on,
          color: '#ffffff',
          borderColor: industrialTokens.colors.led.on,
          glowColor: industrialTokens.colors.led.on,
        };
      case 'emergency':
        return {
          backgroundColor: '#ff4757',
          color: '#ffffff',
          borderColor: '#ff3742',
          glowColor: '#ff4757',
        };
      default:
        return {
          backgroundColor: baseColor,
          color: industrialTokens.colors.text.primary,
          borderColor: industrialTokens.colors.shadows.dark,
          glowColor: '#4a90e2',
        };
    }
  };

  // Event handlers with enhanced feedback
  const handleMouseDown = useCallback(() => {
    if (!disabled && controlledPressed === undefined) {
      setInternalPressed(true);
      if (tactileFeedback && navigator.vibrate) {
        navigator.vibrate(10); // Subtle haptic feedback
      }
    }
  }, [disabled, controlledPressed, tactileFeedback]);

  const handleMouseUp = useCallback(() => {
    if (!disabled && controlledPressed === undefined) {
      setInternalPressed(false);
    }
  }, [disabled, controlledPressed]);

  const handleMouseLeave = useCallback(() => {
    if (!disabled && controlledPressed === undefined) {
      setInternalPressed(false);
    }
    setIsHovered(false);
  }, [disabled, controlledPressed]);

  const handleMouseEnter = useCallback(() => {
    if (!disabled) {
      setIsHovered(true);
    }
  }, [disabled]);

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

  // Combine styles with enhanced effects
  const typeStyles = getTypeStyles();
  
  const buttonStyle: React.CSSProperties = {
    ...typeStyles,
    opacity: disabled ? 0.6 : 1,
    cursor: disabled ? 'not-allowed' : 'pointer',
    border: '1px solid',
    userSelect: 'none',
    position: 'relative',
    overflow: 'hidden',
    ...style,
  };

  // Enhanced manufacturing for buttons
  const buttonManufacturing = {
    screws: type === 'emergency' || size === 'xl',
    vents: false,
    texture: type === 'emergency' ? 'textured' : 'smooth',
    ...manufacturing,
  };

  // Animation variants
  const buttonVariants = {
    default: {
      y: 0,
      scale: 1,
      boxShadow: NeumorphicUtils.getShadowStyle(depth, 'raised').boxShadow,
    },
    hover: {
      y: -1,
      scale: 1.02,
      boxShadow: `${NeumorphicUtils.getShadowStyle('deep', 'raised').boxShadow}${glowOnHover ? `, 0 0 20px ${typeStyles.glowColor}40` : ''}`,
    },
    pressed: {
      y: 2,
      scale: 0.98,
      boxShadow: NeumorphicUtils.getShadowStyle(depth, 'recessed').boxShadow,
    },
  };

  const springTransition = {
    type: "spring" as const,
    stiffness: 400,
    damping: 25,
  };

  return (
    <motion.div
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
      variants={buttonVariants}
      initial="default"
      animate={
        disabled 
          ? "default" 
          : isPressed 
            ? "pressed" 
            : isHovered 
              ? "hover" 
              : "default"
      }
      whileTap={!disabled ? "pressed" : undefined}
      transition={springTransition}
      onClick={handleClick}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
      onMouseEnter={handleMouseEnter}
      onKeyDown={handleKeyDown}
      onKeyUp={handleKeyUp}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label={ariaLabel || (typeof children === 'string' ? children : 'Enhanced industrial button')}
      aria-disabled={disabled}
      {...props}
    >
      {/* Surface texture overlay */}
      {buttonManufacturing.texture !== 'smooth' && (
        <div 
          className="absolute inset-0 pointer-events-none rounded-md"
          style={NeumorphicUtils.getSurfaceTexture(buttonManufacturing.texture as 'smooth' | 'brushed' | 'textured')}
        />
      )}

      {/* Emergency button warning stripes */}
      {type === 'emergency' && (
        <div 
          className="absolute inset-0 pointer-events-none rounded-md opacity-20"
          style={{
            background: `repeating-linear-gradient(
              45deg,
              transparent 0px,
              transparent 4px,
              rgba(255,255,255,0.3) 4px,
              rgba(255,255,255,0.3) 8px
            )`,
          }}
        />
      )}

      {/* Button content */}
      <span className="relative z-10 flex items-center justify-center">
        {children}
      </span>

      {/* Glow effect for hover */}
      {glowOnHover && isHovered && !disabled && (
        <motion.div
          className="absolute inset-0 rounded-md pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.3 }}
          exit={{ opacity: 0 }}
          style={{
            background: `radial-gradient(circle, ${typeStyles.glowColor}20 0%, transparent 70%)`,
          }}
        />
      )}
    </motion.div>
  );
};

export default EnhancedIndustrialButton;