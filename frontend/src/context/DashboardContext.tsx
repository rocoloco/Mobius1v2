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
  retryGeneration: () => Promise<void>;
  clearError: () => void;
}

// Combined context value
export interface DashboardContextValue extends DashboardState, DashboardActions {}

// Create context
const DashboardContext = createContext<DashboardContextValue | null>(null);

// Provider props
export interface DashboardProviderProps {
  children: React.ReactNode;
  brandId: string;
  initialSessionId?: string;
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
    // If realtime is connected, we're connected
    if (realtimeConnectionStatus === 'connected') return 'connected';
    // If realtime is connecting, show connecting
    if (realtimeConnectionStatus === 'connecting') return 'connecting';
    // If polling is active, show as connecting (degraded mode)
    if (isPolling && jobId) return 'connecting';
    // Otherwise disconnected
    return 'disconnected';
  }, [realtimeConnectionStatus, isPolling, jobId]);

  // Update error state when job error occurs
  useEffect(() => {
    if (jobError) {
      setError(jobError);
      setIsSubmitting(false);
    }
  }, [jobError]);

  // Clear isSubmitting when job status is received (polling has started)
  useEffect(() => {
    if (jobStatus?.status) {
      setIsSubmitting(false);
    }
  }, [jobStatus?.status]);

  // Extract data from job status
  const currentImageUrl = jobStatus?.current_image_url;
  const complianceScore = jobStatus?.compliance_score;
  const violations = jobStatus?.violations || [];
  const twinData = jobStatus?.twin_data;

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

  // Action: Accept auto-correction
  const acceptCorrection = useCallback(async () => {
    if (!jobId) {
      console.warn('No active job to accept correction for');
      return;
    }

    try {
      setError(null);

      // Call accept correction API with retry logic
      // Note: Adjust endpoint based on actual API
      await apiClient.post(`/jobs/${jobId}/accept`, {}, RETRY_CONFIGS.STANDARD);

      // Add system message
      const systemMessage: ChatMessage = {
        role: 'system',
        content: 'Auto-correction accepted. Generating corrected version...',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, systemMessage]);

    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Failed to accept correction');
      setError(errorObj);
      console.error('Error accepting correction:', errorObj);
    }
  }, [jobId]);

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

  // Combine state and actions
  const contextValue: DashboardContextValue = {
    // State
    jobId,
    sessionId,
    brandId,
    status: jobStatus,
    isPolling,
    isSubmitting,
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
    
    // Actions
    submitPrompt,
    loadVersion,
    acceptCorrection,
    retryGeneration,
    clearError,
  };

  return (
    <DashboardContext.Provider value={contextValue}>
      {children}
    </DashboardContext.Provider>
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

export default DashboardContext;
