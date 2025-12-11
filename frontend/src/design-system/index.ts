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

// Industrial Components
export {
  BaseIndustrialComponent,
  ManufacturingDetails,
  IndustrialCard,
  IndustrialButton,
  IndustrialInput,
  IndustrialIndicator,
  IndustrialIndicatorGroup,
  IndustrialComponents,
  type IndustrialComponentProps,
  type BaseIndustrialComponentProps,
  type IndustrialCardProps,
  type IndustrialButtonProps,
  type IndustrialInputProps,
  type IndustrialIndicatorProps,
  type IndustrialIndicatorGroupProps,
} from './components';



// Polished Components (Radix UI based)
export { PolishedIndustrialButton } from './components/PolishedIndustrialButton';
export { PolishedIndustrialCard } from './components/PolishedIndustrialCard';
export { PolishedIndustrialInput } from './components/PolishedIndustrialInput';
export {
  PolishedIndustrialTabs,
  PolishedIndustrialTabsList,
  PolishedIndustrialTabsTrigger,
  PolishedIndustrialTabsContent,
} from './components/PolishedIndustrialTabs';
export type { PolishedIndustrialButtonProps } from './components/PolishedIndustrialButton';
export type { PolishedIndustrialCardProps } from './components/PolishedIndustrialCard';
export type { PolishedIndustrialInputProps } from './components/PolishedIndustrialInput';

// Demos
export { IndustrialDemo } from './demo';
export { PolishedIndustrialDemo } from './PolishedDemo';

/**
 * Design System Version
 */
export const DESIGN_SYSTEM_VERSION = '1.0.0';

// Import the utilities for the industrial object
import { industrialTokens as tokens, tokenUtils } from './tokens';
import { NeumorphicUtils } from './neumorphic';
import { AnimationUtils } from './animations';
import { IndustrialComponents } from './components';

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
  components: IndustrialComponents,
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