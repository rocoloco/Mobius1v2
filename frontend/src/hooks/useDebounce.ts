/**
 * useDebounce - Custom hook for debouncing values and callbacks
 * 
 * Provides debounced values and callbacks to prevent excessive re-renders
 * and API calls during rapid user input.
 * 
 * Requirements: 12.1-12.7 (Performance optimization)
 */

import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * useDebounce - Debounce a value
 * 
 * Returns a debounced version of the value that only updates
 * after the specified delay has passed without changes.
 * 
 * @param value - The value to debounce
 * @param delay - Delay in milliseconds (default: 300ms)
 * @returns The debounced value
 * 
 * @example
 * ```tsx
 * const [searchTerm, setSearchTerm] = useState('');
 * const debouncedSearch = useDebounce(searchTerm, 300);
 * 
 * useEffect(() => {
 *   // Only fires 300ms after user stops typing
 *   performSearch(debouncedSearch);
 * }, [debouncedSearch]);
 * ```
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * useDebouncedCallback - Debounce a callback function
 * 
 * Returns a debounced version of the callback that only executes
 * after the specified delay has passed without being called again.
 * 
 * @param callback - The callback function to debounce
 * @param delay - Delay in milliseconds (default: 300ms)
 * @returns The debounced callback
 * 
 * @example
 * ```tsx
 * const handleResize = useDebouncedCallback(() => {
 *   // Only fires 300ms after resize stops
 *   recalculateLayout();
 * }, 300);
 * 
 * useEffect(() => {
 *   window.addEventListener('resize', handleResize);
 *   return () => window.removeEventListener('resize', handleResize);
 * }, [handleResize]);
 * ```
 */
export function useDebouncedCallback<T extends (...args: never[]) => void>(
  callback: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const callbackRef = useRef(callback);

  // Update callback ref when callback changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      callbackRef.current(...args);
    }, delay);
  }, [delay]);
}

/**
 * useWindowResize - Debounced window resize handler
 * 
 * Provides debounced window dimensions that update after resize stops.
 * 
 * @param delay - Debounce delay in milliseconds (default: 300ms)
 * @returns Object with width and height
 * 
 * @example
 * ```tsx
 * const { width, height } = useWindowResize(300);
 * 
 * const isMobile = width < 768;
 * ```
 */
export function useWindowResize(delay: number = 300): { width: number; height: number } {
  const [dimensions, setDimensions] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  });

  const handleResize = useDebouncedCallback(() => {
    setDimensions({
      width: window.innerWidth,
      height: window.innerHeight,
    });
  }, delay);

  useEffect(() => {
    // Set initial dimensions
    setDimensions({
      width: window.innerWidth,
      height: window.innerHeight,
    });

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [handleResize]);

  return dimensions;
}

export default useDebounce;
