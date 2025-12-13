import { useEffect, useRef, useState, useCallback } from 'react';

interface UseKeyboardNavigationOptions {
  itemCount: number;
  onSelect?: (index: number) => void;
  onEscape?: () => void;
  loop?: boolean; // Whether to loop from last to first item
}

/**
 * useKeyboardNavigation - Custom hook for keyboard navigation in lists
 * 
 * Provides keyboard navigation functionality for lists using arrow keys.
 * Supports up/down navigation, Enter to select, and Escape to exit.
 * 
 * @param options - Configuration options
 * @returns Navigation state and handlers
 */
export function useKeyboardNavigation({
  itemCount,
  onSelect,
  onEscape,
  loop = true,
}: UseKeyboardNavigationOptions) {
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle keyboard events
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (itemCount === 0) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setFocusedIndex(prev => {
          if (prev === -1) return 0;
          if (prev >= itemCount - 1) return loop ? 0 : prev;
          return prev + 1;
        });
        break;

      case 'ArrowUp':
        event.preventDefault();
        setFocusedIndex(prev => {
          if (prev === -1) return itemCount - 1;
          if (prev <= 0) return loop ? itemCount - 1 : 0;
          return prev - 1;
        });
        break;

      case 'Enter':
      case ' ':
        event.preventDefault();
        if (focusedIndex >= 0 && focusedIndex < itemCount && onSelect) {
          onSelect(focusedIndex);
        }
        break;

      case 'Escape':
        event.preventDefault();
        setFocusedIndex(-1);
        if (onEscape) {
          onEscape();
        }
        break;

      case 'Home':
        event.preventDefault();
        setFocusedIndex(0);
        break;

      case 'End':
        event.preventDefault();
        setFocusedIndex(itemCount - 1);
        break;
    }
  }, [itemCount, focusedIndex, onSelect, onEscape, loop]);

  // Attach/detach keyboard event listeners
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('keydown', handleKeyDown);
    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  // Reset focused index when item count changes
  useEffect(() => {
    if (focusedIndex >= itemCount) {
      setFocusedIndex(-1);
    }
  }, [itemCount, focusedIndex]);

  // Focus the container when focused index changes
  useEffect(() => {
    if (focusedIndex >= 0 && containerRef.current) {
      const focusedElement = containerRef.current.querySelector(
        `[data-keyboard-index="${focusedIndex}"]`
      ) as HTMLElement;
      
      if (focusedElement) {
        focusedElement.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
        });
      }
    }
  }, [focusedIndex]);

  return {
    containerRef,
    focusedIndex,
    setFocusedIndex,
    handleKeyDown,
  };
}