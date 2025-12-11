// Brand Types
export interface Brand {
  id: string;
  name: string;
  archetype: string;
  color: string;
  voiceVectors: VoiceVectors;
  logoUrl?: string;
}

export interface VoiceVectors {
  formal: number;
  witty: number;
  technical: number;
  urgent: number;
}

// Asset Types
export interface Asset {
  id: string;
  brandId: string;
  name: string;
  prompt: string;
  imageUrl: string;
  complianceScore: number;
  createdAt: string;
}

// Violation Types
export interface Violation {
  category: string;
  ruleId: string;
  description: string;
  fixSuggestion: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

// Job Types
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

export interface Job {
  id: string;
  brandId: string;
  prompt: string;
  status: JobStatus;
  progress: number;
  imageUrl?: string;
  complianceScore?: number;
  violations?: Violation[];
  error?: string;
  createdAt: string;
  updatedAt: string;
}

// Generation State
export interface GenerationState {
  isGenerating: boolean;
  currentJob: Job | null;
  showAudit: boolean;
}

// Re-export monitoring types
export * from './monitoring';
