/**
 * Dashboard View
 * 
 * Main dashboard view integrating all Luminous organisms into the BentoGrid layout.
 * Connects to DashboardContext for state management and real-time updates.
 * 
 * Requirements: All (1.1-14.8)
 */

import { useState, useCallback, useMemo, useEffect } from 'react';
import { DashboardProvider, useDashboard } from '../context/DashboardContext';
import { useBrandContext } from '../context/BrandContext';
import { AppShell } from '../luminous/components/organisms/AppShell';
import { StudioLayout } from '../luminous/layouts/StudioLayout';
import { Director } from '../luminous/components/organisms/Director';
import { Canvas } from '../luminous/components/organisms/Canvas';
import { Critic } from '../luminous/components/organisms/Critic';
import { AriaLiveRegions } from '../luminous/components/atoms/AriaLiveRegions';
import { BrandGraphModal } from '../luminous/components/organisms/BrandGraphModal';
import type { BrandGraphResponse } from '../api/types';

interface DashboardContentProps {
  onSettingsClick?: () => void;
  brandGraph?: BrandGraphResponse | null;
  brandsLoading?: boolean;
}

/**
 * DashboardContent - Inner component that uses the dashboard context
 * 
 * Separated from Dashboard to allow useDashboard hook usage within DashboardProvider
 */
