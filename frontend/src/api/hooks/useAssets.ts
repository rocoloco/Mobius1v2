import { useState, useEffect } from 'react';
import { apiClient } from '../client';
import type { AssetListResponse } from '../types';
import type { Asset } from '../../types';

/**
 * Hook to fetch assets for the Vault
 */
export const useAssets = (brandId: string | null) => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!brandId) {
      setAssets([]);
      return;
    }

    const fetchAssets = async () => {
      try {
        setLoading(true);
        setError(null);

        // Note: The backend may not have this exact endpoint yet
        // This is based on the plan's API spec
        const response = await apiClient.get<AssetListResponse>(
          `/assets?brand_id=${brandId}`
        );

        // Convert API assets to internal type
        const convertedAssets: Asset[] = response.assets.map(a => ({
          id: a.asset_id,
          brandId: a.brand_id,
          name: `asset_${a.asset_id.slice(0, 8)}`,
          prompt: a.prompt,
          imageUrl: a.image_url,
          complianceScore: a.compliance_score,
          createdAt: a.created_at,
        }));

        setAssets(convertedAssets);
      } catch (err) {
        // If endpoint doesn't exist, fail gracefully
        console.warn('Assets endpoint not available:', err);
        setError(null);
        setAssets([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAssets();
  }, [brandId]);

  return { assets, loading, error };
};
