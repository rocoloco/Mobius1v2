/**
 * Polished Industrial Button Component
 * 
 * Professional button built on Radix UI primitives with industrial design tokens
 */

import React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx } from 'clsx';
import { industrialTokens, NeumorphicUtils } from '../index';

const buttonVariants = cva(
  [
    'inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium',
    'transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:pointer-events-none disabled:opacity-50',
    'relative overflow-hidden select-none touch-manipulation',
    'border border-gray-300/30'
  ],
  {
    variants: {
      variant: {
        primary: [
          'text-white font-semibold tracking-wide',
          'bg-gradient-to-b from-blue-500 to-blue-600',
          'border-blue-400/30 focus-visible:ring-blue-500',
          'hover:from-blue-600 hover:to-blue-700 hover:shadow-lg',
          'active:from-blue-700 active:to-blue-800'
        ],
        secondary: [
          'text-gray-700 font-medium',
          'border-gray-400/40 focus-visible:ring-gray-500',
          'hover:text-gray-900 hover:border-gray-500/60'
        ],
        danger: [
          'text-white font-semibold tracking-wide',
          'bg-gradient-to-b from-red-500 to-red-600',
          'border-red-400/30 focus-visible:ring-red-500',
          'hover:from-red-600 hover:to-red-700 hover:shadow-lg',
          'active:from-red-700 active:to-red-800'
        ],
        success: [
          'text-white font-semibold tracking-wide',
          'bg-gradient-to-b from-green-500 to-green-600',
          'border-green-400/30 focus-visible:ring-green-500',
          'hover:from-green-600 hover:to-green-700 hover:shadow-lg',
          'active:from-green-700 active:to-green-800'
        ],
        ghost: [
          'text-gray-600 border-transparent font-medium',
          'hover:text-gray-800 hover:bg-gray-100/50 focus-visible:ring-gray-500'
        ],
        outline: [
          'text-gray-700 border-2 border-gray-500 font-medium bg-transparent',
          'hover:text-gray-900 hover:border-gray-600 hover:bg-gray-50/30',
          'focus-visible:ring-gray-500'
        ],
        industrial: [
          'text-orange-700 font-bold tracking-wider uppercase',
          'border-orange-400/60 focus-visible:ring-orange-500',
          'hover:text-orange-800 hover:border-orange-500/80'
        ],
        emergency: [
          'text-white font-bold tracking-wide uppercase',
          'bg-gradient-to-b from-orange-500 to-red-500',
          'border-orange-400/30 focus-visible:ring-orange-500',
          'hover:from-orange-600 hover:to-red-600 hover:shadow-lg',
          'active:from-orange-700 active:to-red-700'
        ],
        resin: [
          'text-white font-semibold tracking-wide relative overflow-hidden',
          'bg-gradient-to-b from-blue-400/80 to-blue-500/80',
          'border-blue-300/40 focus-visible:ring-blue-400',
          'backdrop-blur-sm'
        ]
      },
      size: {
        sm: 'h-9 !px-4 text-xs min-w-[2.25rem]',
        md: 'h-11 !px-8 text-sm min-w-[2.75rem]',
        lg: 'h-13 !px-10 text-base min-w-[3.25rem]',
        xl: 'h-16 !px-12 text-lg min-w-[4rem]'
      },
      industrial: {
        true: 'font-semibold tracking-wide uppercase'
      }
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      industrial: true
    }
  }
);

export interface PolishedIndustrialButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  neumorphic?: boolean;
  active?: boolean; // For the blooming LED effect
  glowColor?: string; // Custom glow color for the internal LED
}

const PolishedIndustrialButton = React.forwardRef<
  HTMLButtonElement,
  PolishedIndustrialButtonProps
