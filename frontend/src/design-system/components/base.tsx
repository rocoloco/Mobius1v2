/**
 * Base Industrial Component
 * 
 * Shared props interface and base component for all industrial components
 */

import React from 'react';
import { industrialTokens } from '../tokens';
import { NeumorphicUtils, type ShadowVariant, type ShadowType } from '../neumorphic';
import { PhillipsHeadBolt } from './IndustrialBolts';

/**
 * Base industrial component props interface
 */
export interface IndustrialComponentProps {
  variant?: ShadowType;
  depth?: ShadowVariant;
  manufacturing?: {
    screws?: boolean;
    vents?: boolean;
    connectors?: boolean;
    texture?: 'smooth' | 'brushed' | 'textured';
  };
  className?: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}

/**
 * Manufacturing details component
 */
interface ManufacturingDetailsProps {
  screws?: boolean;
  vents?: boolean;
  connectors?: boolean;
  texture?: 'smooth' | 'brushed' | 'textured';
  className?: string;
}

export const ManufacturingDetails: React.FC<ManufacturingDetailsProps> = ({
  screws = false,
  vents = false,
  connectors = false,
  texture = 'smooth',
  className = '',
}) => {
  const ventStyle = NeumorphicUtils.getVentSlotStyle();
  const textureStyle = NeumorphicUtils.getSurfaceTexture(texture);

  return (
    <>
      {/* Surface texture overlay */}
      {texture !== 'smooth' && (
        <div 
          className={`absolute inset-0 pointer-events-none ${className}`}
          style={textureStyle}
        />
      )}
      
      {/* Corner bolts with Phillips head screw indentations */}
      {screws && (
        <>
          <PhillipsHeadBolt 
            className="absolute top-2 left-2"
          />
          <PhillipsHeadBolt 
            className="absolute top-2 right-2"
          />
          <PhillipsHeadBolt 
            className="absolute bottom-2 left-2"
          />
          <PhillipsHeadBolt 
            className="absolute bottom-2 right-2"
          />
        </>
      )}
      
      {/* Vent slots */}
      {vents && (
        <div 
          className="absolute bottom-0 left-4 right-4 h-2"
          style={ventStyle}
        />
      )}
      
      {/* Connectors */}
      {connectors && (
        <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-2 h-8 bg-gray-600 rounded-l-sm" />
      )}
    </>
  );
};

/**
 * Base industrial component wrapper
 */
export interface BaseIndustrialComponentProps extends IndustrialComponentProps {
  as?: keyof React.JSX.IntrinsicElements;
  role?: string;
  'aria-label'?: string;
  tabIndex?: number;
  disabled?: boolean;
  onClick?: () => void;
  onKeyDown?: (event: React.KeyboardEvent) => void;
  onKeyUp?: (event: React.KeyboardEvent) => void;
  onMouseDown?: () => void;
  onMouseUp?: () => void;
  onMouseLeave?: () => void;
}

export const BaseIndustrialComponent: React.FC<BaseIndustrialComponentProps> = ({
  as = 'div',
  variant = 'raised',
  depth = 'normal',
  manufacturing,
  className = '',
  children,
  style,
  ...props
}) => {
  const shadowStyle = NeumorphicUtils.getShadowStyle(depth, variant);
  
  const baseStyle: React.CSSProperties = {
    backgroundColor: industrialTokens.colors.surface.primary,
    position: 'relative',
    ...shadowStyle,
    ...style,
  };

  const Component = as as React.ElementType;

  return (
    <Component
      className={`relative ${className}`}
      style={baseStyle}
      {...props}
    >
      {manufacturing && (
        <ManufacturingDetails {...manufacturing} />
      )}
      {children}
    </Component>
  );
};

export default BaseIndustrialComponent;