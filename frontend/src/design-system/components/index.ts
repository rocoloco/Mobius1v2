/**
 * Industrial Design System - Components Export
 * 
 * Core industrial components with skeuomorphic styling
 */

// Base component
export { 
  BaseIndustrialComponent, 
  ManufacturingDetails,
  type IndustrialComponentProps,
  type BaseIndustrialComponentProps 
} from './base';

// Industrial Card
export { 
  IndustrialCard,
  type IndustrialCardProps 
} from './IndustrialCard';

// Industrial Button
export { 
  IndustrialButton,
  type IndustrialButtonProps 
} from './IndustrialButton';

// Industrial Input
export { 
  IndustrialInput,
  type IndustrialInputProps 
} from './IndustrialInput';

// Industrial Indicator
export { 
  IndustrialIndicator,
  IndustrialIndicatorGroup,
  type IndustrialIndicatorProps,
  type IndustrialIndicatorGroupProps 
} from './IndustrialIndicator';

// Industrial Bolts
export {
  PhillipsHeadBolt,
  FlatheadBolt,
  TorxHeadBolt,
  HexHeadBolt
} from './IndustrialBolts';

// Enhanced Industrial Button
export {
  EnhancedIndustrialButton,
  type EnhancedIndustrialButtonProps
} from './EnhancedIndustrialButton';

// Industrial Manufacturing Details
export {
  VentGrille,
  ConnectorPort,
  SurfaceTexture,
  WarningLabel,
  SerialPlate
} from './IndustrialManufacturing';

// Import components for the collection
import { IndustrialCard } from './IndustrialCard';
import { IndustrialButton } from './IndustrialButton';
import { IndustrialInput } from './IndustrialInput';
import { IndustrialIndicator, IndustrialIndicatorGroup } from './IndustrialIndicator';
import { PhillipsHeadBolt, FlatheadBolt, TorxHeadBolt, HexHeadBolt } from './IndustrialBolts';
import { EnhancedIndustrialButton } from './EnhancedIndustrialButton';
import { VentGrille, ConnectorPort, SurfaceTexture, WarningLabel, SerialPlate } from './IndustrialManufacturing';

/**
 * Component collection for easy access
 */
export const IndustrialComponents = {
  Card: IndustrialCard,
  Button: IndustrialButton,
  EnhancedButton: EnhancedIndustrialButton,
  Input: IndustrialInput,
  Indicator: IndustrialIndicator,
  IndicatorGroup: IndustrialIndicatorGroup,
  PhillipsHeadBolt,
  FlatheadBolt,
  TorxHeadBolt,
  HexHeadBolt,
  VentGrille,
  ConnectorPort,
  SurfaceTexture,
  WarningLabel,
  SerialPlate,
};

export default IndustrialComponents;