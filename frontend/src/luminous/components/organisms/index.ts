/**
 * Organism Components
 * 
 * Complex components composed of molecules and atoms that form distinct sections
 * of the interface. These are the major functional areas of the dashboard.
 */

// Export organism components here as they are created
export { AppShell } from './AppShell';
export { Director } from './Director';
export { Canvas } from './Canvas';
export { ComplianceGauge } from './ComplianceGauge';
export { ContextDeck } from './ContextDeck';
export { TwinData } from './TwinData';
export { BrandGraphModal } from './BrandGraphModal';
export { Critic } from './Critic';

// Lazy-loaded versions for code splitting
export { LazyComplianceGauge } from './LazyComplianceGauge';
