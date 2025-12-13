import { useEffect, useState } from 'react';

interface AriaLiveRegionsProps {
  statusMessage?: string;
  errorMessage?: string;
}

/**
 * AriaLiveRegions - Accessibility component for screen reader announcements
 * 
 * Provides aria-live regions for announcing status updates and errors to screen readers.
 * Uses aria-live="polite" for status updates and aria-live="assertive" for errors.
 * 
 * @param statusMessage - Status message to announce (e.g., "Generation started", "Audit complete")
 * @param errorMessage - Error message to announce (e.g., "Generation failed")
 */
export function AriaLiveRegions({ statusMessage, errorMessage }: AriaLiveRegionsProps) {
  const [currentStatus, setCurrentStatus] = useState<string>('');
  const [currentError, setCurrentError] = useState<string>('');

  // Update status message with debouncing to avoid rapid announcements
  useEffect(() => {
    if (statusMessage && statusMessage !== currentStatus) {
      const timer = setTimeout(() => {
        setCurrentStatus(statusMessage);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [statusMessage, currentStatus]);

  // Update error message immediately for urgent announcements
  useEffect(() => {
    if (errorMessage && errorMessage !== currentError) {
      setCurrentError(errorMessage);
    } else if (!errorMessage && currentError) {
      // Clear error message when error is resolved
      setCurrentError('');
    }
  }, [errorMessage, currentError]);

  return (
    <>
      {/* Status updates - polite announcements */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        data-testid="status-live-region"
      >
        {currentStatus}
      </div>

      {/* Error messages - assertive announcements */}
      <div
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
        data-testid="error-live-region"
      >
        {currentError}
      </div>
    </>
  );
}