>(({ 
  className, 
  variant, 
  size, 
  industrial,
  asChild = false, 
  loading = false,
  leftIcon,
  rightIcon,
  neumorphic = true,
  active = false,
  glowColor,
  children,
  style,
  disabled,
  ...props 
}, ref) => {
  const Comp = asChild ? Slot : 'button';
  
  // Apply neumorphic styling based on variant
  const getIndustrialStyle = () => {
    if (!neumorphic) return {};
    
    const baseNeumorphic = NeumorphicUtils.getPremiumShadowStyle('normal', 'raised');
    
    switch (variant) {
      case 'secondary':
      case 'ghost':
      case 'outline':
      case 'industrial':
        // These variants use neumorphic surface with shadows
        return {
          backgroundColor: industrialTokens.colors.surface.primary,
          ...baseNeumorphic,
        };
      
      case 'resin':
        // Translucent resin keycap with internal LED
        return getTranslucentResinStyle();
      
      case 'primary':
        // Primary keeps its blue gradient but gets neumorphic shadows
        return {
          ...baseNeumorphic,
        };
        
      case 'danger':
        // Danger keeps its red gradient but gets neumorphic shadows  
        return {
          ...baseNeumorphic,
        };
        
      case 'success':
        // Success keeps its green gradient but gets neumorphic shadows
        return {
          ...baseNeumorphic,
        };
        
      case 'emergency':
        // Emergency keeps its orange-red gradient but gets neumorphic shadows
        return {
          ...baseNeumorphic,
        };
        
      default:
        return {
          backgroundColor: industrialTokens.colors.surface.primary,
          ...baseNeumorphic,
        };
    }
  };

  // Generate translucent resin keycap styling with internal LED bloom
  const getTranslucentResinStyle = (): React.CSSProperties => {
    const ledColor = glowColor || '#3b82f6'; // Default blue
    const isActive = active || loading;
    
    const baseStyle: React.CSSProperties = {
      // Translucent resin material
      background: `linear-gradient(135deg, 
        rgba(255, 255, 255, 0.15) 0%, 
        rgba(255, 255, 255, 0.05) 50%, 
        rgba(0, 0, 0, 0.05) 100%
      )`,
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      
      // Base neumorphic shadows
      ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised'),
    };

    if (isActive) {
      // Internal LED bloom effect
      return {
        ...baseStyle,
        background: `
          radial-gradient(circle at center, 
            ${ledColor}40 0%, 
            ${ledColor}20 30%, 
            transparent 70%
          ),
          linear-gradient(135deg, 
            rgba(255, 255, 255, 0.2) 0%, 
            rgba(255, 255, 255, 0.1) 50%, 
            rgba(0, 0, 0, 0.05) 100%
          )
        `,
        boxShadow: `
          inset 0 0 20px ${ledColor}30,
          inset 0 1px 1px rgba(255,255,255,0.4),
          0 0 20px ${ledColor}40,
          0 0 40px ${ledColor}20,
          8px 8px 16px #babecc, 
          -8px -8px 16px #ffffff
        `,
        border: `1px solid ${ledColor}60`,
      };
    }

    return baseStyle;
  };

  // Combine styles with explicit padding based on size
  const getPaddingForSize = () => {
    switch (size) {
      case 'sm': return '0 1rem'; // 16px
      case 'md': return '0 2rem'; // 32px  
      case 'lg': return '0 2.5rem'; // 40px
      case 'xl': return '0 3rem'; // 48px
      default: return '0 2rem';
    }
  };

  const combinedStyle: React.CSSProperties = {
    ...getIndustrialStyle(),
    padding: getPaddingForSize(),
    ...style
  };

  // Add press physics animation
  const handleMouseDown = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!disabled && !loading) {
      e.currentTarget.style.transform = 'translateY(2px)';
      e.currentTarget.style.boxShadow = NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed').boxShadow || '';
    }
    props.onMouseDown?.(e);
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!disabled && !loading) {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = combinedStyle.boxShadow as string || '';
    }
    props.onMouseUp?.(e);
  };

  const handleMouseLeave = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!disabled && !loading) {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = combinedStyle.boxShadow as string || '';
    }
    props.onMouseLeave?.(e);
  };

  return (
    <Comp
      className={clsx(
        buttonVariants({ variant, size, industrial, className }),
        variant && `button-${variant}`
      )}
      style={combinedStyle}
      ref={ref}
      disabled={disabled || loading}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-inherit rounded-lg">
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      
      <div 
        className={clsx('flex items-center gap-3', loading && 'opacity-0')}
        style={{
          // Light diffusion effect for resin variant when active
          filter: variant === 'resin' && (active || loading) 
            ? 'drop-shadow(0 0 2px rgba(255,255,255,0.8)) drop-shadow(0 0 4px rgba(255,255,255,0.4))'
            : undefined
        }}
      >
        {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
        {children}
        {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
      </div>
    </Comp>
  );
});

PolishedIndustrialButton.displayName = 'PolishedIndustrialButton';

export { PolishedIndustrialButton, buttonVariants };