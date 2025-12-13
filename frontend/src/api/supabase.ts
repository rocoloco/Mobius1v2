/**
 * Supabase Client Configuration
 * Used for real-time subscriptions to job status updates
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Flag to track if Supabase is configured
export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

if (!isSupabaseConfigured) {
  console.warn('Supabase credentials not configured. Real-time updates will not be available.');
}

// Create a mock client that does nothing when Supabase is not configured
const createMockClient = (): SupabaseClient => {
  const mockChannel = {
    on: () => mockChannel,
    subscribe: () => mockChannel,
    unsubscribe: () => Promise.resolve(),
  };
  
  return {
    channel: () => mockChannel,
    removeChannel: () => Promise.resolve(),
    // Add other methods as needed, returning safe defaults
  } as unknown as SupabaseClient;
};

// Only create real client if credentials are configured
export const supabase: SupabaseClient = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey, {
      realtime: {
        params: {
          eventsPerSecond: 10,
        },
      },
    })
  : createMockClient();

export default supabase;
