/**
 * Industrial Design System - Main Export
 * 
 * Complete design system for industrial skeuomorphic interfaces
 */

// Core design tokens
export { 
  industrialTokens, 
  tokenUtils,
  type IndustrialDesignTokens 
} from './tokens';

// Neumorphic utilities
export { 
  NeumorphicUtils, 
  useNeumorphicPress,
  type ShadowVariant,
  type ShadowType 
} from './neumorphic';

// Animation system
export { 
  AnimationUtils, 
  mechanicalEasing, 
  animationDurations, 
  mechanicalKeyframes,
  useMechanicalAnimation 
} from './animations';

/**
 * Design System Version
 */
export const DESIGN_SYSTEM_VERSION = '1.0.0';

// Import the utilities for the industrial object
import { industrialTokens as tokens, tokenUtils } from './tokens';
import { NeumorphicUtils } from './neumorphic';
import { AnimationUtils } from './animations';

/**
 * Quick access utilities
 */
export const industrial = {
  tokens,
  utils: {
    shadow: tokenUtils.getShadow,
    ledColor: tokenUtils.getLEDColor,
    easing: tokenUtils.getMechanicalEasing,
    customShadow: tokenUtils.calculateCustomShadow,
  },
  neumorphic: NeumorphicUtils,
  animation: AnimationUtils,
};

/**
 * Design system configuration
 */
export const designSystemConfig = {
  version: DESIGN_SYSTEM_VERSION,
  theme: 'industrial-skeuomorphic',
  lightSource: { x: -1, y: -1 }, // Top-left illumination
  shadowCompliance: 'unidirectional',
  animationProfile: 'mechanical',
};

export default industrial;