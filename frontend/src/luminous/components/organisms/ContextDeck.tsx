import React, { useEffect, useState } from 'react';
import { Linkedin, Twitter, Facebook, Instagram, EyeOff, Mic } from 'lucide-react';
import { ConstraintCard } from '../molecules/ConstraintCard';
import { GlassPanel } from '../atoms/GlassPanel';
import type { BrandGraphResponse } from '../../../api/types';

interface ContextDeckProps {
  brandId: string;
  activeConstraints?: string[];
  brandGraph?: BrandGraphResponse | null;
  loading?: boolean;
}

interface Constraint {
  id: string;
  type: 'channel' | 'negative' | 'voice';
  label: string;
  icon: React.ReactNode;
  active: boolean;
  metadata?: {
    voiceVectors?: {
      formal: number;
      witty: number;
      technical: number;
      urgent: number;
    };
  };
}

/**
 * Get platform icon based on context string
 */
function getPlatformIcon(context: string): React.ReactNode {
  const lowerContext = context.toLowerCase();
  
  if (lowerContext.includes('linkedin')) {
    return <Linkedin size={20} />;
  } else if (lowerContext.includes('twitter') || lowerContext.includes('x.com')) {
    return <Twitter size={20} />;
  } else if (lowerContext.includes('facebook')) {
    return <Facebook size={20} />;
  } else if (lowerContext.includes('instagram')) {
    return <Instagram size={20} />;
  }
  
  // Default icon for unknown platforms
  return <Linkedin size={20} />;
}

/**
 * ContextDeck - Constraint visualization panel
 * 
 * Displays active brand constraints as a vertical stack of pill-shaped cards.
 * Fetches constraint data from the brand graph API and renders channel constraints,
 * negative constraints, and voice constraints with appropriate icons and visualizations.
 * 
 * @param brandId - The brand ID to fetch constraints for
 * @param activeConstraints - Optional array of constraint IDs that should be highlighted
 */
export function ContextDeck({ 
  activeConstraints = [], 
  brandGraph = null, 
  loading = false 
}: ContextDeckProps) {
  const [constraints, setConstraints] = useState<Constraint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!brandGraph) {
      setConstraints([]);
      return;
    }

    try {
      setError(null);
      
      const parsedConstraints: Constraint[] = [];
      
      // Parse channel constraints from contextual_rules
      if (brandGraph.contextual_rules) {
        const channelRules = brandGraph.contextual_rules.filter(
          rule => rule.context && rule.context !== 'general'
        );
        
        channelRules.forEach((rule, index) => {
          parsedConstraints.push({
            id: `channel-${index}`,
            type: 'channel',
            label: rule.context,
            icon: getPlatformIcon(rule.context),
            active: activeConstraints.includes(`channel-${index}`),
          });
        });
      }
      
      // Parse negative constraints
      if (brandGraph.identity_core?.negative_constraints) {
        brandGraph.identity_core.negative_constraints.forEach((constraint, index) => {
          parsedConstraints.push({
            id: `negative-${index}`,
            type: 'negative',
            label: constraint,
            icon: <EyeOff size={20} />,
            active: activeConstraints.includes(`negative-${index}`),
          });
        });
      }
      
      // Parse voice constraints (only if at least one vector is non-zero)
      if (brandGraph.identity_core?.voice_vectors) {
        const vectors = brandGraph.identity_core.voice_vectors;
        const hasNonZeroVector = vectors.formal > 0 || vectors.witty > 0 || 
                                 vectors.technical > 0 || vectors.urgent > 0;
        
        if (hasNonZeroVector) {
          parsedConstraints.push({
            id: 'voice-vectors',
            type: 'voice',
            label: 'Brand Voice',
            icon: <Mic size={20} />,
            active: activeConstraints.includes('voice-vectors'),
            metadata: {
              voiceVectors: brandGraph.identity_core.voice_vectors,
            },
          });
        }
      }
      
      setConstraints(parsedConstraints);
    } catch (err) {
      console.error('Failed to parse brand graph:', err);
      setError(err instanceof Error ? err.message : 'Failed to parse constraints');
    }
  }, [brandGraph, JSON.stringify(activeConstraints)]);

  if (loading) {
    return (
      <GlassPanel className="h-full" spotlight={true} shimmer={false}>
        <div 
          className="flex flex-col h-full overflow-hidden" 
          style={{ padding: '24px', minHeight: 0 }}
        >
          {/* Header skeleton - match exact structure */}
          <div className="flex-shrink-0 mb-3">
            <div className="h-6 bg-white/10 rounded w-32 mb-1"></div>
            <div className="h-3 bg-white/5 rounded w-40 mt-0.5"></div>
          </div>
          
          {/* Constraint cards skeleton - match actual ConstraintCard structure */}
          <div className="flex-1 overflow-hidden" style={{ display: 'flex', flexDirection: 'column', gap: '0', minHeight: 0 }}>
            {[1, 2, 3].map((i) => (
              <div 
                key={i} 
                className="bg-white/5 rounded-xl motion-safe:animate-pulse"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  marginBottom: '8px',
                }}
              >
                <div 
                  className="bg-white/10 rounded"
                  style={{ flexShrink: 0, width: '20px', height: '20px' }}
                ></div>
                <div 
                  className="bg-white/10 rounded flex-1"
                  style={{ height: '16px' }}
                ></div>
              </div>
            ))}
          </div>
        </div>
      </GlassPanel>
    );
  }

  if (error) {
    return (
      <GlassPanel className="h-full" spotlight={true} shimmer={false}>
        <div className="flex items-center justify-center h-full overflow-hidden" style={{ padding: '24px', minHeight: 0 }}>
          <div className="text-red-400 text-sm">{error}</div>
        </div>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel className="h-full" spotlight={true} shimmer={false}>
      <div 
        className="flex flex-col h-full overflow-hidden" 
        style={{ padding: '24px', minHeight: 0 }}
        data-testid="context-deck"
      >
        {/* Header */}
        <div className="flex-shrink-0 mb-3">
          <h2 className="text-base font-semibold text-slate-100">Context Deck</h2>
          <p className="text-xs text-slate-400 mt-0.5">Active brand constraints</p>
        </div>
        
        {/* Constraints list - scrollable but hide scrollbar */}
        <div 
          className="flex-1 overflow-y-auto scrollbar-hide focus:outline-none focus:ring-2 focus:ring-blue-500/50" 
          style={{ display: 'flex', flexDirection: 'column', gap: '0', minHeight: 0 }}
          tabIndex={constraints.length > 0 ? 0 : -1}
          role={constraints.length > 0 ? "list" : undefined}
          aria-label={constraints.length > 0 ? "Brand constraints" : undefined}
        >
          {constraints.length === 0 ? (
            <div className="text-slate-400 text-sm text-center py-8" role="status">
              No constraints defined for this brand
            </div>
          ) : (
            constraints.map((constraint) => (
              <ConstraintCard
                key={constraint.id}
                type={constraint.type}
                label={constraint.label}
                icon={constraint.icon}
                active={constraint.active}
                metadata={constraint.metadata}
              />
            ))
          )}
        </div>
      </div>
    </GlassPanel>
  );
}
