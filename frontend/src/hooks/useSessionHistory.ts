/**
 * useSessionHistory Hook
 * 
 * Manages session version history for multi-turn generation workflows.
 * Fetches history from backend and provides navigation between versions.
 * 
 * Requirements: 10.1-10.7
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';
import type { Version, SessionHistoryResponse } from '../api/types';

interface UseSessionHistoryReturn {
  versions: Version[];
  currentIndex: number;
  currentVersion: Version | null;
  isLoading: boolean;
  error: Error | null;
  loadVersion: (index: number) => void;
  addVersion: (version: Version) => void;
  refetch: () => Promise<void>;
}

/**
 * Manage session version history for multi-turn generation
 * 
 * @param sessionId - The session ID to track (null to disable tracking)
 * @returns Object containing versions array, current index, navigation functions
 * 
 * @example
 * ```tsx
 * const { versions, currentIndex, currentVersion, loadVersion, addVersion } = 
 *   useSessionHistory(sessionId);
 * 
 * // Navigate to a specific version
 * <button onClick={() => loadVersion(0)}>Load First Version</button>
 * 
 * // Add a new version when generation completes
 * useEffect(() => {
 *   if (newImageUrl) {
 *     addVersion({
 *       attempt_id: versions.length + 1,
 *       image_url: newImageUrl,
 *       thumb_url: newThumbUrl,
 *       score: complianceScore,
 *       timestamp: new Date().toISOString(),
 *       prompt: lastPrompt,
 *     });
 *   }
 * }, [newImageUrl]);
 * ```
 */
export function useSessionHistory(sessionId: string | null): UseSessionHistoryReturn {
  const [versions, setVersions] = useState<Version[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Fetch session history from backend
  const fetchHistory = useCallback(async () => {
    if (!sessionId) {
      setVersions([]);
      setCurrentIndex(0);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<SessionHistoryResponse>(
        `/sessions/${sessionId}/history`
      );
      
      setVersions(response.versions);
      
      // Set current index to the latest version (last in array)
      if (response.versions.length > 0) {
        setCurrentIndex(response.versions.length - 1);
      } else {
        setCurrentIndex(0);
      }
    } catch (err) {
      const errorObj = err instanceof Error 
        ? err 
        : new Error('Failed to fetch session history');
      setError(errorObj);
      console.error('Error fetching session history:', errorObj);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  // Fetch history when sessionId changes
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // Load a specific version by index
  const loadVersion = useCallback((index: number) => {
    if (index < 0 || index >= versions.length) {
      console.warn(`Invalid version index: ${index}. Valid range: 0-${versions.length - 1}`);
      return;
    }
    
    setCurrentIndex(index);
    console.log(`Loaded version ${index + 1} of ${versions.length}`);
  }, [versions.length]);

  // Add a new version to the history
  const addVersion = useCallback((version: Version) => {
    setVersions(prev => {
      const newVersions = [...prev, version];
      // Automatically navigate to the new version
      setCurrentIndex(newVersions.length - 1);
      return newVersions;
    });
    
    console.log(`Added new version (attempt ${version.attempt_id})`);
  }, []);

  // Get the current version object
  const currentVersion = versions.length > 0 && currentIndex >= 0 && currentIndex < versions.length
    ? versions[currentIndex]
    : null;

  return {
    versions,
    currentIndex,
    currentVersion,
    isLoading,
    error,
    loadVersion,
    addVersion,
    refetch: fetchHistory,
  };
}

export default useSessionHistory;
