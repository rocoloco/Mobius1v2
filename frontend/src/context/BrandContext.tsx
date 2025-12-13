import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useBrands, useBrandDetails, useAssets } from '../api/hooks';
import { useBrandSelection } from '../hooks/useBrandSelection';
import type { Brand, Asset } from '../types';

interface BrandContextValue {
  brands: Brand[];
  activeBrand: Brand | null;
  assets: Asset[];
  loading: boolean;
  error: string | null;
  setActiveBrandId: (id: string) => void;
  addBrand: (brand: Brand) => void;
  addAsset: (asset: Asset) => void;
  refetchBrands: () => void;
  // New brand selection properties
  selectedBrandId: string | null;
  shouldShowBrandSelector: boolean;
  isMultiBrand: boolean;
  selectBrand: (brandId: string) => void;
  clearBrandSelection: () => void;
}

const BrandContext = createContext<BrandContextValue | null>(null);

export const BrandProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  // Fetch brands from API
  const { brands: apiBrands, loading: brandsLoading, error: brandsError, refetch } = useBrands();

  const [localBrands, setLocalBrands] = useState<Brand[]>([]);

  // Merge API brands with locally created brands
  const brands = [...apiBrands, ...localBrands];

  // Use brand selection hook for smart brand management
  const {
    selectedBrandId,
    selectedBrand,
    selectBrand,
    clearSelection,
    shouldShowSelector,
    isMultiBrand,
  } = useBrandSelection({
    brands,
    onBrandChange: (brandId) => {
      console.log('🔄 Brand changed to:', brandId);
    },
  });

  // Fetch detailed brand data for selected brand
  const { brand: detailedBrand, loading: brandLoading } = useBrandDetails(selectedBrandId);

  // Use detailed brand data if available, otherwise fall back to list data
  const activeBrand = detailedBrand || selectedBrand || null;

  // Fetch assets for selected brand
  const { assets, loading: assetsLoading } = useAssets(selectedBrandId);

  // Only consider it loading if we don't have the minimum data needed to render
  // We need at least brands loaded to show the dashboard
  const loading = brandsLoading;

  // Debug logging
  useEffect(() => {
    console.log('🔍 BrandContext State:', {
      brandsLoading,
      brandLoading,
      assetsLoading,
      finalLoading: loading,
      brandsCount: brands.length,
      selectedBrandId,
      shouldShowSelector,
      isMultiBrand,
    });
  }, [brandsLoading, brandLoading, assetsLoading, loading, brands.length, selectedBrandId, shouldShowSelector, isMultiBrand]);

  const error = brandsError;

  // Legacy compatibility - map to new brand selection system
  const setActiveBrandId = useCallback((id: string) => {
    selectBrand(id);
  }, [selectBrand]);

  const addBrand = useCallback((brand: Brand) => {
    setLocalBrands((prev) => [...prev, brand]);
    selectBrand(brand.id);
    // Refetch brands from API to get the newly created one
    setTimeout(refetch, 1000);
  }, [refetch, selectBrand]);

  const addAsset = useCallback((asset: Asset) => {
    // Assets are managed by useAssets hook, this is for compatibility
    console.log('Asset added:', asset);
  }, []);

  return (
    <BrandContext.Provider
      value={{
        brands,
        activeBrand,
        assets,
        loading,
        error,
        setActiveBrandId,
        addBrand,
        addAsset,
        refetchBrands: refetch,
        // New brand selection properties
        selectedBrandId,
        shouldShowBrandSelector: shouldShowSelector,
        isMultiBrand,
        selectBrand,
        clearBrandSelection: clearSelection,
      }}
    >
      {children}
    </BrandContext.Provider>
  );
};

export const useBrandContext = (): BrandContextValue => {
  const context = useContext(BrandContext);
  if (!context) {
    throw new Error('useBrandContext must be used within a BrandProvider');
  }
  return context;
};

export default BrandContext;
