import { useState, useEffect, useCallback } from 'react';
import type { Brand } from '../types';

const LAST_SELECTED_BRAND_KEY = 'mobius_last_selected_brand_id';

interface UseBrandSelectionProps {
  brands: Brand[];
  onBrandChange?: (brandId: string | null) => void;
}

interface UseBrandSelectionReturn {
  selectedBrandId: string | null;
  selectedBrand: Brand | null;
  selectBrand: (brandId: string) => void;
  clearSelection: () => void;
  shouldShowSelector: boolean;
  isMultiBrand: boolean;
}

/**
 * Hook for managing brand selection with localStorage persistence
 * 
 * Handles:
 * - Single brand auto-selection
 * - Multi-brand selection with persistence
 * - Last selected brand memory
 * - Brand change notifications
 */
export const useBrandSelection = ({
  brands,
  onBrandChange,
}: UseBrandSelectionProps): UseBrandSelectionReturn => {
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null);

  const isMultiBrand = brands.length > 1;
  const selectedBrand = brands.find(b => b.id === selectedBrandId) || null;

  // Determine if we should show the brand selector
  const shouldShowSelector = isMultiBrand && !selectedBrandId;

  // Load last selected brand from localStorage
  const loadLastSelectedBrand = useCallback(() => {
    try {
      const lastSelected = localStorage.getItem(LAST_SELECTED_BRAND_KEY);
      if (lastSelected && brands.some(b => b.id === lastSelected)) {
        return lastSelected;
      }
    } catch (error) {
      console.warn('Failed to load last selected brand from localStorage:', error);
    }
    return null;
  }, [brands]);

  // Save selected brand to localStorage
  const saveLastSelectedBrand = useCallback((brandId: string) => {
    try {
      localStorage.setItem(LAST_SELECTED_BRAND_KEY, brandId);
    } catch (error) {
      console.warn('Failed to save last selected brand to localStorage:', error);
    }
  }, []);

  // Initialize brand selection when brands load
  useEffect(() => {
    if (brands.length === 0) {
      return;
    }

    // Single brand: auto-select
    if (brands.length === 1) {
      const brandId = brands[0].id;
      setSelectedBrandId(brandId);
      saveLastSelectedBrand(brandId);
      onBrandChange?.(brandId);
      return;
    }

    // Multi-brand: try to restore last selected
    const lastSelected = loadLastSelectedBrand();
    if (lastSelected) {
      setSelectedBrandId(lastSelected);
      onBrandChange?.(lastSelected);
    } else {
      // No last selected brand, user needs to choose
      setSelectedBrandId(null);
      onBrandChange?.(null);
    }
  }, [brands, loadLastSelectedBrand, saveLastSelectedBrand, onBrandChange]);

  // Select a brand
  const selectBrand = useCallback((brandId: string) => {
    if (!brands.some(b => b.id === brandId)) {
      console.warn('Attempted to select non-existent brand:', brandId);
      return;
    }

    setSelectedBrandId(brandId);
    saveLastSelectedBrand(brandId);
    onBrandChange?.(brandId);
  }, [brands, saveLastSelectedBrand, onBrandChange]);

  // Clear selection (for multi-brand scenarios)
  const clearSelection = useCallback(() => {
    setSelectedBrandId(null);
    try {
      localStorage.removeItem(LAST_SELECTED_BRAND_KEY);
    } catch (error) {
      console.warn('Failed to clear last selected brand from localStorage:', error);
    }
    onBrandChange?.(null);
  }, [onBrandChange]);

  return {
    selectedBrandId,
    selectedBrand,
    selectBrand,
    clearSelection,
    shouldShowSelector,
    isMultiBrand,
  };
};