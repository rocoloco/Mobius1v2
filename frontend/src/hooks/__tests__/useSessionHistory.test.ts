/**
 * Tests for useSessionHistory hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useSessionHistory } from '../useSessionHistory';
import type { Version, SessionHistoryResponse } from '../../api/types';

// Mock API client
vi.mock('../../api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('useSessionHistory', () => {
  const mockVersions: Version[] = [
    {
      attempt_id: 1,
      image_url: 'https://example.com/image1.png',
      thumb_url: 'https://example.com/thumb1.png',
      score: 85,
      timestamp: '2024-01-01T00:00:00Z',
      prompt: 'First prompt',
    },
    {
      attempt_id: 2,
      image_url: 'https://example.com/image2.png',
      thumb_url: 'https://example.com/thumb2.png',
      score: 92,
      timestamp: '2024-01-01T00:01:00Z',
      prompt: 'Second prompt',
    },
  ];

  const mockResponse: SessionHistoryResponse = {
    session_id: 'session-123',
    versions: mockVersions,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return empty versions when sessionId is null', () => {
    const { result } = renderHook(() => useSessionHistory(null));

    expect(result.current.versions).toEqual([]);
    expect(result.current.currentIndex).toBe(0);
    expect(result.current.currentVersion).toBeNull();
  });

  it('should fetch session history on mount', async () => {
    const { apiClient } = await import('../../api/client');
    vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useSessionHistory('session-123'));

    await waitFor(() => {
      expect(result.current.versions).toEqual(mockVersions);
      expect(result.current.currentIndex).toBe(1); // Should be at latest version
      expect(result.current.currentVersion).toEqual(mockVersions[1]);
    });
  });

  it('should load a specific version', async () => {
    const { apiClient } = await import('../../api/client');
    vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useSessionHistory('session-123'));

    await waitFor(() => {
      expect(result.current.versions.length).toBe(2);
    });

    act(() => {
      result.current.loadVersion(0);
    });

    expect(result.current.currentIndex).toBe(0);
    expect(result.current.currentVersion).toEqual(mockVersions[0]);
  });

  it('should add a new version', async () => {
    const { apiClient } = await import('../../api/client');
    vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useSessionHistory('session-123'));

    await waitFor(() => {
      expect(result.current.versions.length).toBe(2);
    });

    const newVersion: Version = {
      attempt_id: 3,
      image_url: 'https://example.com/image3.png',
      thumb_url: 'https://example.com/thumb3.png',
      score: 95,
      timestamp: '2024-01-01T00:02:00Z',
      prompt: 'Third prompt',
    };

    act(() => {
      result.current.addVersion(newVersion);
    });

    expect(result.current.versions.length).toBe(3);
    expect(result.current.currentIndex).toBe(2); // Should auto-navigate to new version
    expect(result.current.currentVersion).toEqual(newVersion);
  });

  it('should handle fetch errors', async () => {
    const { apiClient } = await import('../../api/client');
    const mockError = new Error('Failed to fetch history');
    vi.mocked(apiClient.get).mockRejectedValue(mockError);

    const { result } = renderHook(() => useSessionHistory('session-123'));

    await waitFor(() => {
      expect(result.current.error).toEqual(mockError);
    });
  });

  it('should not load invalid version index', async () => {
    const { apiClient } = await import('../../api/client');
    vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useSessionHistory('session-123'));

    await waitFor(() => {
      expect(result.current.versions.length).toBe(2);
    });

    const initialIndex = result.current.currentIndex;

    act(() => {
      result.current.loadVersion(999); // Invalid index
    });

    // Index should not change
    expect(result.current.currentIndex).toBe(initialIndex);
  });
});
