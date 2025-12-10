/**
 * Industrial Input Component
 * 
 * Recessed data slot appearance with LED status indicators
 */

import React, { useState, useCallback, forwardRef } from 'react';
import { BaseIndustrialComponent, type IndustrialComponentProps } from './base';
import { industrialTokens } from '../tokens';
import { NeumorphicUtils } from '../neumorphic';

/**
 * Industrial Input component interface
 */
export interface IndustrialInputProps extends Omit<IndustrialComponentProps, 'variant' | 'children'> {
  type?: 'text' | 'number' | 'password' | 'email';
  placeholder?: string;
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  status?: 'normal' | 'error' | 'success' | 'warning';
  ledIndicator?: boolean;
  disabled?: boolean;
  required?: boolean;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  helperText?: string;
  'aria-label'?: string;
}

/**
 * LED Status Indicator Component
 */
const LEDStatusIndicator: React.FC<{ 
  status: IndustrialInputProps['status'];
  active: boolean;
}> = ({ status = 'normal', active }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'error': return industrialTokens.colors.led.error;
      case 'success': return industrialTokens.colors.led.on;
      case 'warning': return industrialTokens.colors.led.warning;
      default: return industrialTokens.colors.led.off;
    }
  };

  const statusColor = getStatusColor();
  const glowIntensity = active ? 1 : 0.3;
  
  const glowStyle: React.CSSProperties = {
    backgroundColor: statusColor,
    boxShadow: status !== 'normal' && active ? `0 0 ${8 * glowIntensity}px ${statusColor}, 0 0 ${16 * glowIntensity}px ${statusColor}` : 'none',
    transition: `all ${industrialTokens.animations.mechanical.duration.normal} ${industrialTokens.animations.mechanical.easing}`,
  };

  return (
    <div 
      className="w-2 h-2 rounded-full flex-shrink-0"
      style={glowStyle}
    />
  );
};

/**
 * Industrial Input Component
 */
export const IndustrialInput = forwardRef<HTMLInputElement, IndustrialInputProps>(({
  type = 'text',
  placeholder,
  value,
  defaultValue,
  onChange,
  onFocus,
  onBlur,
  status = 'normal',
  ledIndicator = true,
  disabled = false,
  required = false,
  size = 'md',
  label,
  helperText,
  depth = 'normal',
  manufacturing,
  className = '',
  style,
  'aria-label': ariaLabel,
  ...props
}, ref) => {
  const [isFocused, setIsFocused] = useState(false);
  const [internalValue, setInternalValue] = useState(defaultValue || '');

  // Use controlled value if provided, otherwise use internal state
  const inputValue = value !== undefined ? value : internalValue;

  // Size configurations
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm min-h-[32px]',
    md: 'px-4 py-2 text-base min-h-[40px]',
    lg: 'px-6 py-3 text-lg min-h-[48px]',
  };

  // Status-based styling
  const getStatusStyles = () => {
    const baseStyles = {
      backgroundColor: industrialTokens.colors.surface.secondary,
      color: industrialTokens.colors.text.primary,
      borderColor: industrialTokens.colors.shadows.dark,
    };

    switch (status) {
      case 'error':
        return {
          ...baseStyles,
          borderColor: industrialTokens.colors.led.error,
        };
      case 'success':
        return {
          ...baseStyles,
          borderColor: industrialTokens.colors.led.on,
        };
      case 'warning':
        return {
          ...baseStyles,
          borderColor: industrialTokens.colors.led.warning,
        };
      default:
        return baseStyles;
    }
  };

  // Focus enhancement for recessed effect
  const getFocusStyles = (): React.CSSProperties => {
    if (!isFocused) return {};
    
    return {
      boxShadow: `${NeumorphicUtils.getShadowStyle('deep', 'recessed').boxShadow}, 0 0 0 2px ${industrialTokens.colors.led.on}40`,
    };
  };

  // Event handlers
  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    
    if (value === undefined) {
      setInternalValue(newValue);
    }
    
    if (onChange) {
      onChange(newValue);
    }
  }, [value, onChange]);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
    if (onFocus) {
      onFocus();
    }
  }, [onFocus]);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
    if (onBlur) {
      onBlur();
    }
  }, [onBlur]);

  // Combine styles
  const statusStyles = getStatusStyles();
  const focusStyles = getFocusStyles();
  
  const inputStyle: React.CSSProperties = {
    ...statusStyles,
    ...focusStyles,
    opacity: disabled ? 0.6 : 1,
    cursor: disabled ? 'not-allowed' : 'text',
    border: '1px solid',
    outline: 'none',
    transition: `all ${industrialTokens.animations.mechanical.duration.normal} ${industrialTokens.animations.mechanical.easing}`,
    ...style,
  };

  // Default manufacturing for inputs (no screws, subtle texture)
  const inputManufacturing = {
    screws: false,
    vents: false,
    texture: 'smooth' as const,
    ...manufacturing,
  };

  const inputId = `industrial-input-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="flex flex-col space-y-2">
      {/* Label */}
      {label && (
        <label 
          htmlFor={inputId}
          className="text-sm font-medium"
          style={{ color: industrialTokens.colors.text.primary }}
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {/* Input container */}
      <div className="relative flex items-center">
        <BaseIndustrialComponent
          variant="recessed"
          depth={isFocused ? 'deep' : depth}
          manufacturing={inputManufacturing}
          className={`
            flex-1 
            rounded-md 
            ${sizeClasses[size]} 
            ${className}
          `}
          style={{ padding: 0 }}
        >
          <input
            ref={ref}
            id={inputId}
            type={type}
            placeholder={placeholder}
            value={inputValue}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            disabled={disabled}
            required={required}
            className={`
              w-full h-full bg-transparent border-0 outline-none
              ${sizeClasses[size]}
            `}
            style={{
              color: inputStyle.color,
              fontSize: 'inherit',
            }}
            aria-label={ariaLabel || label || placeholder}
            {...props}
          />
        </BaseIndustrialComponent>
        
        {/* LED Status Indicator */}
        {ledIndicator && (
          <div className="ml-3 flex items-center">
            <LEDStatusIndicator 
              status={status} 
              active={isFocused || inputValue.length > 0} 
            />
          </div>
        )}
      </div>
      
      {/* Helper text */}
      {helperText && (
        <p 
          className="text-xs"
          style={{ 
            color: status === 'error' 
              ? industrialTokens.colors.led.error 
              : industrialTokens.colors.text.muted 
          }}
        >
          {helperText}
        </p>
      )}
    </div>
  );
});

IndustrialInput.displayName = 'IndustrialInput';

export default IndustrialInput;