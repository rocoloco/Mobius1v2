import { useState, useEffect } from 'react';
import { apiClient } from '../client';
import type { Asset } from '../../types';

interface AssetListResponse {
  assets: Array<{
    asset_id: string;
    brand_id: string;
    name: string;
    prompt: string;
    image_url: string;
    compliance_score: number;
    created_at: string;
  }>;
}

/**
 * Hook to fetch assets for a brand
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

        const response = await apiClient.get<AssetListResponse>(
          `/brands/${brandId}/assets`
        );

        const convertedAssets: Asset[] = response.assets.map(a => ({
          id: a.asset_id,
          brandId: a.brand_id,
          name: a.name,
          prompt: a.prompt,
          imageUrl: a.image_url,
          complianceScore: a.compliance_score,
          createdAt: a.created_at,
        }));

        setAssets(convertedAssets);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch assets');
        console.error('Error fetching assets:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAssets();
  }, [brandId]);

  return { assets, loading, error };
};
