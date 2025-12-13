/**
 * API Client for Mobius V2 Backend
 * Base URL configured from environment or defaults to Modal deployment
 */

import { retryWithBackoff, type RetryOptions } from '../utils/retry';

// Default to the Modal deployment URL, can be overridden
const DEFAULT_API_BASE = 'https://rocoloco--mobius-v2-final-fastapi-app.modal.run/v1';

class APIClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || DEFAULT_API_BASE;
  }

  setBaseUrl(url: string) {
    this.baseUrl = url;
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retryOptions?: RetryOptions
  ): Promise<T> {
    const makeRequest = async (): Promise<T> => {
      const url = `${this.baseUrl}${endpoint}`;

      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: response.statusText,
        }));
        const errorMessage = error.detail || `API Error: ${response.status}`;
        const apiError = new Error(errorMessage);
        
        // Add response status to error for retry logic
        (apiError as any).status = response.status;
        throw apiError;
      }

      return response.json();
    };

    // Use retry logic if retryOptions provided
    if (retryOptions) {
      return retryWithBackoff(makeRequest, retryOptions);
    }

    return makeRequest();
  }

  private async requestFormData<T>(
    endpoint: string,
    formData: FormData,
    retryOptions?: RetryOptions
  ): Promise<T> {
    const makeRequest = async (): Promise<T> => {
      const url = `${this.baseUrl}${endpoint}`;

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type - browser will set it with boundary for multipart/form-data
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: response.statusText,
        }));
        const errorMessage = error.detail || `API Error: ${response.status}`;
        const apiError = new Error(errorMessage);
        
        // Add response status to error for retry logic
        (apiError as any).status = response.status;
        throw apiError;
      }

      return response.json();
    };

    // Use retry logic if retryOptions provided
    if (retryOptions) {
      return retryWithBackoff(makeRequest, retryOptions);
    }

    return makeRequest();
  }

  async get<T>(endpoint: string, retryOptions?: RetryOptions): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' }, retryOptions);
  }

  async post<T>(endpoint: string, data?: unknown, retryOptions?: RetryOptions): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }, retryOptions);
  }

  async patch<T>(endpoint: string, data: unknown, retryOptions?: RetryOptions): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }, retryOptions);
  }

  async delete<T>(endpoint: string, retryOptions?: RetryOptions): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' }, retryOptions);
  }

  async postFormData<T>(endpoint: string, formData: FormData, retryOptions?: RetryOptions): Promise<T> {
    return this.requestFormData<T>(endpoint, formData, retryOptions);
  }
}

export const apiClient = new APIClient();
export default apiClient;
