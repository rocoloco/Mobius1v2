/**
 * useJobStatus Hook
 * 
 * Manages job status tracking with Supabase Realtime and polling fallback.
 * Automatically falls back to polling if Realtime connection fails.
 * 
 * Requirements: 9.1-9.10
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useSupabaseRealtime } from './useSupabaseRealtime';
import { apiClient } from '../api/client';
import { RETRY_CONFIGS } from '../utils/retry';
import type { JobStatusResponse } from '../api/types';

interface UseJobStatusReturn {
  status: JobStatusResponse | null;
  error: Error | null;
  isPolling: boolean;
  refetch: () => Promise<void>;
}

const POLLING_INTERVAL_MS = 5000; // 5 seconds
const REALTIME_TIMEOUT_MS = 10000; // 10 seconds to detect if realtime is working

/**
 * Track job status with real-time updates and polling fallback
 * 
 * @param jobId - The job ID to track (null to disable tracking)
 * @returns Object containing status, error, isPolling flag, and refetch function
 * 
 * @example
 * ```tsx
 * const { status, error, isPolling, refetch } = useJobStatus(currentJobId);
 * 
 * if (error) {
 *   return <div>Error: {error.message}</div>;
 * }
 * 
 * if (!status) {
 *   return <div>Loading...</div>;
 * }
 * 
 * return (
 *   <div>
 *     Job Status: {status.status}
 *     {isPolling && <span>(Polling mode)</span>}
 *   </div>
 * );
 * ```
 */
export function useJobStatus(jobId: string | null): UseJobStatusReturn {
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [realtimeWorking, setRealtimeWorking] = useState(true);
  
  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const realtimeTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastUpdateTimeRef = useRef<number>(Date.now());

  // Fetch job status from API
  const fetchJobStatus = useCallback(async () => {
    if (!jobId) return;

    try {
      // Use fast retry config for status polling to fail quickly
      const response = await apiClient.get<JobStatusResponse>(`/jobs/${jobId}`, RETRY_CONFIGS.FAST);
      setStatus(response);
      setError(null);
      lastUpdateTimeRef.current = Date.now();
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Failed to fetch job status');
      setError(errorObj);
      console.error('Error fetching job status:', errorObj);
    }
  }, [jobId]);

  // Handle realtime updates
  const handleRealtimeUpdate = useCallback((update: JobStatusResponse) => {
    setStatus(update);
    setError(null);
    setRealtimeWorking(true);
    lastUpdateTimeRef.current = Date.now();
    
    // If we were polling, we can stop now
    if (isPolling) {
      setIsPolling(false);
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }
  }, [isPolling]);

  // Handle realtime errors
  const handleRealtimeError = useCallback((err: Error) => {
    console.error('Realtime error, falling back to polling:', err);
    setRealtimeWorking(false);
    setIsPolling(true);
  }, []);

  // Subscribe to realtime updates
  useSupabaseRealtime({
    jobId,
    onUpdate: handleRealtimeUpdate,
    onError: handleRealtimeError,
  });

  // Initial fetch when jobId changes
  useEffect(() => {
    if (jobId) {
      fetchJobStatus();
    } else {
      setStatus(null);
      setError(null);
      setIsPolling(false);
    }
  }, [jobId, fetchJobStatus]);

  // Set up realtime timeout detector
  useEffect(() => {
    if (!jobId || !realtimeWorking) return;

    // Clear any existing timeout
    if (realtimeTimeoutRef.current) {
      clearTimeout(realtimeTimeoutRef.current);
    }

    // Set timeout to detect if realtime is not working
    realtimeTimeoutRef.current = setTimeout(() => {
      const timeSinceLastUpdate = Date.now() - lastUpdateTimeRef.current;
      
      // If we haven't received an update in a while and job is still active, fall back to polling
      if (timeSinceLastUpdate > REALTIME_TIMEOUT_MS && status && 
          !['completed', 'failed', 'cancelled'].includes(status.status)) {
        console.warn('No realtime updates received, falling back to polling');
        setRealtimeWorking(false);
        setIsPolling(true);
      }
    }, REALTIME_TIMEOUT_MS);

    return () => {
      if (realtimeTimeoutRef.current) {
        clearTimeout(realtimeTimeoutRef.current);
      }
    };
  }, [jobId, realtimeWorking, status]);

  // Set up polling fallback
  useEffect(() => {
    // Only poll if:
    // 1. We have a jobId
    // 2. Realtime is not working OR we're explicitly in polling mode
    // 3. Job is not in a terminal state
    const shouldPoll = jobId && 
                       (isPolling || !realtimeWorking) && 
                       status && 
                       !['completed', 'failed', 'cancelled'].includes(status.status);

    if (shouldPoll) {
      // Clear any existing interval
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      // Start polling
      pollingIntervalRef.current = setInterval(() => {
        fetchJobStatus();
      }, POLLING_INTERVAL_MS);

      console.log(`Started polling for job ${jobId} (interval: ${POLLING_INTERVAL_MS}ms)`);
    }

    // Cleanup
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [jobId, isPolling, realtimeWorking, status, fetchJobStatus]);

  return {
    status,
    error,
    isPolling: isPolling || !realtimeWorking,
    refetch: fetchJobStatus,
  };
}

export default useJobStatus;
