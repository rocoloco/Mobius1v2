/**
 * Tests for useJobStatus hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useJobStatus } from '../useJobStatus';
import type { JobStatusResponse } from '../../api/types';

// Mock dependencies
vi.mock('../useSupabaseRealtime', () => ({
  useSupabaseRealtime: vi.fn(),
}));

vi.mock('../../api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('useJobStatus', () => {
  const mockJobStatus: JobStatusResponse = {
    job_id: 'test-job-123',
    brand_id: 'brand-123',
    prompt: 'test prompt',
    status: 'generating',
    progress: 50,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return null status when jobId is null', () => {
    const { result } = renderHook(() => useJobStatus(null));

    expect(result.current.status).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.isPolling).toBe(false);
  });

  it('should fetch job status on mount', async () => {
    const { apiClient } = await import('../../api/client');
    vi.mocked(apiClient.get).mockResolvedValue(mockJobStatus);

    const { result } = renderHook(() => useJobStatus('test-job-123'));

    await waitFor(() => {
      expect(result.current.status).toEqual(mockJobStatus);
    });
  });

  it('should handle fetch errors', async () => {
    const { apiClient } = await import('../../api/client');
    const mockError = new Error('Failed to fetch');
    vi.mocked(apiClient.get).mockRejectedValue(mockError);

    const { result } = renderHook(() => useJobStatus('test-job-123'));

    await waitFor(() => {
      expect(result.current.error).toEqual(mockError);
    });
  });

  it('should provide refetch function', () => {
    const { result } = renderHook(() => useJobStatus('test-job-123'));

    expect(typeof result.current.refetch).toBe('function');
  });
});
