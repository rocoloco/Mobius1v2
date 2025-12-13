/**
 * LazyComplianceGauge - Code-split ComplianceGauge with lazy-loaded VisX
 * 
 * Lazy loads the ComplianceGauge component which includes VisX chart library.
 * This reduces initial bundle size by deferring chart library loading.
 * 
 * Requirements: All (Performance optimization)
 */

import { lazy, Suspense } from 'react';
import { GlassPanel } from '../atoms/GlassPanel';

// Lazy load ComplianceGauge - VisX charts will be in this chunk
const ComplianceGauge = lazy(() => 
  import('./ComplianceGauge').then(module => ({ default: module.ComplianceGauge }))
);

interface Violation {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
}

interface LazyComplianceGaugeProps {
  score: number;
  violations: Violation[];
  onViolationClick: (violationId: string) => void;
  auditUnavailable?: boolean;
}

/**
 * ComplianceGaugeSkeleton - Loading placeholder for the gauge
 */
function ComplianceGaugeSkeleton() {
  return (
    <GlassPanel className="h-full" data-testid="compliance-gauge-skeleton">
      <div className="h-full flex flex-col overflow-hidden">
        {/* Gauge skeleton */}
        <div className="flex-shrink-0 flex items-center justify-center pt-4 pb-2 px-4">
          <div className="relative w-[120px] h-[120px]">
            <div 
              className="w-full h-full rounded-full animate-pulse"
              style={{ 
                background: 'conic-gradient(rgba(255,255,255,0.1) 0deg, rgba(255,255,255,0.05) 360deg)',
                border: '8px solid rgba(255,255,255,0.05)',
              }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-12 h-6 rounded bg-white/5 animate-pulse" />
            </div>
          </div>
        </div>
        
        {/* Violations skeleton */}
        <div className="flex-1 overflow-hidden flex flex-col border-t border-white/10">
          <div className="flex-shrink-0 p-4">
            <div className="w-20 h-3 rounded bg-white/5 animate-pulse" />
          </div>
          <div className="flex-1 px-4 pb-2 space-y-2">
            <div className="h-10 rounded-lg bg-white/5 animate-pulse" />
            <div className="h-10 rounded-lg bg-white/5 animate-pulse" />
            <div className="h-10 rounded-lg bg-white/5 animate-pulse" />
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}

/**
 * LazyComplianceGauge - Wrapper that lazy loads the ComplianceGauge
 * 
 * Use this component for code splitting when the gauge is not immediately visible
 * or when optimizing initial page load.
 */
export function LazyComplianceGauge(props: LazyComplianceGaugeProps) {
  return (
    <Suspense fallback={<ComplianceGaugeSkeleton />}>
      <ComplianceGauge {...props} />
    </Suspense>
  );
}

export default LazyComplianceGauge;
