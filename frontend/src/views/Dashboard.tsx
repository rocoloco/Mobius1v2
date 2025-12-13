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
import { AppShell } from '../luminous/components/organisms/AppShell';
import { BentoGrid } from '../luminous/layouts/BentoGrid';
import { Director } from '../luminous/components/organisms/Director';
import { Canvas } from '../luminous/components/organisms/Canvas';
import { ComplianceGauge } from '../luminous/components/organisms/ComplianceGauge';
import { ContextDeck } from '../luminous/components/organisms/ContextDeck';
import { TwinData } from '../luminous/components/organisms/TwinData';
import { AriaLiveRegions } from '../luminous/components/atoms/AriaLiveRegions';
import { apiClient } from '../api/client';
import type { BrandGraphResponse } from '../api/types';



interface DashboardContentProps {
  onSettingsClick?: () => void;
}

/**
 * DashboardContent - Inner component that uses the dashboard context
 * 
 * Separated from Dashboard to allow useDashboard hook usage within DashboardProvider
 */
function DashboardContent({ onSettingsClick }: DashboardContentProps) {
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
    retryGeneration,
    clearError,
  } = useDashboard();

  // Brand graph data - loaded in background, doesn't block UI
  const [brandGraph, setBrandGraph] = useState<BrandGraphResponse | null>(null);
  
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
  const handleSubmit = useCallback((prompt: string) => {
    submitPrompt(prompt);
  }, [submitPrompt]);

  // Handle version change from Canvas
  const handleVersionChange = useCallback((index: number) => {
    loadVersion(index);
  }, [loadVersion]);

  // Handle accept correction from Canvas
  const handleAcceptCorrection = useCallback(() => {
    acceptCorrection();
  }, [acceptCorrection]);

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

  // Map violations for ComplianceGauge (includes 'info' severity)
  const gaugeViolations = useMemo(() => {
    return violations.map((v, index) => ({
      id: `violation-${index}`,
      severity: mapSeverityForGauge(v.severity),
      message: v.description,
    }));
  }, [violations]);

  // Extract active constraints from violations for ContextDeck highlighting
  const activeConstraints = useMemo(() => {
    // Extract constraint IDs from violations that should highlight constraint cards
    return violations.map((_, index) => `violation-${index}`);
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

  // Fetch brand graph in background - doesn't block initial render
  useEffect(() => {
    async function fetchBrandGraph() {
      try {
        const graph = await apiClient.get<BrandGraphResponse>(`/brands/${brandId}/graph`);
        setBrandGraph(graph);
      } catch (err) {
        console.error('Failed to fetch brand graph, using sample data:', err);
        // Import sample data dynamically to avoid bundling when not needed
        const { sampleBrandGraph } = await import('../data/sampleBrand');
        setBrandGraph(sampleBrandGraph);
      }
    }

    if (brandId) {
      fetchBrandGraph();
    }
  }, [brandId]);

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
      
      <BentoGrid
        director={
          <Director
            sessionId={sessionId || 'new-session'}
            onSubmit={handleSubmit}
            isGenerating={isGenerating}
            messages={messages}
            error={error}
            onRetry={retryGeneration}
            onClearError={clearError}
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
          />
        }
        gauge={
          <ComplianceGauge
            score={complianceScore ?? 0}
            violations={gaugeViolations}
            onViolationClick={handleViolationClick}
          />
        }
        context={
          <ContextDeck
            brandId={brandId}
            activeConstraints={activeConstraints}
            brandGraph={brandGraph}
            loading={false}
          />
        }
        twin={
          <TwinData
            detectedColors={detectedColors}
            brandColors={brandColors}
            detectedFonts={detectedFonts}
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
  brandId: string;
  initialSessionId?: string;
  onSettingsClick?: () => void;
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
 * @param brandId - The brand ID to use for generation and constraints
 * @param initialSessionId - Optional session ID to resume a previous session
 * @param onSettingsClick - Callback when settings icon is clicked
 */
export function Dashboard({ 
  brandId, 
  initialSessionId,
  onSettingsClick,
}: DashboardProps) {
  return (
    <DashboardProvider brandId={brandId} initialSessionId={initialSessionId}>
      <DashboardContent onSettingsClick={onSettingsClick} />
    </DashboardProvider>
  );
}
