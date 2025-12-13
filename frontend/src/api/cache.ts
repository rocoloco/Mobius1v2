/**
 * Simple API Cache for deduplicating requests and caching responses
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  promise?: Promise<T>;
}

class APICache {
  private cache = new Map<string, CacheEntry<any>>();
  private readonly TTL = 5 * 60 * 1000; // 5 minutes

  /**
   * Get data from cache or fetch if not available/expired
   */
  async get<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
    const cached = this.cache.get(key);
    
    // Return cached data if still valid
    if (cached && Date.now() - cached.timestamp < this.TTL && cached.data) {
      return cached.data;
    }
    
    // Return in-flight promise if exists (deduplication)
    if (cached?.promise) {
      return cached.promise;
    }
    
    // Create new request
    const promise = fetcher();
    this.cache.set(key, { data: null, timestamp: Date.now(), promise });
    
    try {
      const data = await promise;
      this.cache.set(key, { data, timestamp: Date.now() });
      return data;
    } catch (error) {
      this.cache.delete(key);
      throw error;
    }
  }

  /**
   * Clear cache entry
   */
  clear(key: string) {
    this.cache.delete(key);
  }

  /**
   * Clear all cache entries
   */
  clearAll() {
    this.cache.clear();
  }

  /**
   * Get cache size
   */
  size() {
    return this.cache.size;
  }
}

export const apiCache = new APICache();
export default apiCache;