import { useState, useEffect } from 'react';

/**
 * Hook that animates a number counting up from 0 to the target value.
 * Creates a "sensor measuring" effect rather than instant display.
 *
 * @param endValue - The final value to count up to
 * @param duration - Animation duration in milliseconds (default: 1000ms)
 * @returns The current animated value
 */
export const useTicker = (endValue: number, duration: number = 1000): number => {
  const [value, setValue] = useState(0);

  useEffect(() => {
    // Reset to 0 when endValue changes
    setValue(0);

    if (endValue === 0) return;

    let start = 0;
    const increment = endValue / (duration / 16); // 60fps target

    const timer = setInterval(() => {
      start += increment;
      if (start >= endValue) {
        setValue(endValue);
        clearInterval(timer);
      } else {
        setValue(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [endValue, duration]);

  return value;
};

export default useTicker;
