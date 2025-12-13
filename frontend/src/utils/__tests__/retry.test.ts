import { describe, it, expect, vi, beforeEach } from 'vitest';
import { retryWithBackoff, calculateBackoffDelay, RETRY_CONFIGS } from '../retry';

describe('Retry Utility', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('calculateBackoffDelay', () => {
    it('should calculate exponential backoff correctly', () => {
      expect(calculateBackoffDelay(0, 1000, 2, 30000)).toBe(1000); // 1000 * 2^0 = 1000
      expect(calculateBackoffDelay(1, 1000, 2, 30000)).toBe(2000); // 1000 * 2^1 = 2000
      expect(calculateBackoffDelay(2, 1000, 2, 30000)).toBe(4000); // 1000 * 2^2 = 4000
      expect(calculateBackoffDelay(3, 1000, 2, 30000)).toBe(8000); // 1000 * 2^3 = 8000
    });

    it('should cap delay at maxDelay', () => {
      expect(calculateBackoffDelay(10, 1000, 2, 5000)).toBe(5000); // Should be capped at 5000
    });
  });

  describe('retryWithBackoff', () => {
    it('should succeed on first attempt', async () => {
      const mockFn = vi.fn().mockResolvedValue('success');
      
      const result = await retryWithBackoff(mockFn, { maxAttempts: 3 });
      
      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should retry on failure and eventually succeed', async () => {
      const mockFn = vi.fn()
        .mockRejectedValueOnce(new Error('500'))
        .mockRejectedValueOnce(new Error('502'))
        .mockResolvedValue('success');
      
      const result = await retryWithBackoff(mockFn, { 
        maxAttempts: 3,
        baseDelay: 10, // Short delay for testing
      });
      
      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(3);
    });

    it('should throw error after max attempts', async () => {
      const mockFn = vi.fn().mockRejectedValue(new Error('500'));
      
      await expect(retryWithBackoff(mockFn, { 
        maxAttempts: 2,
        baseDelay: 10,
      })).rejects.toThrow('500');
      
      expect(mockFn).toHaveBeenCalledTimes(2);
    });

    it('should not retry on 4xx errors', async () => {
      const mockFn = vi.fn().mockRejectedValue(new Error('400'));
      
      await expect(retryWithBackoff(mockFn, { 
        maxAttempts: 3,
        baseDelay: 10,
      })).rejects.toThrow('400');
      
      expect(mockFn).toHaveBeenCalledTimes(1);
    });
  });

  describe('RETRY_CONFIGS', () => {
    it('should have correct configuration values', () => {
      expect(RETRY_CONFIGS.CRITICAL.maxAttempts).toBe(5);
      expect(RETRY_CONFIGS.STANDARD.maxAttempts).toBe(3);
      expect(RETRY_CONFIGS.FAST.maxAttempts).toBe(2);
      
      expect(RETRY_CONFIGS.CRITICAL.baseDelay).toBe(1000);
      expect(RETRY_CONFIGS.STANDARD.baseDelay).toBe(1000);
      expect(RETRY_CONFIGS.FAST.baseDelay).toBe(500);
    });
  });
});