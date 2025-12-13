/**
 * BrandGraphModal - Modal displaying brand graph details
 * 
 * Shows brand attributes from the MOAT (graph database):
 * - Colors with usage context
 * - Typography families
 * - Voice vectors (formal, witty, technical, urgent)
 * - Archetype
 * - Negative constraints
 * 
 * Styled with Luminous Structuralism - glassmorphism, gradients, and glow effects.
 */

import { memo, useCallback, useEffect } from 'react';
import { X, Palette, Type, Mic2, Shield, Sparkles } from 'lucide-react';
import { luminousTokens } from '../../tokens';
import type { BrandGraphResponse } from '../../../api/types';

interface BrandGraphModalProps {
  brandGraph: BrandGraphResponse;
  isOpen: boolean;
  onClose: () => void;
  logoUrl?: string;
}

export const BrandGraphModal = memo(function BrandGraphModal({
  brandGraph,
  isOpen,
  onClose,
  logoUrl,
}: BrandGraphModalProps) {
  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleBackdropClick = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }, [onClose]);

  if (!isOpen) return null;

  const { identity_core, visual_tokens } = brandGraph;
  const colors = visual_tokens?.colors || [];
  const typography = visual_tokens?.typography || [];
  const voiceVectors = identity_core?.voice_vectors;
  const archetype = identity_core?.archetype;
  const negativeConstraints = identity_core?.negative_constraints || [];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-6 sm:p-8 md:p-12"
      style={{ 
        backgroundColor: 'rgba(0, 0, 0, 0.8)', 
        backdropFilter: 'blur(12px)',
      }}
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="brand-graph-title"
    >
      {/* Modal Container with glow effect */}
      <div
        className="relative w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col rounded-3xl"
        style={{
          background: 'linear-gradient(135deg, rgba(30, 30, 45, 0.95) 0%, rgba(15, 15, 25, 0.98) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: `
            0 0 0 1px rgba(255, 255, 255, 0.05),
            0 25px 50px -12px rgba(0, 0, 0, 0.5),
            0 0 100px -20px rgba(139, 92, 246, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1)
          `,
        }}
      >
        {/* Spotlight effect */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse 80% 50% at 50% 0%, rgba(139, 92, 246, 0.15) 0%, transparent 60%)',
          }}
        />

        {/* Header */}
        <div 
          className="relative flex items-center justify-between border-b"
          style={{ 
            borderColor: 'rgba(255, 255, 255, 0.08)',
            padding: '32px 40px',
          }}
        >
          <div className="flex items-center gap-4">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
              }}
            >
              {logoUrl ? (
                <img
                  src={logoUrl}
                  alt={`${brandGraph.name} logo`}
                  className="max-w-10 max-h-10 object-contain"
                  onError={(e) => {
                    // Hide the image and show Sparkles fallback
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    const container = target.parentElement;
                    if (container) {
                      container.innerHTML = `<svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="${luminousTokens.colors.accent.purple}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.582a.5.5 0 0 1 0 .963L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>`;
                    }
                  }}
                />
              ) : (
                <Sparkles size={38} style={{ color: luminousTokens.colors.accent.purple }} />
              )}
            </div>
            <div>
              <h2
                id="brand-graph-title"
                className="text-xl font-semibold"
                style={{ color: luminousTokens.colors.text.high }}
              >
                {brandGraph.name}
              </h2>
              {archetype && (
                <span
                  className="text-xs"
                  style={{ color: luminousTokens.colors.text.muted }}
                >
                  {archetype}
                </span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2.5 rounded-xl transition-all duration-300 hover:scale-105"
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
            aria-label="Close modal"
          >
            <X size={18} style={{ color: luminousTokens.colors.text.muted }} />
          </button>
        </div>

        {/* Content - Scrollable */}
        <div 
          className="relative flex-1 overflow-y-auto space-y-8"
          style={{ padding: '32px 40px' }}
        >
          {/* Colors */}
          {colors.length > 0 && (
            <Section icon={<Palette size={16} />} title="Brand Colors">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {colors.map((color, idx) => (
                  <div
                    key={idx}
                    className="group relative flex items-center gap-4 p-4 rounded-2xl transition-all duration-300 hover:scale-[1.02]"
                    style={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid rgba(255, 255, 255, 0.06)',
                    }}
                  >
                    <div
                      className="w-12 h-12 rounded-xl flex-shrink-0 shadow-lg"
                      style={{ 
                        backgroundColor: color.hex, 
                        border: '2px solid rgba(255, 255, 255, 0.1)',
                        boxShadow: `0 4px 12px ${color.hex}40`,
                      }}
                    />
                    <div className="min-w-0 flex-1">
                      <div
                        className="text-sm font-mono font-medium"
                        style={{ color: luminousTokens.colors.text.high }}
                      >
                        {color.hex}
                      </div>
                      <div
                        className="text-xs truncate capitalize"
                        style={{ color: luminousTokens.colors.text.muted }}
                      >
                        {color.name || color.usage}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Section>
          )}

          {/* Typography */}
          {typography.length > 0 && (
            <Section icon={<Type size={16} />} title="Typography">
              <div className="space-y-3">
                {typography.map((font, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-4 rounded-2xl"
                    style={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid rgba(255, 255, 255, 0.06)',
                    }}
                  >
                    <span
                      className="text-base font-medium"
                      style={{ color: luminousTokens.colors.text.high }}
                    >
                      {font.family}
                    </span>
                    <span
                      className="text-xs px-3 py-1.5 rounded-full"
                      style={{ 
                        color: luminousTokens.colors.text.muted,
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      }}
                    >
                      {font.usage || font.weights?.join(', ')}
                    </span>
                  </div>
                ))}
              </div>
            </Section>
          )}

          {/* Voice Vectors */}
          {voiceVectors && (
            <Section icon={<Mic2 size={16} />} title="Voice Vectors">
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(voiceVectors).map(([key, value]) => (
                  <VoiceBar key={key} label={key} value={value as number} />
                ))}
              </div>
            </Section>
          )}

          {/* Negative Constraints */}
          {negativeConstraints.length > 0 && (
            <Section icon={<Shield size={16} />} title="Constraints">
              <div className="flex flex-wrap gap-3">
                {negativeConstraints.map((constraint, idx) => (
                  <span
                    key={idx}
                    className="text-xs px-4 py-2 rounded-full font-medium"
                    style={{
                      color: luminousTokens.colors.compliance.critical,
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.25)',
                    }}
                  >
                    {constraint}
                  </span>
                ))}
              </div>
            </Section>
          )}
        </div>

        {/* Footer gradient fade */}
        <div
          className="absolute bottom-0 left-0 right-0 h-20 pointer-events-none"
          style={{
            background: 'linear-gradient(to top, rgba(15, 15, 25, 0.9) 0%, transparent 100%)',
          }}
        />
      </div>
    </div>
  );
});

