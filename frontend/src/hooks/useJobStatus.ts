/**
 * useJobStatus Hook
 * 
 * Manages job status tracking with Supabase Realtime and polling fallback.
 * Automatically falls back to polling if Realtime connection fails.
 * 
 * Requirements: 9.1-9.10
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useSupabaseRealtime, type ConnectionStatus } from './useSupabaseRealtime';
import { apiClient } from '../api/client';
import { RETRY_CONFIGS } from '../utils/retry';
import type { JobStatusResponse } from '../api/types';

interface UseJobStatusReturn {
  status: JobStatusResponse | null;
  error: Error | null;
  isPolling: boolean;
  connectionStatus: ConnectionStatus;
  isTimedOut: boolean;
  refetch: () => Promise<void>;
}

// Adaptive polling intervals based on job status
const getPollingInterval = (status: string | undefined, attempt: number = 0): number => {
  if (!status) return 5000;
  
  // Faster polling for active generation states
  if (status === 'processing' || status === 'generating' || status === 'auditing') {
    return Math.min(2000 + (attempt * 300), 4000); // 2s → 4s adaptive
  }
  
  // Slower polling for other states
  return 5000;
};

const REALTIME_FALLBACK_DELAY_MS = 3000; // Reduced from 5s to 3s
const JOB_TIMEOUT_MS = 180000; // 3 minutes - if job is still pending after this, consider it stuck

/**
 * Track job status with real-time updates and polling fallback
 * 
 * Strategy:
 * 1. Subscribe to Supabase Realtime for instant updates
 * 2. Do an initial fetch to get current state
 * 3. If realtime fails or times out, fall back to polling
 * 4. Stop polling/realtime when job reaches terminal state
 * 
 * @param jobId - The job ID to track (null to disable tracking)
 * @returns Object containing status, error, isPolling flag, connectionStatus, and refetch function
 */
