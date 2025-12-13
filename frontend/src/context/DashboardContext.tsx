/**
 * DashboardContext
 * 
 * Central state management for the Luminous Dashboard.
 * Manages job status, session history, real-time updates, and user actions.
 * 
 * Requirements: 9.1-9.10, 10.1-10.7
 */

import React, { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react';
import { useJobStatus } from '../hooks/useJobStatus';
import { useSessionHistory } from '../hooks/useSessionHistory';
import { apiClient } from '../api/client';
import { RETRY_CONFIGS } from '../utils/retry';
import type {
  JobStatusResponse,
  GenerateRequest,
  GenerateResponse,
  Violation,
  TwinData,
  Version,
} from '../api/types';

// Chat message type
export interface ChatMessage {
  role: 'user' | 'system' | 'error';
  content: string;
  timestamp: Date;
}

// Dashboard state interface
export interface DashboardState {
  // Job tracking
  jobId: string | null;
  sessionId: string | null;
  brandId: string;
  
  // Job status
  status: JobStatusResponse | null;
  isPolling: boolean;
  isSubmitting: boolean;
  isTimedOut: boolean;
  
  // Image and audit data
  currentImageUrl?: string;
  complianceScore?: number;
  violations: Violation[];
  twinData?: TwinData;
  
  // Session history
  versions: Version[];
  currentVersionIndex: number;
  currentVersion: Version | null;
  
  // Chat history
  messages: ChatMessage[];
  
  // Connection state
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
  
  // Error state
  error: Error | null;
}

// Dashboard actions interface
export interface DashboardActions {
  submitPrompt: (prompt: string) => Promise<void>;
  loadVersion: (index: number) => void;
  acceptCorrection: () => Promise<void>;
  requestTweak: (instruction: string) => Promise<void>;
  retryGeneration: () => Promise<void>;
  clearError: () => void;
  startNewSession: () => void;
}

// Combined context value (kept for backward compatibility)
export interface DashboardContextValue extends DashboardState, DashboardActions {}

// Create separate contexts to prevent unnecessary re-renders
// Components using only actions won't re-render when state changes
const DashboardStateContext = createContext<DashboardState | null>(null);
const DashboardActionsContext = createContext<DashboardActions | null>(null);

// Legacy combined context (for backward compatibility)
const DashboardContext = createContext<DashboardContextValue | null>(null);

// Provider props
export interface DashboardProviderProps {
  children: React.ReactNode;
  brandId: string;
  initialSessionId?: string;
  brandsLoading?: boolean;
}

/**
 * DashboardProvider
 * 
 * Provides dashboard state and actions to all child components.
 * Manages real-time job updates, session history, and user interactions.
 * 
 * @example
 * ```tsx
 * <DashboardProvider brandId="brand-123">
 *   <Dashboard />
 * </DashboardProvider>
 * ```
 */
export function DashboardProvider({
  children,
  brandId,
  initialSessionId,
  brandsLoading: _brandsLoading = false,
}: DashboardProviderProps) {
  // Local state
  const [jobId, setJobId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<Error | null>(null);
  const [lastPrompt, setLastPrompt] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Use custom hooks for job status and session history
  const {
    status: jobStatus,
    error: jobError,
    isPolling,
    connectionStatus: realtimeConnectionStatus,
    isTimedOut,
    refetch: refetchJobStatus,
  } = useJobStatus(jobId);

  const {
    versions,
    currentIndex: currentVersionIndex,
    currentVersion,
    loadVersion: loadVersionFromHistory,
    addVersion,
  } = useSessionHistory(sessionId);

  // Derive connection status from realtime status and polling state
  const connectionStatus: 'connected' | 'disconnected' | 'connecting' = useMemo(() => {
    // If no active job, show as connected (app is ready/idle)
    if (!jobId) return 'connected';
    // If realtime is connected, we're connected
    if (realtimeConnectionStatus === 'connected') return 'connected';
    // If realtime is connecting, show connecting
    if (realtimeConnectionStatus === 'connecting') return 'connecting';
    // If polling is active, show as connecting (degraded mode)
    if (isPolling) return 'connecting';
    // Otherwise disconnected (realtime failed and no polling)
    return 'disconnected';
  }, [realtimeConnectionStatus, isPolling, jobId]);

  // Update error state when job error occurs or times out
  useEffect(() => {
    if (jobError) {
      setError(jobError);
      setIsSubmitting(false);
      
      // Add timeout error message to chat if it's a timeout
      if (isTimedOut) {
        const errorMessage: ChatMessage = {
          role: 'error',
          content: 'Image generation timed out after 3 minutes. This usually happens when the AI image generation service is overloaded or experiencing issues. Please try again with a simpler prompt or wait a few minutes.',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    }
  }, [jobError, isTimedOut]);

  // Clear isSubmitting when job status is received (polling has started)
  useEffect(() => {
    if (jobStatus?.status) {
      setIsSubmitting(false);
    }
  }, [jobStatus?.status]);

  // Determine if user is viewing a historical version or the latest
  // If currentVersionIndex points to the last version, show live jobStatus data
  // Otherwise, show the selected version's data
  const isViewingLatest = versions.length === 0 || currentVersionIndex === versions.length - 1;
  
  // Extract data - use selected version when viewing history, jobStatus when viewing latest
  const currentImageUrl = isViewingLatest 
    ? jobStatus?.current_image_url 
    : currentVersion?.image_url;
  
  const complianceScore = isViewingLatest 
    ? jobStatus?.compliance_score 
    : currentVersion?.score;
  
  const violations = isViewingLatest 
    ? (jobStatus?.violations || [])
    : (currentVersion?.violations || []);
  
  const twinData = jobStatus?.twin_data; // Twin data is always from latest job

  // Action: Submit a new prompt
  const submitPrompt = useCallback(async (prompt: string) => {
    try {
      setError(null);
      setLastPrompt(prompt);
      setIsSubmitting(true); // Set immediately for instant UI feedback

      // Optimistically add user message to chat
      const userMessage: ChatMessage = {
        role: 'user',
        content: prompt,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, userMessage]);

      // Prepare generation request
      const request: GenerateRequest = {
        brand_id: brandId,
        prompt,
        async_mode: true, // Always use async mode for real-time updates
      };

      // Include session_id and previous_image_url for multi-turn generation
      // This enables the backend to use the previous image as context
      if (sessionId) {
        request.session_id = sessionId;
      }
      
      // Pass the current image URL for multi-turn context
      // This is critical for "fix the errors" type prompts
      if (currentImageUrl) {
        request.previous_image_url = currentImageUrl;
        console.log('Multi-turn generation with previous image:', currentImageUrl);
      }

      // Call generation API with retry logic for critical operations
      const response = await apiClient.post<GenerateResponse>('/generate', request, RETRY_CONFIGS.CRITICAL);

      // Update job and session IDs
      setJobId(response.job_id);
      
      // Note: Status will be updated automatically by useJobStatus hook polling
      // The hook will fetch the job status and update it
      
      // If this is the first generation in a session, store the session ID
      // (In a real implementation, the backend would return session_id)
      if (!sessionId) {
        // Generate a session ID or get it from response
        const newSessionId = response.job_id; // Simplified: use job_id as session_id
        setSessionId(newSessionId);
      }

      // Add user-friendly system acknowledgment message
      const systemMessage: ChatMessage = {
        role: 'system',
        content: currentImageUrl 
          ? 'Refining previous image...' 
          : 'Starting generation...',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, systemMessage]);

    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Failed to submit prompt');
      setError(errorObj);
      setIsSubmitting(false); // Clear submitting state on error
      console.error('Error submitting prompt:', errorObj);

      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: 'error',
        content: `Generation failed: ${errorObj.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      
      // Log detailed error for debugging (Requirements 13.8)
      console.error('Detailed error submitting prompt:', {
        error: errorObj,
        brandId,
        sessionId,
        currentImageUrl,
        prompt,
        timestamp: new Date().toISOString(),
        stack: errorObj.stack,
      });
    }
  }, [brandId, sessionId, currentImageUrl]);

  // Action: Load a specific version from history
  const loadVersion = useCallback((index: number) => {
    loadVersionFromHistory(index);
    
    // Optionally add a system message about loading the version
    const version = versions[index];
    if (version) {
      const systemMessage: ChatMessage = {
        role: 'system',
        content: `Loaded version ${index + 1} (Score: ${version.score}%)`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, systemMessage]);
    }
  }, [loadVersionFromHistory, versions]);

  // Action: Ship It - User approves the image based on their aesthetic judgment
  // This respects the user's creative vision regardless of compliance score
  const acceptCorrection = useCallback(async () => {
    if (!jobId) {
      console.warn('No active job to ship');
      return;
    }

    try {
      setError(null);

      // First, call review API with "approve" decision to ship the current image
      // This marks the job as complete, respecting the user's aesthetic judgment
      await apiClient.post(`/jobs/${jobId}/review`, { 
        decision: 'approve' 
      }, RETRY_CONFIGS.STANDARD);

      // Then save to asset library for future reference
      try {
        await apiClient.post(`/jobs/${jobId}/save-asset`, {}, RETRY_CONFIGS.STANDARD);
      } catch (saveError) {
        // Don't fail the whole operation if asset save fails
        console.warn('Failed to save asset to library:', saveError);
      }

      // Add system message with positive, confident tone
      const systemMessage: ChatMessage = {
        role: 'system',
        content: 'Perfect! Your image has been shipped and saved to your asset library.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, systemMessage]);

    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Failed to ship image');
      setError(errorObj);
      console.error('Error shipping image:', errorObj);
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: 'error',
        content: `Failed to ship: ${errorObj.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  }, [jobId]);

  // Action: Request a tweak to fix violations or edit the existing image
  // Uses the appropriate endpoint based on job status to preserve image context
  const requestTweak = useCallback(async (instruction: string) => {
    if (!jobId) {
      console.warn('No active job to tweak');
      // Fall back to regular prompt submission if no active job
      await submitPrompt(instruction);
      return;
    }

    const currentStatus = jobStatus?.status;
    
    // Use tweak endpoints for both needs_review and completed jobs
    // This preserves the previous image context for multi-turn editing
    if (currentStatus === 'needs_review' || currentStatus === 'completed') {
      try {
        setError(null);
        setIsSubmitting(true);

        // Add user message to chat
        const userMessage: ChatMessage = {
          role: 'user',
          content: instruction,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMessage]);

        if (currentStatus === 'needs_review') {
          // Call review API with "tweak" decision for needs_review jobs
          await apiClient.post(`/jobs/${jobId}/review`, { 
            decision: 'tweak',
            tweak_instruction: instruction,
          }, RETRY_CONFIGS.STANDARD);
        } else {
          // Call tweak endpoint for completed jobs
          // This endpoint is specifically designed for multi-turn refinement
          await apiClient.post(`/jobs/${jobId}/tweak`, { 
            tweak_instruction: instruction,
          }, RETRY_CONFIGS.STANDARD);
        }

        // Add system message
        const systemMessage: ChatMessage = {
          role: 'system',
          content: 'Applying changes to the current image...',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, systemMessage]);
        
        // Trigger a refetch to restart polling for the updated job status
        // The job is now back in 'processing' state and needs to be tracked
        setTimeout(() => {
          refetchJobStatus();
        }, 1000); // Small delay to let backend update job status

      } catch (err) {
        const errorObj = err instanceof Error ? err : new Error('Failed to apply tweak');
        setError(errorObj);
        setIsSubmitting(false);
        console.error('Error applying tweak:', errorObj);
        
        // Add error message to chat
        const errorMessage: ChatMessage = {
          role: 'error',
          content: `Failed to apply changes: ${errorObj.message}`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } else {
      // Job is in another status (e.g., generating, failed), submit as regular prompt
      await submitPrompt(instruction);
    }
  }, [jobId, jobStatus?.status, submitPrompt]);

  // Action: Retry failed generation
  const retryGeneration = useCallback(async () => {
    if (!lastPrompt) {
      console.warn('No prompt to retry');
      return;
    }

    // Simply resubmit the last prompt
    await submitPrompt(lastPrompt);
  }, [lastPrompt, submitPrompt]);

  // Action: Clear error state
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Action: Start a new session (clear current context for fresh generation)
  const startNewSession = useCallback(() => {
    setJobId(null);
    setSessionId(null);
    setError(null);
    setLastPrompt('');
    setIsSubmitting(false);
    
    // Add system message indicating new session
    const systemMessage: ChatMessage = {
      role: 'system',
      content: 'Started new session. Ready for a fresh generation.',
      timestamp: new Date(),
    };
    setMessages([systemMessage]); // Clear chat history and add new session message
  }, []);

  // When job completes or needs review, add version to history
  // This ensures thumbnails are saved even for low-scoring images
  useEffect(() => {
    const isFinished = jobStatus?.status === 'completed' || jobStatus?.status === 'needs_review';
    
    if (isFinished && jobStatus?.current_image_url) {
      // Check if this version is already in history
      const alreadyExists = versions.some(v => v.image_url === jobStatus.current_image_url);
      
      if (!alreadyExists) {
        const newVersion: Version = {
          attempt_id: versions.length + 1,
          image_url: jobStatus.current_image_url,
          thumb_url: jobStatus.current_image_url, // Use same URL for now
          score: jobStatus.compliance_score || 0,
          timestamp: jobStatus.updated_at,
          prompt: jobStatus.prompt,
          violations: jobStatus.violations || [], // Store violations with the version
        };
        
        addVersion(newVersion);
        console.log('Added version to history:', newVersion);

        // Add completion message to chat
        const statusText = jobStatus.status === 'needs_review' 
          ? 'Generation complete - needs review' 
          : 'Generation complete!';
        const systemMessage: ChatMessage = {
          role: 'system',
          content: `${statusText} Compliance score: ${jobStatus.compliance_score}%`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, systemMessage]);
      }
    }
  }, [jobStatus, versions, addVersion]);

  // Memoize state object to prevent unnecessary re-renders
  const stateValue: DashboardState = useMemo(() => ({
    jobId,
    sessionId,
    brandId,
    status: jobStatus,
    isPolling,
    isSubmitting,
    isTimedOut,
    currentImageUrl,
    complianceScore,
    violations,
    twinData,
    versions,
    currentVersionIndex,
    currentVersion,
    messages,
    connectionStatus,
    error,
  }), [
    jobId, sessionId, brandId, jobStatus, isPolling, isSubmitting, isTimedOut,
    currentImageUrl, complianceScore, violations, twinData, versions,
    currentVersionIndex, currentVersion, messages, connectionStatus, error
  ]);

  // Memoize actions object - these callbacks are already memoized with useCallback,
  // but we need to memoize the object itself to prevent re-renders
  const actionsValue: DashboardActions = useMemo(() => ({
    submitPrompt,
    loadVersion,
    acceptCorrection,
    requestTweak,
    retryGeneration,
    clearError,
    startNewSession,
  }), [submitPrompt, loadVersion, acceptCorrection, requestTweak, retryGeneration, clearError, startNewSession]);

  // Combined context value for backward compatibility
  const contextValue: DashboardContextValue = useMemo(() => ({
    ...stateValue,
    ...actionsValue,
  }), [stateValue, actionsValue]);

  return (
    <DashboardStateContext.Provider value={stateValue}>
      <DashboardActionsContext.Provider value={actionsValue}>
        <DashboardContext.Provider value={contextValue}>
          {children}
        </DashboardContext.Provider>
      </DashboardActionsContext.Provider>
    </DashboardStateContext.Provider>
  );
}

/**
 * useDashboard Hook
 * 
 * Access dashboard state and actions from any component.
 * Must be used within a DashboardProvider.
 * 
 * @throws Error if used outside DashboardProvider
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { status, submitPrompt, connectionStatus } = useDashboard();
 *   
 *   return (
 *     <div>
 *       <p>Status: {status?.status}</p>
 *       <p>Connection: {connectionStatus}</p>
 *       <button onClick={() => submitPrompt('Generate a logo')}>
 *         Generate
 *       </button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useDashboard(): DashboardContextValue {
  const context = useContext(DashboardContext);

  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }

  return context;
}

/**
 * useDashboardState Hook
 *
 * Access only dashboard state (no actions).
 * Use this when your component only needs to read state.
 * Components using this hook will re-render when state changes.
 *
 * @example
 * ```tsx
 * function StatusDisplay() {
 *   const { status, complianceScore } = useDashboardState();
 *   return <p>Score: {complianceScore}%</p>;
 * }
 * ```
 */
export function useDashboardState(): DashboardState {
  const context = useContext(DashboardStateContext);

  if (!context) {
    throw new Error('useDashboardState must be used within a DashboardProvider');
  }

  return context;
}

/**
 * useDashboardActions Hook
 *
 * Access only dashboard actions (no state).
 * Use this when your component only needs to trigger actions.
 * Components using this hook will NOT re-render when state changes,
 * making them more performant.
 *
 * @example
 * ```tsx
 * function SubmitButton() {
 *   const { submitPrompt } = useDashboardActions();
 *   return <button onClick={() => submitPrompt('Generate a logo')}>Submit</button>;
 * }
 * ```
 */
export function useDashboardActions(): DashboardActions {
  const context = useContext(DashboardActionsContext);

  if (!context) {
    throw new Error('useDashboardActions must be used within a DashboardProvider');
  }

  return context;
}

export default DashboardContext;
