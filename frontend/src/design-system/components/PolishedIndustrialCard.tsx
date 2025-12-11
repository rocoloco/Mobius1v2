/**
 * Polished Industrial Card Component
 * 
 * Professional card component with industrial design tokens and advanced features.
 * 
 * PRODUCTION FEATURES:
 * - Automatic content padding adjustment for manufacturing details (bolts, textures)
 * - Smart status indicator positioning to avoid bolt conflicts
 * - Multiple bolt types: torx (default), hex, phillips, flathead
 * - Surface texture support: brushed, diamond-plate, perforated, carbon-fiber
 * - Proper z-index layering for overlapping elements
 * - Responsive design with touch-friendly interactions
 * - Full accessibility support with ARIA labels
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx } from 'clsx';
import { industrialTokens, NeumorphicUtils } from '../index';
import { HexHeadBolt, PhillipsHeadBolt, TorxHeadBolt, FlatheadBolt } from './IndustrialBolts';
import { SurfaceTexture } from './IndustrialManufacturing';

const cardVariants = cva(
  [
    'rounded-lg transition-all duration-200 relative overflow-hidden',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2'
  ],
  {
    variants: {
      variant: {
        default: [
          'border border-gray-300/30',
          'focus-visible:ring-gray-500'
        ],
        elevated: [
          'border border-gray-200/40',
          'focus-visible:ring-gray-500'
        ],
        interactive: [
          'focus-visible:ring-gray-500'
        ],
        status: [
          'border border-gray-400/50',
          'focus-visible:ring-gray-500'
        ]
      },
      size: {
        sm: 'p-4',
        md: 'p-6', 
        lg: 'p-8',
        xl: 'p-10'
      },
      status: {
        none: '',
        active: 'border-green-400/50 bg-green-50/30',
        warning: 'border-yellow-400/50 bg-yellow-50/30',
        error: 'border-red-400/50 bg-red-50/30',
        inactive: 'border-gray-300/50 bg-gray-50/30'
      }
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
      status: 'none'
    }
  }
);

export interface PolishedIndustrialCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  title?: string;
  subtitle?: string;
  headerAction?: React.ReactNode;
  footer?: React.ReactNode;
  neumorphic?: boolean;
  manufacturing?: {
    bolts?: boolean | 'torx' | 'hex' | 'phillips' | 'flathead';
    texture?: 'smooth' | 'brushed' | 'diamond-plate' | 'perforated' | 'carbon-fiber';
  };
}

// Utility to get the appropriate bolt component
const getBoltComponent = (boltType: NonNullable<PolishedIndustrialCardProps['manufacturing']>['bolts']) => {
  if (!boltType) return null;
  
  switch (boltType) {
    case 'phillips':
      return PhillipsHeadBolt;
    case 'torx':
      return TorxHeadBolt;
    case 'flathead':
      return FlatheadBolt;
    case 'hex':
      return HexHeadBolt;
    case true: // Default to torx when just true
    default:
      return TorxHeadBolt;
  }
};

// Utility to calculate safe content area when manufacturing details are present
const getContentPadding = (manufacturing?: PolishedIndustrialCardProps['manufacturing'], size?: string) => {
  const basePadding = {
    sm: 16,
    md: 24, 
    lg: 32,
    xl: 40
  }[size || 'md'] || 24;

  // Add extra padding for bolts (they need clearance) - increased for new bolt size
  const boltPadding = manufacturing?.bolts ? 12 : 0;

  return {
    padding: `${basePadding + boltPadding}px`
  };
};

// Status indicator component
const StatusIndicator: React.FC<{ 
  status: NonNullable<PolishedIndustrialCardProps['status']>;
  hasBolts?: boolean;
}> = ({ status, hasBolts = false }) => {
  if (status === 'none') return null;

  const statusConfig = {
    active: { color: industrialTokens.colors.led.on, label: 'Active' },
    warning: { color: industrialTokens.colors.led.warning, label: 'Warning' },
    error: { color: industrialTokens.colors.led.error, label: 'Error' },
    inactive: { color: industrialTokens.colors.led.off, label: 'Inactive' }
  };

  const config = statusConfig[status];
  const shouldGlow = status === 'active' || status === 'error';

  // Position status indicator to avoid bolts
  const positionClass = hasBolts 
    ? 'absolute top-6 right-10 flex items-center gap-2 z-20'
    : 'absolute top-4 right-4 flex items-center gap-2 z-20';

  return (
    <div className={positionClass}>
      <div 
        className="w-3 h-3 rounded-full"
        style={{
          backgroundColor: config.color,
          boxShadow: shouldGlow ? `0 0 8px ${config.color}, 0 0 16px ${config.color}` : 'none',
        }}
        aria-label={`Status: ${config.label}`}
      />
      <span className="text-xs font-medium text-gray-600 hidden sm:inline">
        {config.label}
      </span>
    </div>
  );
};

// Manufacturing details component
const ManufacturingDetails: React.FC<{ manufacturing: PolishedIndustrialCardProps['manufacturing'] }> = ({ manufacturing }) => {
  if (!manufacturing) return null;

  return (
    <>
      {/* Corner bolts */}
      {manufacturing.bolts && (() => {
        const BoltComponent = getBoltComponent(manufacturing.bolts);
        return BoltComponent ? (
          <>
            {/* Top Left Bolt */}
            <div 
              className="absolute top-3 left-3 z-10"
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: industrialTokens.colors.surface.primary,
                boxShadow: `
                  inset 2px 2px 4px rgba(163, 177, 198, 0.6),
                  inset -2px -2px 4px rgba(255, 255, 255, 0.8),
                  0 1px 2px rgba(0, 0, 0, 0.1)
                `,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <BoltComponent size={16} />
            </div>
            
            {/* Top Right Bolt */}
            <div 
              className="absolute top-3 right-3 z-10"
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: industrialTokens.colors.surface.primary,
                boxShadow: `
                  inset 2px 2px 4px rgba(163, 177, 198, 0.6),
                  inset -2px -2px 4px rgba(255, 255, 255, 0.8),
                  0 1px 2px rgba(0, 0, 0, 0.1)
                `,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <BoltComponent size={16} />
            </div>
            
            {/* Bottom Left Bolt */}
            <div 
              className="absolute bottom-3 left-3 z-10"
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: industrialTokens.colors.surface.primary,
                boxShadow: `
                  inset 2px 2px 4px rgba(163, 177, 198, 0.6),
                  inset -2px -2px 4px rgba(255, 255, 255, 0.8),
                  0 1px 2px rgba(0, 0, 0, 0.1)
                `,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <BoltComponent size={16} />
            </div>
            
            {/* Bottom Right Bolt */}
            <div 
              className="absolute bottom-3 right-3 z-10"
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: industrialTokens.colors.surface.primary,
                boxShadow: `
                  inset 2px 2px 4px rgba(163, 177, 198, 0.6),
                  inset -2px -2px 4px rgba(255, 255, 255, 0.8),
                  0 1px 2px rgba(0, 0, 0, 0.1)
                `,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <BoltComponent size={16} />
            </div>
          </>
        ) : null;
      })()}
      
      {/* Surface texture */}
      {manufacturing.texture && manufacturing.texture !== 'smooth' && (
        <div className="absolute inset-0 rounded-xl overflow-hidden pointer-events-none">
          <SurfaceTexture pattern={manufacturing.texture} intensity={0.3} />
        </div>
      )}
      

    </>
  );
};

