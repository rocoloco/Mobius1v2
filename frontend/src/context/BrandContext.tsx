import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useBrands, useBrandDetails, useAssets } from '../api/hooks';
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
}

const BrandContext = createContext<BrandContextValue | null>(null);

export const BrandProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  // Fetch brands from API
  const { brands: apiBrands, loading: brandsLoading, error: brandsError, refetch } = useBrands();

  const [activeBrandId, setActiveBrandIdState] = useState<string | null>(null);
  const [localBrands, setLocalBrands] = useState<Brand[]>([]);

  // Merge API brands with locally created brands
  const brands = [...apiBrands, ...localBrands];

  // Set initial active brand when brands load
  useEffect(() => {
    if (brands.length > 0 && !activeBrandId) {
      setActiveBrandIdState(brands[0].id);
    }
  }, [brands.length, activeBrandId]);

  // Fetch detailed brand data for active brand
  const { brand: detailedBrand, loading: brandLoading } = useBrandDetails(activeBrandId);

  // Use detailed brand data if available, otherwise fall back to list data
  const activeBrand = detailedBrand || brands.find((b) => b.id === activeBrandId) || null;

  // Fetch assets for active brand
  const { assets, loading: assetsLoading } = useAssets(activeBrandId);

  const loading = brandsLoading || brandLoading || assetsLoading;
  const error = brandsError;

  const setActiveBrandId = useCallback((id: string) => {
    setActiveBrandIdState(id);
  }, []);

  const addBrand = useCallback((brand: Brand) => {
    setLocalBrands((prev) => [...prev, brand]);
    setActiveBrandIdState(brand.id);
    // Refetch brands from API to get the newly created one
    setTimeout(refetch, 1000);
  }, [refetch]);

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
