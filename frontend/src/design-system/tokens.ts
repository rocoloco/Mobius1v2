/**
 * Industrial Design System - Design Tokens
 * 
 * Comprehensive design token system with mathematical shadow calculations
 * for neumorphic industrial interfaces.
 */

export interface IndustrialDesignTokens {
  colors: {
    surface: {
      primary: string;
      secondary: string;
      tertiary: string;
    };
    shadows: {
      light: string;
      dark: string;
      accent: string;
    };
    text: {
      primary: string;
      secondary: string;
      muted: string;
    };
    led: {
      off: string;
      on: string;
      error: string;
      warning: string;
    };
  };
  shadows: {
    neumorphic: {
      raised: {
        subtle: string;
        normal: string;
        deep: string;
      };
      recessed: {
        subtle: string;
        normal: string;
        deep: string;
      };
    };
    glow: {
      led: string;
      accent: string;
    };
  };
  animations: {
    mechanical: {
      easing: string;
      duration: {
        fast: string;
        normal: string;
        slow: string;
      };
    };
    press: {
      transform: string;
      shadowInvert: boolean;
      duration: string;
    };
  };
  manufacturing: {
    screws: {
      size: string;
      color: string;
      shadow: string;
    };
    vents: {
      slotWidth: string;
      slotSpacing: string;
      color: string;
    };
  };
}

/**
 * Mathematical shadow calculation system for neumorphic effects
 * Implements unidirectional illumination compliance with consistent light source
 */
class ShadowCalculator {
  private lightSource = { x: -1, y: -1 }; // Top-left light source
  private baseColor = '#babecc'; // Dark shadow color
  private lightColor = '#ffffff'; // Light shadow color

  /**
   * Calculate neumorphic shadow with mathematical precision
   * @param depth Shadow depth multiplier (1 = normal, 0.5 = subtle, 1.5 = deep)
   * @param inset Whether to create inset (recessed) shadows
   */
  calculateShadow(depth: number = 1, inset: boolean = false): string {
    const baseDistance = 8 * depth;
    const blurRadius = 16 * depth;
    
    const darkX = baseDistance * this.lightSource.x * -1;
    const darkY = baseDistance * this.lightSource.y * -1;
    const lightX = baseDistance * this.lightSource.x;
    const lightY = baseDistance * this.lightSource.y;
    
    const insetPrefix = inset ? 'inset ' : '';
    
    return `${insetPrefix}${darkX}px ${darkY}px ${blurRadius}px ${this.baseColor}, ${insetPrefix}${lightX}px ${lightY}px ${blurRadius}px ${this.lightColor}`;
  }

  /**
   * Generate all shadow variants for a given type
   */
  generateShadowSet(inset: boolean = false) {
    return {
      subtle: this.calculateShadow(0.5, inset),
      normal: this.calculateShadow(1, inset),
      deep: this.calculateShadow(1.5, inset),
    };
  }
}

// Initialize shadow calculator
const shadowCalc = new ShadowCalculator();

/**
 * Complete Industrial Design Token System
 */
export const industrialTokens: IndustrialDesignTokens = {
  colors: {
    surface: {
      primary: '#e0e5ec',
      secondary: '#d1d9e6',
      tertiary: '#c8d0e7',
    },
    shadows: {
      light: '#ffffff',
      dark: '#babecc',
      accent: '#ff4757',
    },
    text: {
      primary: '#2d3436',
      secondary: '#636e72',
      muted: '#b2bec3',
    },
    led: {
      off: '#74b9ff',
      on: '#00b894',
      error: '#e17055',
      warning: '#fdcb6e',
    },
  },
  
  shadows: {
    neumorphic: {
      raised: shadowCalc.generateShadowSet(false),
      recessed: shadowCalc.generateShadowSet(true),
    },
    glow: {
      led: '0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor',
      accent: '0 0 15px #ff4757, 0 0 30px #ff4757',
    },
  },
  
  animations: {
    mechanical: {
      easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      duration: {
        fast: '150ms',
        normal: '250ms',
        slow: '400ms',
      },
    },
    press: {
      transform: 'translateY(2px)',
      shadowInvert: true,
      duration: '100ms',
    },
  },
  
  manufacturing: {
    screws: {
      size: '8px',
      color: '#95a5a6',
      shadow: '1px 1px 2px rgba(0,0,0,0.3)',
    },
    vents: {
      slotWidth: '2px',
      slotSpacing: '4px',
      color: 'rgba(0,0,0,0.1)',
    },
  },
};

/**
 * Utility functions for working with design tokens
 */
export const tokenUtils = {
  /**
   * Get shadow by variant and type
   */
  getShadow: (variant: 'subtle' | 'normal' | 'deep', type: 'raised' | 'recessed' = 'raised') => {
    return industrialTokens.shadows.neumorphic[type][variant];
  },

  /**
   * Get LED color by status
   */
  getLEDColor: (status: 'off' | 'on' | 'error' | 'warning') => {
    return industrialTokens.colors.led[status];
  },

  /**
   * Get mechanical easing function
   */
  getMechanicalEasing: () => {
    return industrialTokens.animations.mechanical.easing;
  },

  /**
   * Calculate custom shadow with specific depth
   */
  calculateCustomShadow: (depth: number, inset: boolean = false) => {
    return shadowCalc.calculateShadow(depth, inset);
  },
};

export default industrialTokens;