const PolishedIndustrialCard = React.forwardRef<
  HTMLDivElement,
  PolishedIndustrialCardProps
>(({ 
  className, 
  variant, 
  size, 
  status,
  title,
  subtitle,
  headerAction,
  footer,
  neumorphic = true,
  manufacturing,
  children,
  style,
  ...props 
}, ref) => {
  // Apply proper industrial neumorphic styling based on variant
  const getIndustrialStyle = () => {
    const baseStyle = {
      backgroundColor: industrialTokens.colors.surface.primary,
    };

    if (!neumorphic) return baseStyle;

    switch (variant) {
      case 'default':
        // Flush with surface - minimal depth
        return {
          ...baseStyle,
          ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'raised'),
        };
      case 'elevated':
        // Raised above surface - more prominent
        return {
          ...baseStyle,
          ...NeumorphicUtils.getPremiumShadowStyle('deep', 'raised'),
        };
      case 'interactive':
        // Let CSS handle ALL styling for hover effects - no inline styles
        return {};
      case 'status':
        // Recessed for status display
        return {
          ...baseStyle,
          ...NeumorphicUtils.getPremiumShadowStyle('normal', 'recessed'),
        };
      default:
        return {
          ...baseStyle,
          ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised'),
        };
    }
  };

  const industrialStyle = getIndustrialStyle();



  // Get dynamic padding based on manufacturing features
  const contentPadding = getContentPadding(manufacturing, size || 'md');
  
  // For interactive cards, don't apply inline styles that could override CSS hover effects
  const finalStyle: React.CSSProperties = variant === 'interactive' 
    ? { ...contentPadding, ...style } // Only padding and user styles
    : { ...industrialStyle, ...contentPadding, ...style }; // Full styling for other variants

  return (
    <div
      ref={ref}
      className={clsx(
        cardVariants({ variant, size: undefined, status, className }),
        variant === 'interactive' && 'group interactive-card-hover'
      )}
      style={finalStyle}
      {...props}
    >


      {/* Interactive indicator */}
      {variant === 'interactive' && (
        <div className="absolute top-3 right-3 w-2 h-2 bg-blue-400/60 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
      )}

      {/* Manufacturing details */}
      <ManufacturingDetails manufacturing={manufacturing} />
      
      {/* Status indicator */}
      {status && status !== 'none' && <StatusIndicator status={status} hasBolts={!!manufacturing?.bolts} />}
      
      {/* Header */}
      {(title || subtitle || headerAction) && (
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            {title && (
              <h3 
                className="text-lg font-semibold text-gray-900 truncate"
                style={{ color: industrialTokens.colors.text.primary }}
              >
                {title}
              </h3>
            )}
            {subtitle && (
              <p 
                className="text-sm text-gray-600 mt-1"
                style={{ color: industrialTokens.colors.text.secondary }}
              >
                {subtitle}
              </p>
            )}
          </div>
          {headerAction && (
            <div className="flex-shrink-0 ml-4">
              {headerAction}
            </div>
          )}
        </div>
      )}
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
      
      {/* Footer */}
      {footer && (
        <div className="mt-4 pt-4 border-t border-gray-200/50">
          {footer}
        </div>
      )}
    </div>
  );
});

PolishedIndustrialCard.displayName = 'PolishedIndustrialCard';

export { PolishedIndustrialCard, cardVariants };