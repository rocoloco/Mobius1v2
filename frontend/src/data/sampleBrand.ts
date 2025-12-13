/**
 * Sample Brand Data for Development
 * 
 * This provides realistic brand data when the API is not available
 * or for testing the dashboard components.
 */

import type { BrandGraphResponse } from '../api/types';

export const sampleBrandGraph: BrandGraphResponse = {
  brand_id: 'demo-brand-123',
  name: 'Acme Innovation Labs',
  version: '2.1.0',
  identity_core: {
    archetype: 'The Innovator',
    voice_vectors: {
      formal: 0.7,
      witty: 0.4,
      technical: 0.8,
      urgent: 0.2,
    },
    negative_constraints: [
      'No stock photography',
      'Avoid aggressive language',
      'No competitor mentions',
      'No Comic Sans font',
      'Avoid red backgrounds',
    ],
  },
  visual_tokens: {
    colors: [
      {
        name: 'Primary Blue',
        hex: '#2563EB',
        usage: 'primary',
        usage_weight: 0.4,
        context: 'Brand primary color for headers and CTAs',
      },
      {
        name: 'Innovation Purple',
        hex: '#7C3AED',
        usage: 'accent',
        usage_weight: 0.3,
        context: 'Accent color for highlights and innovation themes',
      },
      {
        name: 'Success Green',
        hex: '#10B981',
        usage: 'semantic',
        usage_weight: 0.2,
        context: 'Success states and positive messaging',
      },
      {
        name: 'Warning Amber',
        hex: '#F59E0B',
        usage: 'semantic',
        usage_weight: 0.1,
        context: 'Warnings and attention-grabbing elements',
      },
    ],
    typography: [
      {
        family: 'Inter',
        weights: ['400', '500', '600', '700'],
        usage: 'Primary font for all body text and headers',
      },
      {
        family: 'JetBrains Mono',
        weights: ['400', '500'],
        usage: 'Code snippets and technical documentation',
      },
    ],
    logos: [
      {
        variant_name: 'Primary Logo',
        url: 'https://via.placeholder.com/200x80/2563EB/FFFFFF?text=ACME',
        min_width_px: 120,
        clear_space_ratio: 0.5,
        forbidden_backgrounds: ['#FF0000', '#000000'],
      },
    ],
  },
  contextual_rules: [
    {
      context: 'LinkedIn',
      rule: 'Use professional tone and focus on B2B messaging',
      priority: 1,
      applies_to: ['social', 'professional'],
    },
    {
      context: 'Twitter',
      rule: 'Keep messages concise and engaging, use hashtags strategically',
      priority: 2,
      applies_to: ['social', 'casual'],
    },
    {
      context: 'Technical Documentation',
      rule: 'Use precise language and include code examples where relevant',
      priority: 1,
      applies_to: ['documentation', 'technical'],
    },
    {
      context: 'Marketing Materials',
      rule: 'Emphasize innovation and cutting-edge technology',
      priority: 1,
      applies_to: ['marketing', 'sales'],
    },
  ],
  asset_graph: {
    logos: {
      'primary': 'https://via.placeholder.com/200x80/2563EB/FFFFFF?text=ACME',
      'white': 'https://via.placeholder.com/200x80/FFFFFF/2563EB?text=ACME',
    },
    templates: {
      'social-post': 'template-social-001',
      'presentation': 'template-deck-001',
    },
    patterns: {
      'gradient': 'linear-gradient(135deg, #2563EB, #7C3AED)',
      'texture': 'subtle-noise-pattern',
    },
    photography_style: 'Clean, modern, technology-focused imagery with blue accent lighting',
  },
  relationships: {
    color_count: 4,
    colors_with_usage: [
      { hex: '#2563EB', usage_count: 12 },
      { hex: '#7C3AED', usage_count: 8 },
      { hex: '#10B981', usage_count: 5 },
      { hex: '#F59E0B', usage_count: 3 },
    ],
  },
  metadata: {
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-12-12T15:45:00Z',
    source_filename: 'acme-brand-guidelines-v2.1.pdf',
    ingested_at: '2024-12-12T15:45:00Z',
  },
};

export const sampleViolations = [
  {
    severity: 'critical' as const,
    description: 'Logo is too small - minimum width is 120px, current is 80px',
    bounding_box: [100, 50, 80, 32] as [number, number, number, number],
  },
  {
    severity: 'high' as const,
    description: 'Using unauthorized red color #FF0000 - use brand colors only',
    bounding_box: [200, 150, 150, 100] as [number, number, number, number],
  },
  {
    severity: 'medium' as const,
    description: 'Font weight too light - use minimum 500 weight for headers',
    bounding_box: [50, 200, 300, 40] as [number, number, number, number],
  },
  {
    severity: 'low' as const,
    description: 'Consider using brand purple accent for better visual hierarchy',
    bounding_box: [400, 100, 100, 50] as [number, number, number, number],
  },
];

export const sampleTwinData = {
  colors_detected: ['#2563EB', '#FF0000', '#CCCCCC', '#000000'],
  fonts_detected: [
    { family: 'Inter', weight: '400', allowed: true },
    { family: 'Arial', weight: '400', allowed: false },
    { family: 'JetBrains Mono', weight: '500', allowed: true },
  ],
};