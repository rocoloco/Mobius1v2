import { useState, useEffect } from 'react';
import { apiClient } from '../client';
import type { BrandListResponse, BrandDetailResponse, BrandGraphResponse } from '../types';
import type { Brand } from '../../types';

/**
 * Hook to fetch and manage brands list
 */
export const useBrands = () => {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBrands = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get<BrandListResponse>('/brands');

      // Convert API response to internal Brand type
      const convertedBrands: Brand[] = response.brands.map(b => ({
        id: b.brand_id,
        name: b.name,
        archetype: 'THE SAGE', // Will be fetched from graph endpoint
        color: '#ff4757', // Default, will be from brand details
        logoUrl: b.logo_thumbnail_url,
        voiceVectors: {
          formal: 0.5,
          witty: 0.5,
          technical: 0.5,
          urgent: 0.5,
        },
      }));

      setBrands(convertedBrands);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch brands');
      console.error('Error fetching brands:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBrands();
  }, []);

  return { brands, loading, error, refetch: fetchBrands };
};

/**
 * Hook to fetch detailed brand information including graph data
 */
export const useBrandDetails = (brandId: string | null) => {
  const [brand, setBrand] = useState<Brand | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!brandId) {
      setBrand(null);
      return;
    }

    const fetchBrandDetails = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch brand graph which includes identity core
        const graphResponse = await apiClient.get<BrandGraphResponse>(
          `/brands/${brandId}/graph`
        );

        // Also fetch basic details for logo
        const detailsResponse = await apiClient.get<BrandDetailResponse>(
          `/brands/${brandId}`
        );

        // Extract primary color from visual tokens
        const primaryColor = graphResponse.visual_tokens.colors.find(
          c => c.usage === 'primary'
        )?.hex || '#ff4757';

        const convertedBrand: Brand = {
          id: graphResponse.brand_id,
          name: graphResponse.name,
          archetype: graphResponse.identity_core.archetype,
          color: primaryColor,
          logoUrl: detailsResponse.logo_url,
          voiceVectors: graphResponse.identity_core.voice_vectors,
        };

        setBrand(convertedBrand);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch brand details');
        console.error('Error fetching brand details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchBrandDetails();
  }, [brandId]);

  return { brand, loading, error };
};

/**
 * Hook to create a new brand
 */
export const useCreateBrand = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createBrand = async (
    brandName: string,
    websiteUrl?: string,
    pdfFile?: File,
    logoFile?: File
  ) => {
    try {
      setLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('brand_name', brandName);
      formData.append('organization_id', '00000000-0000-0000-0000-000000000000');

      // Add website scan data if URL provided
      if (websiteUrl) {
        const scanResponse = await apiClient.post<any>('/brands/scan', {
          url: websiteUrl,
        });
        formData.append('visual_scan_data', JSON.stringify(scanResponse));
      }

      // Add PDF file
      if (pdfFile) {
        formData.append('file', pdfFile);
      }

      // Add logo file
      if (logoFile) {
        formData.append('logo', logoFile);
      }

      const response = await apiClient.postFormData<any>(
        '/brands/ingest',
        formData
      );

      return response.brand_id;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create brand';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { createBrand, loading, error };
};
