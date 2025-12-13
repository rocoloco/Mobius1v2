/**
 * API Response Types matching Mobius V2 Backend
 */

// Health Check
export interface HealthCheckResponse {
  status: string;
  version: string;
  supabase: boolean;
  neo4j: boolean;
}

// Brand Ingestion
export interface IngestBrandResponse {
  brand_id: string;
  status: string;
  needs_review: {
    brand_identity: boolean;
    visual_analysis: boolean;
  };
  message: string;
}

// Visual Scan
export interface VisualScanResponse {
  archetype: string;
  colors: Array<{
    hex: string;
    name: string;
    usage: string;
  }>;
  fonts: string[];
  voice: {
    adjectives: string[];
    forbidden_words: string[];
  };
}

// Brand List
export interface BrandListItem {
  brand_id: string;
  name: string;
  logo_thumbnail_url?: string;
  asset_count: number;
  avg_compliance_score: number;
  last_activity: string;
}

export interface BrandListResponse {
  brands: BrandListItem[];
  total: number;
}

// Brand Detail
export interface BrandDetailResponse {
  brand_id: string;
  name: string;
  organization_id: string;
  logo_url?: string;
  guidelines: BrandGuidelines;
  created_at: string;
  updated_at: string;
}

export interface BrandGuidelines {
  identity_core: {
    archetype: string;
    voice_vectors: {
      formal: number;
      witty: number;
      technical: number;
      urgent: number;
    };
    negative_constraints: string[];
  };
  colors: Array<{
    name: string;
    hex: string;
    usage: 'primary' | 'secondary' | 'accent' | 'neutral' | 'semantic';
    usage_weight: number;
    context: string;
  }>;
  typography: Array<{
    family: string;
    weights: string[];
    usage: string;
  }>;
  logos: Array<{
    variant_name: string;
    url: string;
    min_width_px: number;
    clear_space_ratio: number;
    forbidden_backgrounds: string[];
  }>;
  voice: {
    adjectives: string[];
    forbidden_words: string[];
    example_phrases: string[];
  };
  rules: Array<{
    category: 'visual' | 'verbal' | 'legal';
    instruction: string;
    severity: 'warning' | 'critical';
    negative_constraint: boolean;
  }>;
  source_filename?: string;
  ingested_at?: string;
  version?: string;
}

// Brand Graph (MOAT)
export interface BrandGraphResponse {
  brand_id: string;
  name: string;
  version: string;
  identity_core: {
    archetype: string;
    voice_vectors: {
      formal: number;
      witty: number;
      technical: number;
      urgent: number;
    };
    negative_constraints: string[];
  };
  visual_tokens: {
    colors: BrandGuidelines['colors'];
    typography: BrandGuidelines['typography'];
    logos: BrandGuidelines['logos'];
  };
  contextual_rules: Array<{
    context: string;
    rule: string;
    priority: number;
    applies_to: string[];
  }>;
  asset_graph: {
    logos: Record<string, string>;
    templates: Record<string, string>;
    patterns: Record<string, string>;
    photography_style?: string;
  };
  relationships: {
    color_count: number;
    colors_with_usage: unknown[];
  };
  metadata: {
    created_at: string;
    updated_at: string;
    source_filename?: string;
    ingested_at?: string;
  };
}

// Generation
export interface GenerateRequest {
  brand_id: string;
  prompt: string;
  async_mode?: boolean;
  template_id?: string;
  webhook_url?: string;
  // Multi-turn generation fields
  session_id?: string;
  previous_image_url?: string;
  context?: string; // e.g., "social_linkedin"
}

export interface GenerateResponse {
  job_id: string;
  status: JobStatus;
  message: string;
  image_url?: string;
}

// Twin Data (for visual token inspection)
export interface TwinData {
  colors_detected: string[];
  fonts_detected: Array<{
    family: string;
    weight: string;
    allowed: boolean;
  }>;
}

// Job Status
export type JobStatus =
  | 'pending'
  | 'processing'
  | 'generating'
  | 'auditing'
  | 'correcting'
  | 'needs_review'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface JobStatusResponse {
  job_id: string;
  brand_id: string;
  prompt: string;
  status: JobStatus;
  progress: number;
  current_image_url?: string;
  compliance_score?: number;
  violations?: Violation[];
  twin_data?: TwinData;
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface Violation {
  category: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  fix_suggestion?: string;
}

// Review Decision
export interface ReviewRequest {
  decision: 'approve' | 'tweak' | 'regenerate';
  feedback?: string;
}

export interface ReviewResponse {
  job_id: string;
  status: JobStatus;
  message: string;
}

// Tweak Request
export interface TweakRequest {
  tweak_instructions: string;
}

export interface TweakResponse {
  job_id: string;
  status: JobStatus;
  message: string;
}

// Assets (for Vault)
export interface Asset {
  asset_id: string;
  brand_id: string;
  job_id: string;
  prompt: string;
  image_url: string;
  compliance_score: number;
  compliance_details: {
    categories: Array<{
      category: string;
      score: number;
      passed: boolean;
      violations: Violation[];
    }>;
    violations: Violation[];
  };
  status: 'approved' | 'rejected' | 'pending';
  created_at: string;
  updated_at: string;
}

export interface AssetListResponse {
  assets: Asset[];
  total: number;
}

// Templates
export interface Template {
  template_id: string;
  brand_id: string;
  name: string;
  description: string;
  generation_params: Record<string, unknown>;
  thumbnail_url: string;
  source_asset_id?: string;
  created_at: string;
  updated_at: string;
}

export interface TemplateListResponse {
  templates: Template[];
  total: number;
}

// Session History (for multi-turn generation)
export interface Version {
  attempt_id: number;
  image_url: string;
  thumb_url: string;
  score: number;
  timestamp: string;
  prompt: string;
}

export interface SessionHistoryResponse {
  session_id: string;
  versions: Version[];
}
