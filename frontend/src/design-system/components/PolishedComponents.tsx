/**
 * Polished Industrial Components - Migration Layer
 * 
 * This file provides a unified export of all polished industrial components
 * and migration utilities for existing application components.
 */

// Export all polished components
export { PolishedIndustrialButton } from './PolishedIndustrialButton';
export { PolishedIndustrialCard } from './PolishedIndustrialCard';
export { PolishedIndustrialInput } from './PolishedIndustrialInput';
export { PolishedIndustrialTabs } from './PolishedIndustrialTabs';

// Export types
export type { PolishedIndustrialButtonProps } from './PolishedIndustrialButton';
export type { PolishedIndustrialCardProps } from './PolishedIndustrialCard';
export type { PolishedIndustrialInputProps } from './PolishedIndustrialInput';

// Re-export industrial components for backward compatibility
export {
  IndustrialCard,
  IndustrialButton,
  IndustrialInput,
  IndustrialIndicator,
  IndustrialIndicatorGroup,
  HexHeadBolt,
  PhillipsHeadBolt,
  TorxHeadBolt,
  FlatheadBolt
} from './index';

// Migration aliases for easy component replacement
export { PolishedIndustrialButton as MigratedButton } from './PolishedIndustrialButton';
export { PolishedIndustrialCard as MigratedCard } from './PolishedIndustrialCard';
export { PolishedIndustrialInput as MigratedInput } from './PolishedIndustrialInput';