function DashboardContent({ onSettingsClick, brandGraph: propsBrandGraph, brandsLoading = false }: DashboardContentProps) {
  // Brand context for brand selection
  const {
    brands,
    selectedBrandId,
    shouldShowBrandSelector,
    selectBrand,
  } = useBrandContext();

  const {
    // State
    sessionId,
    brandId,
    status,
    isSubmitting,
    currentImageUrl,
    complianceScore,
    violations,
    twinData,
    versions,
    currentVersionIndex,
    messages,
    connectionStatus,
    error,
    
    // Actions
    submitPrompt,
    loadVersion,
    acceptCorrection,
    requestTweak,
    retryGeneration,
    clearError,
    startNewSession,
  } = useDashboard();

  // Brand graph data - use from props or load in background
  const [brandGraph, setBrandGraph] = useState<BrandGraphResponse | null>(propsBrandGraph || null);
  
  // Brand Graph modal state
  const [isBrandGraphModalOpen, setIsBrandGraphModalOpen] = useState(false);
  
  // Track highlighted violation for Canvas bounding box highlighting
  const [highlightedViolationId, setHighlightedViolationId] = useState<string | null>(null);

  // ALL HOOKS MUST BE BEFORE ANY EARLY RETURNS (React rules of hooks)
  
  // Handle violation click from ComplianceGauge
  const handleViolationClick = useCallback((violationId: string) => {
    setHighlightedViolationId(violationId);
    
    // Clear highlight after 3 seconds
    setTimeout(() => {
      setHighlightedViolationId(null);
    }, 3000);
  }, []);

  // Handle prompt submission from Director
  // Default behavior: tweak existing image if one exists, otherwise new generation
  // User can click "+" button to explicitly start a new session
  const handleSubmit = useCallback((prompt: string) => {
    const hasExistingImage = !!currentImageUrl;
    const isFinished = status?.status === 'needs_review' || status?.status === 'completed';
    
    // If there's an existing image and job is finished, always tweak
    // This provides seamless multi-turn editing without keyword detection
    if (hasExistingImage && isFinished) {
      requestTweak(prompt);
    } else {
      // No existing image or job still in progress - new generation
      submitPrompt(prompt);
    }
  }, [status?.status, currentImageUrl, submitPrompt, requestTweak]);

  // Handle version change from Canvas
  const handleVersionChange = useCallback((index: number) => {
    loadVersion(index);
  }, [loadVersion]);

  // Handle accept correction from Canvas
  const handleAcceptCorrection = useCallback(() => {
    acceptCorrection();
  }, [acceptCorrection]);

  // Handle brand selection - clear session and start fresh
  const handleBrandSelect = useCallback((brandId: string) => {
    console.log('🔄 Switching to brand:', brandId);
    
    // Clear current session to start fresh with new brand
    startNewSession();
    
    // Select the brand
    selectBrand(brandId);
  }, [selectBrand, startNewSession]);

  // Map job status to Canvas status
  const canvasStatus = useMemo((): 'generating' | 'auditing' | 'complete' | 'error' | 'idle' => {
    // Default to 'idle' when no job is active
    if (!status) return 'idle';
    
    switch (status.status) {
      case 'pending':
      case 'processing':
      case 'generating':
        return 'generating';
      case 'auditing':
      case 'correcting':
        return 'auditing';
      case 'completed':
      case 'needs_review':
        return 'complete';
      case 'failed':
      case 'cancelled':
        return 'error';
      default:
        return 'idle';
    }
  }, [status]);

  // Map violations to the format expected by Canvas and ComplianceGauge
  const mappedViolations = useMemo(() => {
    return violations.map((v, index) => ({
      id: `violation-${index}`,
      severity: mapSeverity(v.severity),
      message: v.description,
      bounding_box: undefined as [number, number, number, number] | undefined,
    }));
  }, [violations]);

  // Map violations for Critic (includes 'info' severity)
  const criticViolations = useMemo(() => {
    return violations.map((v, index) => ({
      id: `violation-${index}`,
      severity: mapSeverityForGauge(v.severity),
      message: v.description,
    }));
  }, [violations]);

  // Prepare TwinData props - no fallback data to prevent layout shift
  const detectedColors = useMemo(() => {
    return twinData?.colors_detected || [];
  }, [twinData]);

  const detectedFonts = useMemo(() => {
    return twinData?.fonts_detected || [];
  }, [twinData]);
  
  // Get brand colors from brand graph - no fallback to prevent layout shift
  const brandColors = useMemo(() => {
    if (brandGraph?.visual_tokens?.colors?.length) {
      return brandGraph.visual_tokens.colors.map(color => color.hex);
    }
    return [];
  }, [brandGraph]);

  // Generate status message for aria-live regions
  const statusMessage = useMemo(() => {
    if (!status) return '';
    
    switch (status.status) {
      case 'pending':
        return 'Generation request queued';
      case 'processing':
      case 'generating':
        return 'Generating brand asset';
      case 'auditing':
        return 'Analyzing compliance';
      case 'correcting':
        return 'Applying auto-corrections';
      case 'completed':
        return complianceScore !== undefined 
          ? `Generation complete. Compliance score: ${Math.round(complianceScore)}%`
          : 'Generation complete';
      case 'needs_review':
        return 'Generation complete, review required';
      default:
        return '';
    }
  }, [status, complianceScore]);

  // Generate error message for aria-live regions
  const errorMessage = useMemo(() => {
    if (!error) return '';
    return `Error: ${error.message}`;
  }, [error]);

  // Determine if AI is generating - check isSubmitting for immediate feedback
  const isGenerating = isSubmitting || status?.status === 'generating' || status?.status === 'processing' || status?.status === 'pending';

  // Determine layout state for StudioLayout
  const layoutState = useMemo((): 'idle' | 'generating' | 'complete' => {
    if (isGenerating) return 'generating';
    if (canvasStatus === 'complete' || currentImageUrl) return 'complete';
    return 'idle';
  }, [isGenerating, canvasStatus, currentImageUrl]);

  // Critic is awake when generation is complete and we have results
  const isCriticAwake = layoutState === 'complete';

  // Get brand graph from BrandContext instead of fetching separately
  // This eliminates the duplicate API call
  useEffect(() => {
    // Use brand graph from context if available, otherwise use sample data
    if (brandId && !brandGraph) {
      // Only import sample data if we don't have real data
      import('../data/sampleBrand').then(({ sampleBrandGraph }) => {
        setBrandGraph(sampleBrandGraph);
      }).catch(console.error);
    }
  }, [brandId, brandGraph]);

  return (
    <AppShell
      connectionStatus={connectionStatus}
      onSettingsClick={onSettingsClick}
    >
      {/* Aria-live regions for screen reader announcements */}
      <AriaLiveRegions 
        statusMessage={statusMessage}
        errorMessage={errorMessage}
      />
      
      {/* Brand Graph Detail Modal */}
      {brandGraph && (
        <BrandGraphModal
          brandGraph={brandGraph}
          isOpen={isBrandGraphModalOpen}
          onClose={() => setIsBrandGraphModalOpen(false)}
          logoUrl={brands.find(b => b.id === selectedBrandId)?.logoUrl}
        />
      )}

      <StudioLayout
        state={layoutState}
        director={
          <Director
            sessionId={sessionId || 'new-session'}
            onSubmit={handleSubmit}
            isGenerating={isGenerating}
            messages={messages}
            error={error}
            onRetry={retryGeneration}
            onClearError={clearError}
            brandGraph={brandGraph ? {
              name: brandGraph.name,
              ruleCount: (brandGraph.identity_core?.negative_constraints?.length || 0) + 
                         (brandGraph.contextual_rules?.length || 0),
              colorCount: brandGraph.visual_tokens?.colors?.length || 0,
              archetype: brandGraph.identity_core?.archetype,
              logoUrl: brands.find(b => b.id === selectedBrandId)?.logoUrl,
            } : null}
            onBrandGraphClick={() => setIsBrandGraphModalOpen(true)}
            hasExistingImage={!!currentImageUrl}
            onNewSession={startNewSession}
            brandsLoading={brandsLoading}
            availableBrands={brands.map(b => ({
              id: b.id,
              name: b.name,
              colorCount: brandGraph?.visual_tokens?.colors?.length,
              ruleCount: (brandGraph?.identity_core?.negative_constraints?.length || 0) + 
                         (brandGraph?.contextual_rules?.length || 0),
              archetype: b.archetype,
              logoUrl: b.logoUrl,
            }))}
            selectedBrandId={selectedBrandId}
            shouldShowBrandSelector={shouldShowBrandSelector}
            onSelectBrand={handleBrandSelect}
          />
        }
        canvas={
          <Canvas
            imageUrl={currentImageUrl}
            violations={mappedViolations}
            versions={versions}
            currentVersion={currentVersionIndex}
            complianceScore={complianceScore ?? 0}
            status={canvasStatus}
            highlightedViolationId={highlightedViolationId}
            onVersionChange={handleVersionChange}
            onAcceptCorrection={handleAcceptCorrection}
            onCreateSimilar={() => submitPrompt('Create another image like this one with the same style and approach')}
            onTryDifferentSizes={() => submitPrompt('Create variations of this design for different formats: Instagram story, LinkedIn banner, and business card')}
            onStartFresh={startNewSession}
            currentPrompt={messages.find(m => m.role === 'user')?.content || ''}
          />
        }
        critic={
          <Critic
            isAwake={isCriticAwake}
            score={complianceScore ?? 0}
            violations={criticViolations}
            detectedColors={detectedColors}
            brandColors={brandColors}
            detectedFonts={detectedFonts}
            onViolationClick={handleViolationClick}
          />
        }
      />
    </AppShell>
  );
}

