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
      
      {/* Studio layout skeleton - 3 column */}
      <div className="flex gap-6 p-6" style={{ height: 'calc(100vh - 64px)' }}>
        {/* Director zone - 25% width */}
        <GlassPanel className="w-1/4">
          <div className="h-full flex flex-col p-4 gap-4">
            {/* Brand graph indicator skeleton */}
            <div className="flex items-center gap-2 pb-3 border-b border-white/10">
              <div className="w-4 h-4 rounded bg-white/5 animate-pulse" />
              <div className="w-24 h-3 rounded bg-white/5 animate-pulse" />
              <div className="w-16 h-3 rounded-full bg-white/5 animate-pulse" />
            </div>
            <div className="flex-1 space-y-3">
              <div className="w-3/4 h-4 rounded bg-white/5 animate-pulse" />
              <div className="w-1/2 h-4 rounded bg-white/5 animate-pulse" />
            </div>
            <div className="h-12 rounded-xl bg-white/5 animate-pulse" />
          </div>
        </GlassPanel>
        
        {/* Canvas zone - 50% width */}
        <GlassPanel className="w-2/4">
          <div className="h-full flex items-center justify-center">
            <div className="w-32 h-32 rounded-lg bg-white/5 animate-pulse" />
          </div>
        </GlassPanel>
        
        {/* Critic zone - 25% width (sleeping state) */}
        <GlassPanel className="w-1/4 opacity-40">
          <div className="h-full flex flex-col items-center justify-center">
            <div className="w-8 h-8 rounded bg-white/5 animate-pulse mb-4" />
            <div className="w-24 h-3 rounded bg-white/5 animate-pulse" />
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
