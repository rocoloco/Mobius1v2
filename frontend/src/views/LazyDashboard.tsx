/**
 * LazyDashboard - Code-split Dashboard with lazy-loaded components
 * 
 * Implements code splitting for performance optimization:
 * - Dashboard is loaded as a separate chunk
 * - VisX chart components are lazy-loaded
 * 
 * Requirements: All (Performance optimization)
 */

import { lazy, Suspense } from 'react';
import { GlassPanel } from '../luminous/components/atoms/GlassPanel';
import { luminousTokens } from '../luminous/tokens';

// Lazy load the Dashboard component - creates a separate chunk
const Dashboard = lazy(() => import('./Dashboard').then(module => ({ default: module.Dashboard })));

/**
 * DashboardSkeleton - Loading placeholder while Dashboard chunk loads
 */
function DashboardSkeleton() {
  return (
    <div 
      className="min-h-screen"
      style={{ backgroundColor: luminousTokens.colors.void }}
    >
      {/* Header skeleton */}
      <div 
        className="h-16 border-b border-white/10"
        style={{ 
          backgroundColor: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: luminousTokens.effects.backdropBlur,
        }}
      >
        <div className="h-full flex items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-white/5 animate-pulse" />
            <div className="w-48 h-4 rounded bg-white/5 animate-pulse" />
          </div>
          <div className="flex items-center gap-4">
            <div className="w-3 h-3 rounded-full bg-white/5 animate-pulse" />
            <div className="w-8 h-8 rounded-lg bg-white/5 animate-pulse" />
            <div className="w-8 h-8 rounded-full bg-white/5 animate-pulse" />
          </div>
        </div>
      </div>
      
      {/* Grid skeleton */}
      <div className="p-4 grid grid-cols-4 grid-rows-3 gap-4" style={{ height: 'calc(100vh - 64px)' }}>
        {/* Director zone */}
        <GlassPanel className="col-span-1 row-span-2">
          <div className="h-full flex flex-col p-4 gap-4">
            <div className="flex-1 space-y-3">
              <div className="w-3/4 h-4 rounded bg-white/5 animate-pulse" />
              <div className="w-1/2 h-4 rounded bg-white/5 animate-pulse" />
            </div>
            <div className="h-12 rounded-xl bg-white/5 animate-pulse" />
          </div>
        </GlassPanel>
        
        {/* Canvas zone */}
        <GlassPanel className="col-span-2 row-span-3">
          <div className="h-full flex items-center justify-center">
            <div className="w-32 h-32 rounded-lg bg-white/5 animate-pulse" />
          </div>
        </GlassPanel>
        
        {/* Gauge zone */}
        <GlassPanel className="col-span-1 row-span-1">
          <div className="h-full flex items-center justify-center p-4">
            <div className="w-24 h-24 rounded-full bg-white/5 animate-pulse" />
          </div>
        </GlassPanel>
        
        {/* Context zone */}
        <GlassPanel className="col-span-1 row-span-1">
          <div className="h-full p-4 space-y-2">
            <div className="w-full h-8 rounded-full bg-white/5 animate-pulse" />
            <div className="w-full h-8 rounded-full bg-white/5 animate-pulse" />
            <div className="w-full h-8 rounded-full bg-white/5 animate-pulse" />
          </div>
        </GlassPanel>
        
        {/* Twin zone */}
        <GlassPanel className="col-span-1 row-span-2">
          <div className="h-full p-4 space-y-3">
            <div className="w-1/2 h-4 rounded bg-white/5 animate-pulse" />
            <div className="flex gap-2">
              <div className="w-12 h-12 rounded-lg bg-white/5 animate-pulse" />
              <div className="w-12 h-12 rounded-lg bg-white/5 animate-pulse" />
            </div>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}

/**
 * LazyDashboard Props
 */
export interface LazyDashboardProps {
  brandId: string;
  initialSessionId?: string;
  onSettingsClick?: () => void;
}

/**
 * LazyDashboard - Wrapper that lazy loads the Dashboard component
 * 
 * Use this component instead of Dashboard for automatic code splitting.
 * The Dashboard chunk will only be loaded when this component is rendered.
 * 
 * @param brandId - The brand ID to use for generation and constraints
 * @param initialSessionId - Optional session ID to resume a previous session
 * @param onSettingsClick - Callback when settings icon is clicked
 */
export function LazyDashboard(props: LazyDashboardProps) {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <Dashboard {...props} />
    </Suspense>
  );
}

export default LazyDashboard;