/**
 * Map API severity to Canvas severity format
 */
function mapSeverity(severity: 'low' | 'medium' | 'high' | 'critical'): 'critical' | 'warning' {
  switch (severity) {
    case 'critical':
    case 'high':
      return 'critical';
    case 'medium':
    case 'low':
    default:
      return 'warning';
  }
}

/**
 * Map API severity to ComplianceGauge severity format (includes 'info')
 */
function mapSeverityForGauge(severity: 'low' | 'medium' | 'high' | 'critical'): 'critical' | 'warning' | 'info' {
  switch (severity) {
    case 'critical':
      return 'critical';
    case 'high':
    case 'medium':
      return 'warning';
    case 'low':
    default:
      return 'info';
  }
}

/**
 * Dashboard Props
 */
export interface DashboardProps {
  brandId?: string;
  initialSessionId?: string;
  onSettingsClick?: () => void;
  brandGraph?: BrandGraphResponse | null;
  brandsLoading?: boolean;
  noBrands?: boolean;
}

/**
 * Dashboard - Main dashboard view with DashboardProvider wrapper
 * 
 * Integrates all Luminous organisms into the BentoGrid layout:
 * - Director: Multi-turn chat interface (top-left)
 * - Canvas: Image viewport with bounding boxes (center)
 * - ComplianceGauge: Radial score chart with violations (top-right)
 * - ContextDeck: Brand constraints visualization (bottom-left)
 * - TwinData: Detected visual tokens inspector (bottom-right)
 * 
 * The dashboard renders immediately and loads brand data asynchronously.
 * This provides a better UX by showing the app shell while data loads.
 * 
 * @param brandId - The brand ID to use for generation and constraints (optional during loading)
 * @param initialSessionId - Optional session ID to resume a previous session
 * @param onSettingsClick - Callback when settings icon is clicked
 * @param brandsLoading - Whether brands are still being fetched
 * @param noBrands - Whether no brands exist after loading completes
 */
export function Dashboard({ 
  brandId, 
  initialSessionId,
  onSettingsClick,
  brandGraph: propsBrandGraph,
  brandsLoading = false,
  noBrands = false,
}: DashboardProps) {
  // Debug logging
  useEffect(() => {
    console.log('🔍 Dashboard Props:', { brandId, brandsLoading, noBrands });
  }, [brandId, brandsLoading, noBrands]);

  // Show empty state if no brands exist after loading completes
  if (noBrands) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center text-white">
          <h2 className="text-xl font-semibold mb-2">No brands found</h2>
          <p className="text-gray-400">Create a brand to get started.</p>
        </div>
      </div>
    );
  }

  // Use a placeholder brand ID while loading - DashboardProvider handles this gracefully
  const effectiveBrandId = brandId || 'loading';

  return (
    <DashboardProvider 
      brandId={effectiveBrandId} 
      initialSessionId={initialSessionId}
      brandsLoading={brandsLoading}
    >
      <DashboardContent 
        onSettingsClick={onSettingsClick} 
        brandGraph={propsBrandGraph}
        brandsLoading={brandsLoading}
      />
    </DashboardProvider>
  );
}
