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
  refetch: () => Promise<void>;
}

const POLLING_INTERVAL_MS = 3000; // 3 seconds for faster feedback
const REALTIME_FALLBACK_DELAY_MS = 5000; // Wait 5s before falling back to polling

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
  
  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const fallbackTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastRealtimeUpdateRef = useRef<number>(0);

  // Check if job is in terminal state
  const isTerminalState = useCallback((jobStatus: JobStatusResponse | null) => {
    if (!jobStatus) return false;
    return ['completed', 'failed', 'cancelled', 'needs_review'].includes(jobStatus.status);
  }, []);

  // Fetch job status from API
  const fetchJobStatus = useCallback(async () => {
    if (!jobId) return;

    try {
      const response = await apiClient.get<JobStatusResponse>(`/jobs/${jobId}`, RETRY_CONFIGS.FAST);
      setStatus(response);
      setError(null);
      
      // Stop polling if we reached terminal state
      if (isTerminalState(response) && pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
        setIsPolling(false);
      }
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Failed to fetch job status');
      setError(errorObj);
      console.error('Error fetching job status:', errorObj);
    }
  }, [jobId, isTerminalState]);

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
    } else {
      setStatus(null);
      setError(null);
      setIsPolling(false);
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

  // Set up polling when needed
  useEffect(() => {
    // Only poll if we have a job, polling is enabled, and job is not terminal
    const shouldPoll = jobId && isPolling && !isTerminalState(status);

    if (shouldPoll) {
      // Clear any existing interval
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      // Start polling
      pollingIntervalRef.current = setInterval(fetchJobStatus, POLLING_INTERVAL_MS);
      console.log(`Started polling for job ${jobId} (interval: ${POLLING_INTERVAL_MS}ms)`);
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [jobId, isPolling, status, fetchJobStatus, isTerminalState]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      if (fallbackTimeoutRef.current) {
        clearTimeout(fallbackTimeoutRef.current);
      }
    };
  }, []);

  return {
    status,
    error,
    isPolling,
    connectionStatus: realtimeConnectionStatus,
    refetch: fetchJobStatus,
  };
}

export default useJobStatus;
