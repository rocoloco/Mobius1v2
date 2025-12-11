/**
 * Real-Time Brand Compliance Monitoring Components
 * 
 * Export all monitoring dashboard components and utilities.
 */

export { default as CRTOscilloscope } from './CRTOscilloscope';
export type { CRTOscilloscopeProps } from './CRTOscilloscope';

export { default as IndustrialOscilloscope } from './IndustrialOscilloscope';
export type { IndustrialOscilloscopeProps } from './IndustrialOscilloscope';

export { default as HybridOscilloscope } from './HybridOscilloscope';
export type { HybridOscilloscopeProps } from './HybridOscilloscope';

export { default as TerminalTeleprinter } from './TerminalTeleprinter';
export type { TerminalTeleprinterProps } from './TerminalTeleprinter';

export { default as CRTOscilloscopeDemo } from './CRTOscilloscopeDemo';
export { default as HybridOscilloscopeDemo } from './HybridOscilloscopeDemo';
export { default as TerminalTeleprinterDemo } from './TerminalTeleprinterDemo';
export { default as DesignComparisonDemo } from './DesignComparisonDemo';

export { 
  generateCRTStyles, 
  crtSVGFilters, 
  CRTPerformanceOptimizer, 
  injectCRTStyles,
  defaultCRTConfig,
  type CRTEffectsConfig 
} from './CRTEffects';

// Re-export monitoring types for convenience
export type {
  ComplianceScores,
  MonitoringComponentProps,
  ReasoningLog,
  ColorAnalysisData,
  ConstraintStatus,
  AuditStatus,
  WebSocketMessage,
  MonitoringState,
  AnimationState,
} from '../../types/monitoring';