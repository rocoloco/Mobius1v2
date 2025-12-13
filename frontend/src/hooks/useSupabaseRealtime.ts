/**
 * useSupabaseRealtime Hook
 * 
 * Subscribes to Supabase Realtime updates for job status changes.
 * Automatically manages subscription lifecycle and cleanup.
 * 
 * Requirements: 9.1-9.10
 */

import { useEffect, useRef } from 'react';
import { RealtimeChannel } from '@supabase/supabase-js';
import { supabase } from '../api/supabase';
import type { JobStatusResponse } from '../api/types';

interface UseSupabaseRealtimeOptions {
  jobId: string | null;
  onUpdate: (update: JobStatusResponse) => void;
  onError?: (error: Error) => void;
}

/**
 * Subscribe to real-time job status updates via Supabase Realtime
 * 
 * @param options - Configuration object with jobId, onUpdate callback, and optional onError
 * @returns void
 * 
 * @example
 * ```tsx
 * useSupabaseRealtime({
 *   jobId: currentJobId,
 *   onUpdate: (update) => {
 *     setJobStatus(update);
 *   },
 *   onError: (error) => {
 *     console.error('Realtime error:', error);
 *   }
 * });
 * ```
 */
export function useSupabaseRealtime({
  jobId,
  onUpdate,
  onError,
}: UseSupabaseRealtimeOptions): void {
  const channelRef = useRef<RealtimeChannel | null>(null);
  const onUpdateRef = useRef(onUpdate);
  const onErrorRef = useRef(onError);

  // Keep refs up to date
  useEffect(() => {
    onUpdateRef.current = onUpdate;
    onErrorRef.current = onError;
  }, [onUpdate, onError]);

  useEffect(() => {
    // Don't subscribe if no jobId
    if (!jobId) {
      return;
    }

    // Create channel for this specific job
    const channel = supabase
      .channel(`job:${jobId}`)
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'jobs',
          filter: `job_id=eq.${jobId}`,
        },
        (payload) => {
          try {
            // Call the update callback with the new job data
            onUpdateRef.current(payload.new as JobStatusResponse);
          } catch (error) {
            console.error('Error processing realtime update:', error);
            onErrorRef.current?.(error as Error);
          }
        }
      )
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Subscribed to job updates: ${jobId}`);
        } else if (status === 'CHANNEL_ERROR') {
          const error = new Error('Failed to subscribe to realtime updates');
          console.error(error);
          onErrorRef.current?.(error);
        } else if (status === 'TIMED_OUT') {
          const error = new Error('Realtime subscription timed out');
          console.error(error);
          onErrorRef.current?.(error);
        }
      });

    channelRef.current = channel;

    // Cleanup: unsubscribe when component unmounts or jobId changes
    return () => {
      if (channelRef.current) {
        console.log(`Unsubscribing from job updates: ${jobId}`);
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
    };
  }, [jobId]);
}

export default useSupabaseRealtime;