// Section component with icon and title
function Section({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <div
          className="p-2 rounded-lg"
          style={{
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%)',
          }}
        >
          <span style={{ color: luminousTokens.colors.accent.purple }}>{icon}</span>
        </div>
        <h3
          className="text-sm font-semibold uppercase tracking-wider"
          style={{ color: luminousTokens.colors.text.body }}
        >
          {title}
        </h3>
      </div>
      {children}
    </div>
  );
}

// Voice vector bar with gradient fill
function VoiceBar({ label, value }: { label: string; value: number }) {
  const percentage = Math.round(value * 100);
  
  return (
    <div
      className="rounded-2xl"
      style={{ 
        backgroundColor: 'rgba(255, 255, 255, 0.03)',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        padding: '20px 24px',
      }}
    >
      <div 
        className="flex items-center justify-between"
        style={{ marginBottom: '12px' }}
      >
        <span
          className="text-sm font-medium capitalize"
          style={{ color: luminousTokens.colors.text.body }}
        >
          {label}
        </span>
        <span
          className="text-xs font-mono rounded-md"
          style={{ 
            color: luminousTokens.colors.accent.purple,
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            padding: '4px 10px',
          }}
        >
          {percentage}%
        </span>
      </div>
      <div
        className="h-2 rounded-full overflow-hidden"
        style={{ backgroundColor: 'rgba(255, 255, 255, 0.08)' }}
      >
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${percentage}%`,
            background: `linear-gradient(90deg, ${luminousTokens.colors.accent.purple}, ${luminousTokens.colors.accent.blue})`,
            boxShadow: `0 0 12px ${luminousTokens.colors.accent.purple}60`,
          }}
        />
      </div>
    </div>
  );
}

BrandGraphModal.displayName = 'BrandGraphModal';
