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
   * Generate premium shadow styles with inner glow for solid resin effect
   */
  static getPremiumShadowStyle(variant: ShadowVariant = 'normal', type: ShadowType = 'raised'): React.CSSProperties {
    const baseShadow = tokenUtils.getShadow(variant, type);
    const innerGlow = type === 'raised' 
      ? 'inset 0 1px 1px rgba(255,255,255,0.4)' 
      : 'inset 0 -1px 1px rgba(255,255,255,0.2)';
    
    return {
      boxShadow: `${innerGlow}, ${baseShadow}`,
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
   * Generate diffused LED styles for sub-surface scattering effect
   * Creates the appearance of LEDs buried under translucent plastic
   */
  static getDiffusedLEDStyle(status: 'off' | 'on' | 'error' | 'warning', intensity: number = 1): React.CSSProperties {
    const color = tokenUtils.getLEDColor(status);
    const glowIntensity = status === 'off' ? 0 : intensity;
    
    if (glowIntensity === 0) {
      return {
        backgroundColor: 'rgba(200, 200, 200, 0.3)', // Dim plastic appearance when off
        border: '1px solid rgba(180, 180, 180, 0.4)',
        filter: 'blur(0px)',
        transition: `all ${industrialTokens.animations.mechanical.duration.normal} ${industrialTokens.animations.mechanical.easing}`,
      };
    }

    return {
      backgroundColor: color,
      // Multi-layer glow for sub-surface scattering
      boxShadow: `
        inset 0 0 ${4 * glowIntensity}px rgba(255, 255, 255, 0.6),
        0 0 ${8 * glowIntensity}px ${color},
        0 0 ${16 * glowIntensity}px ${color},
        0 0 ${24 * glowIntensity}px ${color}
      `,
      // Soft blur for diffused light through plastic
      filter: `blur(${0.5 * glowIntensity}px)`,
      // Subtle border for plastic housing
      border: `1px solid rgba(255, 255, 255, ${0.2 * glowIntensity})`,
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

  /**
   * Generate micro-texture for premium soft plastic finish
   * Simulates the pebble finish found on high-end electronics
   */
  static getMicroTexture(intensity: 'subtle' | 'normal' | 'fine' = 'normal'): React.CSSProperties {
    const textures = {
      subtle: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.015'/%3E%3C/svg%3E\")",
      normal: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.02'/%3E%3C/svg%3E\")",
      fine: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='1.2' numOctaves='5' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.025'/%3E%3C/svg%3E\")"
    };

    return {
      backgroundImage: textures[intensity],
    };
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