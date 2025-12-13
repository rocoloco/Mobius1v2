/**
 * Retry Utility with Exponential Backoff
 * 
 * Implements retry logic with exponential backoff for failed API requests.
 * Requirements: 13.7
 */

export interface RetryOptions {
  maxAttempts?: number;
  baseDelay?: number; // Base delay in milliseconds
  maxDelay?: number; // Maximum delay in milliseconds
  backoffFactor?: number; // Multiplier for exponential backoff
  shouldRetry?: (error: Error, attempt: number) => boolean;
}

const DEFAULT_OPTIONS: Required<RetryOptions> = {
  maxAttempts: 3,
  baseDelay: 1000, // 1 second
  maxDelay: 30000, // 30 seconds
  backoffFactor: 2,
  shouldRetry: (error: Error, _attempt: number) => {
    // Retry on network errors, 5xx server errors, but not on 4xx client errors
    if (error.message.includes('fetch')) return true; // Network error
    if (error.message.includes('500')) return true; // Server error
    if (error.message.includes('502')) return true; // Bad gateway
    if (error.message.includes('503')) return true; // Service unavailable
    if (error.message.includes('504')) return true; // Gateway timeout
    return false;
  },
};

/**
 * Sleep utility for delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Calculate exponential backoff delay
 * 
 * @param attempt - Current attempt number (0-based)
 * @param baseDelay - Base delay in milliseconds
 * @param backoffFactor - Exponential backoff multiplier
 * @param maxDelay - Maximum delay cap
 * @returns Delay in milliseconds
 */
export function calculateBackoffDelay(
  attempt: number,
  baseDelay: number,
  backoffFactor: number,
  maxDelay: number
): number {
  const delay = baseDelay * Math.pow(backoffFactor, attempt);
  return Math.min(delay, maxDelay);
}

/**
 * Retry a function with exponential backoff
 * 
 * @param fn - Function to retry (should return a Promise)
 * @param options - Retry configuration options
 * @returns Promise that resolves with the function result or rejects with the last error
 * 
 * @example
 * ```typescript
 * const result = await retryWithBackoff(
 *   () => apiClient.post('/generate', data),
 *   { maxAttempts: 3, baseDelay: 1000 }
 * );
 * ```
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  let lastError: Error;

  for (let attempt = 0; attempt < opts.maxAttempts; attempt++) {
    try {
      // Attempt the function
      const result = await fn();
      return result;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      // Check if we should retry this error
      if (!opts.shouldRetry(lastError, attempt)) {
        throw lastError;
      }
      
      // If this was the last attempt, throw the error
      if (attempt === opts.maxAttempts - 1) {
        throw lastError;
      }
      
      // Calculate delay for next attempt
      const delay = calculateBackoffDelay(
        attempt,
        opts.baseDelay,
        opts.backoffFactor,
        opts.maxDelay
      );
      
      // Log retry attempt for debugging
      console.warn(`Retry attempt ${attempt + 1}/${opts.maxAttempts} after ${delay}ms delay:`, {
        error: lastError.message,
        attempt: attempt + 1,
        delay,
      });
      
      // Wait before retrying
      await sleep(delay);
    }
  }
  
  // This should never be reached, but TypeScript requires it
  throw lastError!;
}

/**
 * Create a retry wrapper for API client methods
 * 
 * @param apiMethod - API method to wrap with retry logic
 * @param options - Retry configuration options
 * @returns Wrapped API method with retry logic
 * 
 * @example
 * ```typescript
 * const retryablePost = createRetryWrapper(
 *   (endpoint, data) => apiClient.post(endpoint, data),
 *   { maxAttempts: 3 }
 * );
 * 
 * const result = await retryablePost('/generate', requestData);
 * ```
 */
export function createRetryWrapper<TArgs extends any[], TReturn>(
  apiMethod: (...args: TArgs) => Promise<TReturn>,
  options: RetryOptions = {}
) {
  return async (...args: TArgs): Promise<TReturn> => {
    return retryWithBackoff(() => apiMethod(...args), options);
  };
}

/**
 * Retry configuration for different types of operations
 */
export const RETRY_CONFIGS = {
  // For critical operations like generation requests
  CRITICAL: {
    maxAttempts: 5,
    baseDelay: 1000,
    maxDelay: 30000,
    backoffFactor: 2,
  } as RetryOptions,
  
  // For less critical operations like status checks
  STANDARD: {
    maxAttempts: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffFactor: 2,
  } as RetryOptions,
  
  // For quick operations that should fail fast
  FAST: {
    maxAttempts: 2,
    baseDelay: 500,
    maxDelay: 2000,
    backoffFactor: 2,
  } as RetryOptions,
} as const;