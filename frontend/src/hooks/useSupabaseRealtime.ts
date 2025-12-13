/**
 * useSupabaseRealtime Hook
 * 
 * Subscribes to Supabase Realtime updates for job status changes.
 * Automatically manages subscription lifecycle and cleanup.
 * 
 * Requirements: 9.1-9.10
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { RealtimeChannel } from '@supabase/supabase-js';
import { supabase, isSupabaseConfigured } from '../api/supabase';
import type { JobStatusResponse } from '../api/types';

export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting';

interface UseSupabaseRealtimeOptions {
  jobId: string | null;
  onUpdate: (update: JobStatusResponse) => void;
  onError?: (error: Error) => void;
  onConnectionChange?: (status: ConnectionStatus) => void;
}

interface UseSupabaseRealtimeReturn {
  isConnected: boolean;
  connectionStatus: ConnectionStatus;
}

/**
 * Subscribe to real-time job status updates via Supabase Realtime
 * 
 * Uses Postgres Changes to listen for UPDATE events on the jobs table.
 * Requires Supabase Realtime to be enabled for the jobs table in the dashboard.
 * 
 * @param options - Configuration object with jobId, onUpdate callback, and optional onError
 * @returns Object with connection status
 * 
 * @example
 * ```tsx
 * const { isConnected, connectionStatus } = useSupabaseRealtime({
 *   jobId: currentJobId,
 *   onUpdate: (update) => {
 *     setJobStatus(update);
 *   },
 *   onError: (error) => {
 *     console.error('Realtime error:', error);
 *   },
 *   onConnectionChange: (status) => {
 *     console.log('Connection status:', status);
 *   }
 * });
 * ```
 */
export function useSupabaseRealtime({
  jobId,
  onUpdate,
  onError,
  onConnectionChange,
}: UseSupabaseRealtimeOptions): UseSupabaseRealtimeReturn {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const channelRef = useRef<RealtimeChannel | null>(null);
  const onUpdateRef = useRef(onUpdate);
  const onErrorRef = useRef(onError);
  const onConnectionChangeRef = useRef(onConnectionChange);

  // Keep refs up to date
  useEffect(() => {
    onUpdateRef.current = onUpdate;
    onErrorRef.current = onError;
    onConnectionChangeRef.current = onConnectionChange;
  }, [onUpdate, onError, onConnectionChange]);

  // Update connection status and notify
  const updateConnectionStatus = useCallback((status: ConnectionStatus) => {
    setConnectionStatus(status);
    onConnectionChangeRef.current?.(status);
  }, []);

  useEffect(() => {
    // Don't subscribe if no jobId or Supabase not configured
    if (!jobId) {
      updateConnectionStatus('disconnected');
      return;
    }

    if (!isSupabaseConfigured) {
      console.warn('Supabase not configured, realtime updates unavailable');
      updateConnectionStatus('disconnected');
      onErrorRef.current?.(new Error('Supabase not configured'));
      return;
    }

    updateConnectionStatus('connecting');

    // Create channel for this specific job
    // Using postgres_changes to listen for row-level changes
    const channel = supabase
      .channel(`job-updates-${jobId}`)
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
            console.log('Realtime update received:', payload.new);
            
            // Map the database row to JobStatusResponse format
            const update = mapDatabaseRowToJobStatus(payload.new);
            onUpdateRef.current(update);
          } catch (error) {
            console.error('Error processing realtime update:', error);
            onErrorRef.current?.(error as Error);
          }
        }
      )
      .subscribe((status, err) => {
        console.log(`Realtime subscription status for job ${jobId}:`, status);
        
        if (status === 'SUBSCRIBED') {
          console.log(`✓ Subscribed to realtime updates for job: ${jobId}`);
          updateConnectionStatus('connected');
        } else if (status === 'CHANNEL_ERROR') {
          const error = new Error(`Realtime channel error: ${err?.message || 'Unknown error'}`);
          console.error(error);
          updateConnectionStatus('disconnected');
          onErrorRef.current?.(error);
        } else if (status === 'TIMED_OUT') {
          const error = new Error('Realtime subscription timed out');
          console.error(error);
          updateConnectionStatus('disconnected');
          onErrorRef.current?.(error);
        } else if (status === 'CLOSED') {
          console.log(`Realtime channel closed for job: ${jobId}`);
          updateConnectionStatus('disconnected');
        }
      });

    channelRef.current = channel;

    // Cleanup: unsubscribe when component unmounts or jobId changes
    return () => {
      if (channelRef.current) {
        console.log(`Unsubscribing from realtime updates for job: ${jobId}`);
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
    };
  }, [jobId, updateConnectionStatus]);

  return {
    isConnected: connectionStatus === 'connected',
    connectionStatus,
  };
}

/**
 * Map database row to JobStatusResponse format
 * Handles snake_case to camelCase conversion and JSON parsing
 */
function mapDatabaseRowToJobStatus(row: Record<string, unknown>): JobStatusResponse {
  // Parse the state JSON if it's a string
  let state: Record<string, unknown> = {};
  if (typeof row.state === 'string') {
    try {
      state = JSON.parse(row.state);
    } catch {
      state = {};
    }
  } else if (row.state && typeof row.state === 'object') {
    state = row.state as Record<string, unknown>;
  }

  return {
    job_id: row.job_id as string,
    brand_id: row.brand_id as string,
    prompt: (state.prompt as string) || '',
    status: row.status as JobStatusResponse['status'],
    progress: (row.progress as number) || 0,
    current_image_url: state.current_image_url as string | undefined,
    compliance_score: state.compliance_score as number | undefined,
    violations: (state.violations as JobStatusResponse['violations']) || [],
    twin_data: state.twin_data as JobStatusResponse['twin_data'],
    error: (state.error as string) || (row.error as string) || undefined,
    created_at: row.created_at as string,
    updated_at: row.updated_at as string,
  };
}

export default useSupabaseRealtime;
