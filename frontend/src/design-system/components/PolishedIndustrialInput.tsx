/**
 * Polished Industrial Input Component
 * 
 * Professional input field with industrial design tokens and advanced features
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx } from 'clsx';
import { industrialTokens, NeumorphicUtils } from '../index';

const inputVariants = cva(
  [
    'flex w-full rounded-lg border px-5 py-2 text-sm transition-all duration-200',
    'file:border-0 file:bg-transparent file:text-sm file:font-medium',
    'placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2',
    'focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
    'relative'
  ],
  {
    variants: {
      variant: {
        default: [
          'border-gray-300/50 bg-white/80 focus-visible:ring-blue-500',
          'hover:border-gray-400/50 focus:border-blue-400/50'
        ],
        industrial: [
          'border-gray-400/50 focus-visible:ring-blue-500',
          'hover:border-gray-500/50 focus:border-blue-500/50',
          'font-medium tracking-wide'
        ],
        filled: [
          'border-transparent bg-gray-100/80 focus-visible:ring-blue-500',
          'hover:bg-gray-200/80 focus:bg-white focus:border-blue-400/50'
        ]
      },
      size: {
        sm: 'h-9 px-4 text-xs',
        md: 'h-11 px-5 text-sm',
        lg: 'h-13 px-6 text-base'
      },
      status: {
        none: '',
        success: 'border-green-400/50 bg-green-50/30 focus-visible:ring-green-500',
        warning: 'border-yellow-400/50 bg-yellow-50/30 focus-visible:ring-yellow-500',
        error: 'border-red-400/50 bg-red-50/30 focus-visible:ring-red-500'
      }
    },
    defaultVariants: {
      variant: 'industrial',
      size: 'md',
      status: 'none'
    }
  }
);

const labelVariants = cva(
  'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
  {
    variants: {
      status: {
        none: 'text-gray-700',
        success: 'text-green-700',
        warning: 'text-yellow-700',
        error: 'text-red-700'
      }
    },
    defaultVariants: {
      status: 'none'
    }
  }
);

export interface PolishedIndustrialInputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  label?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  ledIndicator?: boolean;
  neumorphic?: boolean;
}

// LED Status Indicator
const LEDIndicator: React.FC<{ status: NonNullable<PolishedIndustrialInputProps['status']> }> = ({ status }) => {
  if (status === 'none') return null;

  const statusConfig = {
    success: { color: industrialTokens.colors.led.on, glow: true },
    warning: { color: industrialTokens.colors.led.warning, glow: true },
    error: { color: industrialTokens.colors.led.error, glow: true }
  };

  const config = statusConfig[status];

  return (
    <div 
      className="w-2 h-2 rounded-full flex-shrink-0"
      style={{
        backgroundColor: config.color,
        boxShadow: config.glow ? `0 0 6px ${config.color}, 0 0 12px ${config.color}` : 'none',
      }}
      aria-hidden="true"
    />
  );
};

const PolishedIndustrialInput = React.forwardRef<
  HTMLInputElement,
  PolishedIndustrialInputProps
>(({ 
  className, 
  variant, 
  size, 
  status,
  label,
  helperText,
  leftIcon,
  rightIcon,
  ledIndicator = false,
  neumorphic = true,
  style,
  id,
  ...props 
}, ref) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  // Apply neumorphic styling with premium inner glow
  const neumorphicStyle = neumorphic ? {
    backgroundColor: industrialTokens.colors.surface.primary,
    ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed'),
  } : {};

  // Get explicit padding based on size and icons
  const getInputPadding = () => {
    const basePadding = {
      sm: '0.5rem 1rem', // 8px 16px
      md: '0.5rem 1.25rem', // 8px 20px
      lg: '0.75rem 1.5rem' // 12px 24px
    }[size || 'md'];

    // Adjust for icons
    if (leftIcon && (rightIcon || ledIndicator)) {
      return '0.5rem 3rem 0.5rem 3rem'; // Both icons
    } else if (leftIcon) {
      return '0.5rem 1.25rem 0.5rem 3rem'; // Left icon only
    } else if (rightIcon || ledIndicator) {
      return '0.5rem 3rem 0.5rem 1.25rem'; // Right icon only
    }
    
    return basePadding;
  };

  // Combine styles with explicit padding
  const combinedStyle: React.CSSProperties = {
    ...neumorphicStyle,
    padding: getInputPadding(),
    ...style
  };

  return (
    <div className="space-y-2">
      {/* Label */}
      {label && (
        <label 
          htmlFor={inputId}
          className={clsx(labelVariants({ status }))}
          style={{ color: industrialTokens.colors.text.primary }}
        >
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {/* Input Container */}
      <div className="relative">
        {/* Left Icon */}
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none">
            {leftIcon}
          </div>
        )}
        
        {/* Input Field */}
        <input
          ref={ref}
          id={inputId}
          className={clsx(
            inputVariants({ variant, size, status }),
            leftIcon && 'pl-12',
            (rightIcon || ledIndicator) && 'pr-12',
            className
          )}
          style={combinedStyle}
          {...props}
        />
        
        {/* Right Side Icons */}
        {(rightIcon || (ledIndicator && status && status !== 'none')) && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
            {ledIndicator && status && status !== 'none' && (
              <LEDIndicator status={status} />
            )}
            {rightIcon && (
              <div className="text-gray-500">
                {rightIcon}
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Helper Text */}
      {helperText && (
        <p 
          className={clsx(
            'text-xs',
            status === 'error' && 'text-red-600',
            status === 'warning' && 'text-yellow-600',
            status === 'success' && 'text-green-600',
            status === 'none' && 'text-gray-600'
          )}
          style={
            status === 'none' 
              ? { color: industrialTokens.colors.text.muted }
              : undefined
          }
        >
          {helperText}
        </p>
      )}
    </div>
  );
});

PolishedIndustrialInput.displayName = 'PolishedIndustrialInput';

export { PolishedIndustrialInput, inputVariants, labelVariants };