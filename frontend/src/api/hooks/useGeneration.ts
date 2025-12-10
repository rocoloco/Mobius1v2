import { useState, useCallback, useEffect, useRef } from 'react';
import { apiClient } from '../client';
import type { GenerateRequest, GenerateResponse, JobStatusResponse, TweakRequest } from '../types';

/**
 * Hook to manage asset generation and job polling
 */
export const useGeneration = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentJob, setCurrentJob] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollingIntervalRef = useRef<number | null>(null);

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const startPolling = useCallback((jobId: string) => {
    // Clear any existing polling
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    const pollJob = async () => {
      try {
        const jobStatus = await apiClient.get<JobStatusResponse>(`/jobs/${jobId}`);
        setCurrentJob(jobStatus);

        // Stop polling on terminal states
        if (
          jobStatus.status === 'completed' ||
          jobStatus.status === 'failed' ||
          jobStatus.status === 'needs_review' ||
          jobStatus.status === 'cancelled'
        ) {
          setIsGenerating(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        }
      } catch (err) {
        console.error('Error polling job:', err);
        setError(err instanceof Error ? err.message : 'Failed to poll job');
        setIsGenerating(false);
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      }
    };

    // Poll immediately, then every 3 seconds
    pollJob();
    pollingIntervalRef.current = setInterval(pollJob, 3000);
  }, []);

  const generate = useCallback(
    async (brandId: string, prompt: string, templateId?: string) => {
      try {
        setIsGenerating(true);
        setError(null);
        setCurrentJob(null);

        const request: GenerateRequest = {
          brand_id: brandId,
          prompt,
          async_mode: true, // Always use async for better UX
          ...(templateId && { template_id: templateId }),
        };

        const response = await apiClient.post<GenerateResponse>(
          '/generate',
          request
        );

        // Start polling for job status
        startPolling(response.job_id);

        return response.job_id;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to generate asset';
        setError(errorMessage);
        setIsGenerating(false);
        throw new Error(errorMessage);
      }
    },
    [startPolling]
  );

  const tweak = useCallback(
    async (jobId: string, instructions: string) => {
      try {
        setIsGenerating(true);
        setError(null);

        const request: TweakRequest = {
          tweak_instructions: instructions,
        };

        await apiClient.post(`/jobs/${jobId}/tweak`, request);

        // Restart polling
        startPolling(jobId);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to apply tweak';
        setError(errorMessage);
        setIsGenerating(false);
        throw new Error(errorMessage);
      }
    },
    [startPolling]
  );

  const approve = useCallback(async (jobId: string) => {
    try {
      await apiClient.post(`/jobs/${jobId}/review`, {
        decision: 'approve',
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to approve';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const regenerate = useCallback(async (jobId: string) => {
    try {
      setIsGenerating(true);
      setError(null);

      await apiClient.post(`/jobs/${jobId}/review`, {
        decision: 'regenerate',
      });

      // Restart polling
      startPolling(jobId);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to regenerate';
      setError(errorMessage);
      setIsGenerating(false);
      throw new Error(errorMessage);
    }
  }, [startPolling]);

  return {
    generate,
    tweak,
    approve,
    regenerate,
    isGenerating,
    currentJob,
    error,
  };
};
