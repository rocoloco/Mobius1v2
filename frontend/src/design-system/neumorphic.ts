/**
 * Neumorphic Shadow Utilities
 * 
 * Implements unidirectional illumination compliance and mathematical
 * shadow calculations for consistent neumorphic effects.
 */

import { industrialTokens, tokenUtils } from './tokens';

export type ShadowVariant = 'subtle' | 'normal' | 'deep';
export type ShadowType = 'raised' | 'recessed';

/**
 * Neumorphic shadow utility class
 */
export class NeumorphicUtils {
  /**
   * Generate CSS class names for neumorphic shadows
   */
  static getShadowClass(variant: ShadowVariant = 'normal', type: ShadowType = 'raised'): string {
    return `shadow-neumorphic-${type}-${variant}`;
  }

  /**
   * Generate inline shadow styles
   */
  static getShadowStyle(variant: ShadowVariant = 'normal', type: ShadowType = 'raised'): React.CSSProperties {
    return {
      boxShadow: tokenUtils.getShadow(variant, type),
    };
  }

  /**
   * Generate press effect styles for buttons
   */
  static getPressStyles(): {
    default: React.CSSProperties;
    pressed: React.CSSProperties;
  } {
    return {
      default: {
        boxShadow: tokenUtils.getShadow('normal', 'raised'),
        transform: 'translateY(0)',
        transition: `all ${industrialTokens.animations.press.duration} ${industrialTokens.animations.mechanical.easing}`,
      },
      pressed: {
        boxShadow: tokenUtils.getShadow('normal', 'recessed'),
        transform: industrialTokens.animations.press.transform,
        transition: `all ${industrialTokens.animations.press.duration} ${industrialTokens.animations.mechanical.easing}`,
      },
    };
  }

  /**
   * Generate LED glow effect styles
   */
  static getLEDGlowStyle(status: 'off' | 'on' | 'error' | 'warning', intensity: number = 1): React.CSSProperties {
    const color = tokenUtils.getLEDColor(status);
    const glowIntensity = status === 'off' ? 0 : intensity;
    
    return {
      backgroundColor: color,
      boxShadow: glowIntensity > 0 ? `0 0 ${10 * glowIntensity}px ${color}, 0 0 ${20 * glowIntensity}px ${color}, 0 0 ${30 * glowIntensity}px ${color}` : 'none',
      transition: `all ${industrialTokens.animations.mechanical.duration.normal} ${industrialTokens.animations.mechanical.easing}`,
    };
  }

  /**
   * Generate manufacturing detail styles
   */
  static getScrewStyle(): React.CSSProperties {
    return {
      width: industrialTokens.manufacturing.screws.size,
      height: industrialTokens.manufacturing.screws.size,
      backgroundColor: industrialTokens.manufacturing.screws.color,
      borderRadius: '50%',
      boxShadow: industrialTokens.manufacturing.screws.shadow,
      position: 'absolute' as const,
    };
  }

  /**
   * Generate realistic industrial bolt base style (deprecated - use IndustrialBolts components instead)
   */
  static getIndustrialBoltStyle(): React.CSSProperties {
    return {
      width: '12px',
      height: '12px',
      borderRadius: '50%',
      position: 'absolute' as const,
      background: `radial-gradient(circle at 30% 30%, #b8c5d1 0%, #95a3b3 40%, #7a8794 100%)`,
      boxShadow: `
        inset 0 0 0 0.5px #6a7580,
        inset 0 1px 2px rgba(0,0,0,0.2),
        0 1px 2px rgba(0,0,0,0.3),
        0 0 0 0.5px rgba(255,255,255,0.1)
      `,
    };
  }



  /**
   * Generate vent slot pattern styles
   */
  static getVentSlotStyle(): React.CSSProperties {
    const { slotWidth, slotSpacing, color } = industrialTokens.manufacturing.vents;
    
    return {
      background: `repeating-linear-gradient(
        90deg,
        transparent 0,
        transparent ${slotSpacing},
        ${color} ${slotSpacing},
        ${color} calc(${slotSpacing} + ${slotWidth})
      )`,
    };
  }

  /**
   * Validate shadow pattern compliance
   * Ensures shadows follow unidirectional illumination rules
   */
  static validateShadowPattern(shadowCSS: string): boolean {
    // Check for dual shadow pattern
    const shadowParts = shadowCSS.split(',').map(s => s.trim());
    if (shadowParts.length !== 2) return false;

    // Check for correct color usage
    const hasDarkShadow = shadowParts.some(part => part.includes('#babecc'));
    const hasLightShadow = shadowParts.some(part => part.includes('#ffffff'));
    
    return hasDarkShadow && hasLightShadow;
  }

  /**
   * Generate surface texture pattern
   */
  static getSurfaceTexture(type: 'smooth' | 'brushed' | 'textured' = 'smooth'): React.CSSProperties {
    switch (type) {
      case 'brushed':
        return {
          background: `linear-gradient(90deg, 
            rgba(255,255,255,0.1) 0%, 
            rgba(255,255,255,0.05) 50%, 
            rgba(255,255,255,0.1) 100%
          )`,
        };
      case 'textured':
        return {
          background: `radial-gradient(circle at 1px 1px, 
            rgba(0,0,0,0.05) 1px, 
            transparent 0
          )`,
          backgroundSize: '8px 8px',
        };
      default:
        return {};
    }
  }
}

/**
 * React hook for neumorphic interactions
 */
export const useNeumorphicPress = () => {
  const [isPressed, setIsPressed] = React.useState(false);
  
  const pressStyles = NeumorphicUtils.getPressStyles();
  
  const handleMouseDown = () => setIsPressed(true);
  const handleMouseUp = () => setIsPressed(false);
  const handleMouseLeave = () => setIsPressed(false);
  
  return {
    isPressed,
    style: isPressed ? pressStyles.pressed : pressStyles.default,
    handlers: {
      onMouseDown: handleMouseDown,
      onMouseUp: handleMouseUp,
      onMouseLeave: handleMouseLeave,
    },
  };
};

// Import React for the hook
import React from 'react';

export default NeumorphicUtils;