export function useJobStatus(jobId: string | null): UseJobStatusReturn {
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [realtimeConnectionStatus, setRealtimeConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [isTimedOut, setIsTimedOut] = useState(false);
  
  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const fallbackTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const jobTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastRealtimeUpdateRef = useRef<number>(0);
  const jobStartTimeRef = useRef<number>(0);
  const pollingAttemptRef = useRef<number>(0); // Track polling attempts for adaptive intervals

  // Check if job is in terminal state
  const isTerminalState = useCallback((jobStatus: JobStatusResponse | null) => {
    if (!jobStatus) return false;
    return ['completed', 'failed', 'cancelled', 'needs_review'].includes(jobStatus.status);
  }, []);

  // Fetch job status from API
  const fetchJobStatus = useCallback(async () => {
    if (!jobId) return;

    try {
      // Disable caching for job status - we need fresh data on every poll
      const response = await apiClient.get<JobStatusResponse>(`/jobs/${jobId}`, RETRY_CONFIGS.FAST, false);
      setStatus(response);
      setError(null);
      
      // Handle polling state based on job status
      if (isTerminalState(response)) {
        // Stop polling if we reached terminal state
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
          setIsPolling(false);
        }
      } else if (!isPolling) {
        // Restart polling if job is back in non-terminal state (e.g., after tweak)
        // This handles the case where a tweak moves the job from needs_review to processing
        console.log('Job back in non-terminal state, restarting polling');
        jobStartTimeRef.current = Date.now(); // Reset timeout tracking
        setIsTimedOut(false);
        setIsPolling(true);
      }
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Failed to fetch job status');
      setError(errorObj);
      console.error('Error fetching job status:', errorObj);
    }
  }, [jobId, isTerminalState, isPolling]);

  // Handle realtime updates
  const handleRealtimeUpdate = useCallback((update: JobStatusResponse) => {
    console.log('Realtime update received:', update.status, update.compliance_score);
    setStatus(update);
    setError(null);
    lastRealtimeUpdateRef.current = Date.now();
    
    // If we were polling, stop since realtime is working
    if (pollingIntervalRef.current) {
      console.log('Realtime working, stopping polling');
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
      setIsPolling(false);
    }
  }, []);

  // Handle realtime errors - fall back to polling
  const handleRealtimeError = useCallback((err: Error) => {
    console.warn('Realtime error, will fall back to polling:', err.message);
    // Don't immediately start polling - wait for the connection status change
  }, []);

  // Handle connection status changes
  const handleConnectionChange = useCallback((newStatus: ConnectionStatus) => {
    console.log('Realtime connection status:', newStatus);
    setRealtimeConnectionStatus(newStatus);
  }, []);

  // Subscribe to realtime updates
  const { connectionStatus } = useSupabaseRealtime({
    jobId,
    onUpdate: handleRealtimeUpdate,
    onError: handleRealtimeError,
    onConnectionChange: handleConnectionChange,
  });

  // Initial fetch when jobId changes
  useEffect(() => {
    if (jobId) {
      fetchJobStatus();
      lastRealtimeUpdateRef.current = 0; // Reset realtime tracking
      jobStartTimeRef.current = Date.now(); // Track when we started tracking this job
      setIsTimedOut(false); // Reset timeout state
    } else {
      setStatus(null);
      setError(null);
      setIsPolling(false);
      setIsTimedOut(false);
      jobStartTimeRef.current = 0;
    }
  }, [jobId, fetchJobStatus]);

  // Set up fallback to polling if realtime doesn't deliver updates
  useEffect(() => {
    if (!jobId || isTerminalState(status)) {
      // Clear fallback timeout if job is done
      if (fallbackTimeoutRef.current) {
        clearTimeout(fallbackTimeoutRef.current);
        fallbackTimeoutRef.current = null;
      }
      return;
    }

    // If realtime is connected but we haven't received updates, set up fallback
    if (connectionStatus === 'connected' && !isPolling) {
      fallbackTimeoutRef.current = setTimeout(() => {
        // Check if we've received any realtime updates
        if (lastRealtimeUpdateRef.current === 0) {
          console.warn('No realtime updates received after connection, falling back to polling');
          setIsPolling(true);
        }
      }, REALTIME_FALLBACK_DELAY_MS);
    }

    // If realtime disconnected or failed, start polling immediately
    if (connectionStatus === 'disconnected' && status && !isTerminalState(status)) {
      console.log('Realtime disconnected, starting polling');
      setIsPolling(true);
    }

    return () => {
      if (fallbackTimeoutRef.current) {
        clearTimeout(fallbackTimeoutRef.current);
        fallbackTimeoutRef.current = null;
      }
    };
  }, [jobId, connectionStatus, status, isPolling, isTerminalState]);

  // Set up adaptive polling when needed
  useEffect(() => {
    // Only poll if we have a job, polling is enabled, and job is not terminal
    const shouldPoll = jobId && isPolling && !isTerminalState(status);

    if (shouldPoll) {
      // Clear any existing interval
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      // Reset polling attempt counter when starting new polling session
      pollingAttemptRef.current = 0;

      // Start adaptive polling
      const startAdaptivePolling = () => {
        const interval = getPollingInterval(status?.status, pollingAttemptRef.current);
        pollingIntervalRef.current = setTimeout(async () => {
          await fetchJobStatus();
          pollingAttemptRef.current += 1;
          
          // Continue polling if still needed
          if (jobId && isPolling && !isTerminalState(status)) {
            startAdaptivePolling();
          }
        }, interval);
        
        console.log(`Started adaptive polling for job ${jobId} (interval: ${interval}ms, attempt: ${pollingAttemptRef.current})`);
      };

      startAdaptivePolling();
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearTimeout(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [jobId, isPolling, status, fetchJobStatus, isTerminalState]);

  // Job timeout detection - mark as timed out if stuck in pending state
  useEffect(() => {
    // Clear any existing timeout
    if (jobTimeoutRef.current) {
      clearTimeout(jobTimeoutRef.current);
      jobTimeoutRef.current = null;
    }

    // Only set timeout if we have a job that's not in terminal state
    if (!jobId || isTerminalState(status) || isTimedOut) {
      return;
    }

    // Check if job is stuck in processing state (common when backend crashes)
    if (status && (status.status === 'processing' || status.status === 'generating')) {
      const elapsed = Date.now() - jobStartTimeRef.current;
      if (elapsed > JOB_TIMEOUT_MS) {
        console.warn(`Job ${jobId} stuck in ${status.status} state for ${elapsed / 1000}s`);
        setIsTimedOut(true);
        setError(new Error(`Job stuck in ${status.status} state. The backend may have crashed during image generation. Please try again.`));
        
        // Stop polling
        if (pollingIntervalRef.current) {
          clearTimeout(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
          setIsPolling(false);
        }
        return;
      }
    }

    // Calculate remaining time until timeout
    const elapsed = Date.now() - jobStartTimeRef.current;
    const remaining = Math.max(0, JOB_TIMEOUT_MS - elapsed);

    if (remaining === 0) {
      // Already timed out
      console.warn(`Job ${jobId} timed out after ${JOB_TIMEOUT_MS / 1000}s in pending state`);
      setIsTimedOut(true);
      setError(new Error('Job timed out. The backend may have crashed. Please try again.'));
      
      // Stop polling
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
        setIsPolling(false);
      }
    } else {
      // Set timeout for remaining time
      jobTimeoutRef.current = setTimeout(() => {
        // Double-check we're still in a non-terminal state
        if (status && !isTerminalState(status)) {
          console.warn(`Job ${jobId} timed out after ${JOB_TIMEOUT_MS / 1000}s in ${status.status} state`);
          setIsTimedOut(true);
          setError(new Error(`Job timed out after ${JOB_TIMEOUT_MS / 1000} seconds. This usually indicates a backend issue with image generation. Please try again.`));
          
          // Stop polling
          if (pollingIntervalRef.current) {
            clearTimeout(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
            setIsPolling(false);
          }
        }
      }, remaining);
    }

    return () => {
      if (jobTimeoutRef.current) {
        clearTimeout(jobTimeoutRef.current);
        jobTimeoutRef.current = null;
      }
    };
  }, [jobId, status, isTimedOut, isTerminalState]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearTimeout(pollingIntervalRef.current);
      }
      if (fallbackTimeoutRef.current) {
        clearTimeout(fallbackTimeoutRef.current);
      }
      if (jobTimeoutRef.current) {
        clearTimeout(jobTimeoutRef.current);
      }
    };
  }, []);

  return {
    status,
    error,
    isPolling,
    connectionStatus: realtimeConnectionStatus,
    isTimedOut,
    refetch: fetchJobStatus,
  };
}

export default useJobStatus;
