/**
 * Performance measurement utilities
 */

/**
 * Measure the execution time of a function or code block
 */
export const measurePerformance = (name: string) => {
  const start = performance.now();
  return () => {
    const end = performance.now();
    const duration = end - start;
    console.log(`⏱️ ${name}: ${duration.toFixed(2)}ms`);
    return duration;
  };
};

/**
 * Measure async function execution time
 */
export const measureAsync = async <T>(name: string, fn: () => Promise<T>): Promise<T> => {
  const stopTimer = measurePerformance(name);
  try {
    const result = await fn();
    stopTimer();
    return result;
  } catch (error) {
    stopTimer();
    throw error;
  }
};

/**
 * Log performance marks for debugging
 */
export const markPerformance = (name: string) => {
  if (typeof performance !== 'undefined' && performance.mark) {
    performance.mark(name);
    console.log(`📍 Performance mark: ${name}`);
  }
};

/**
 * Measure time between two performance marks
 */
export const measureBetweenMarks = (startMark: string, endMark: string, measureName: string) => {
  if (typeof performance !== 'undefined' && performance.measure) {
    try {
      performance.measure(measureName, startMark, endMark);
      const measure = performance.getEntriesByName(measureName)[0];
      console.log(`📏 ${measureName}: ${measure.duration.toFixed(2)}ms`);
      return measure.duration;
    } catch (error) {
      console.warn(`Could not measure between marks ${startMark} and ${endMark}:`, error);
    }
  }
  return 0;
};

/**
 * Log Core Web Vitals when available
 */
export const logWebVitals = () => {
  if (typeof window !== 'undefined') {
    // Log when page is fully loaded
    window.addEventListener('load', () => {
      // Log navigation timing
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        console.log('🚀 Navigation Timing:');
        console.log(`  DNS Lookup: ${(navigation.domainLookupEnd - navigation.domainLookupStart).toFixed(2)}ms`);
        console.log(`  TCP Connect: ${(navigation.connectEnd - navigation.connectStart).toFixed(2)}ms`);
        console.log(`  Request: ${(navigation.responseStart - navigation.requestStart).toFixed(2)}ms`);
        console.log(`  Response: ${(navigation.responseEnd - navigation.responseStart).toFixed(2)}ms`);
        console.log(`  DOM Processing: ${(navigation.domComplete - navigation.domLoading).toFixed(2)}ms`);
        console.log(`  Total Load Time: ${(navigation.loadEventEnd - navigation.navigationStart).toFixed(2)}ms`);
      }
    });

    // Log paint timing
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        console.log(`🎨 ${entry.name}: ${entry.startTime.toFixed(2)}ms`);
      }
    });
    
    try {
      observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
    } catch (error) {
      // Browser doesn't support these metrics
    }
  }
};

/**
 * Simple bundle size analyzer
 */
export const logBundleInfo = () => {
  if (typeof window !== 'undefined' && 'navigator' in window) {
    console.log('📦 Bundle Info:');
    console.log(`  User Agent: ${navigator.userAgent}`);
    console.log(`  Connection: ${(navigator as any).connection?.effectiveType || 'unknown'}`);
    console.log(`  Memory: ${(performance as any).memory ? 
      `${((performance as any).memory.usedJSHeapSize / 1024 / 1024).toFixed(2)}MB used` : 
      'unknown'}`);
  }
};