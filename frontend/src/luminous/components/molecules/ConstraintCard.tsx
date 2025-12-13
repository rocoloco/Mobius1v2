import React from 'react';
import { luminousTokens } from '../../tokens';

interface VoiceVectors {
  formal: number;
  witty: number;
  technical: number;
  urgent: number;
}

interface ConstraintCardProps {
  type: 'channel' | 'negative' | 'voice';
  label: string;
  icon: React.ReactNode;
  active?: boolean;
  metadata?: {
    voiceVectors?: VoiceVectors;
  };
}

/**
 * VoiceVectorBars - Horizontal bar visualization for voice vectors
 * 
 * Displays voice vector values as horizontal bars with labels,
 * providing a clearer visualization than a small radar chart.
 */
function VoiceVectorBars({ vectors }: { vectors: VoiceVectors }) {
  const bars = [
    { label: 'Formal', value: vectors.formal, key: 'formal' },
    { label: 'Witty', value: vectors.witty, key: 'witty' },
    { label: 'Tech', value: vectors.technical, key: 'technical' },
    { label: 'Urgent', value: vectors.urgent, key: 'urgent' },
  ];
  
  return (
    <div className="flex flex-col gap-1.5 min-w-[120px]">
      {bars.map((bar) => (
        <div key={bar.key} className="flex items-center gap-2">
          <span 
            className="text-[10px] font-mono w-10 text-right"
            style={{ color: luminousTokens.colors.text.muted }}
          >
            {bar.label}
          </span>
          <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{
                width: `${bar.value * 100}%`,
                background: luminousTokens.colors.accent.gradient,
              }}
            />
          </div>
          <span 
            className="text-[10px] font-mono w-6"
            style={{ color: luminousTokens.colors.text.body }}
          >
            {Math.round(bar.value * 100)}
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * ConstraintCard - Pill-shaped constraint card component
 * 
 * Displays a brand constraint with icon, label, and optional radar chart
 * for voice constraints. Used in the Context Deck to show active brand rules.
 * 
 * @param type - Constraint type ('channel', 'negative', or 'voice')
 * @param label - Constraint label text
 * @param icon - Icon component to display on the left
 * @param active - Whether the constraint is currently active/highlighted
 * @param metadata - Optional metadata including voice vectors for radar chart
 */
export function ConstraintCard({
  type,
  label,
  icon,
  active = false,
  metadata,
}: ConstraintCardProps) {
  const showVoiceVectors = type === 'voice' && metadata?.voiceVectors;
  
  return (
    <div
      data-testid="constraint-card"
      data-type={type}
      data-active={active}
      className="hover-lift"
      role="listitem"
      aria-label={`${type} constraint: ${label}${active ? ' (active)' : ''}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px 16px',
        borderRadius: '12px',
        border: active ? '1px solid rgba(168, 85, 247, 0.3)' : '1px solid rgba(255, 255, 255, 0.1)',
        backgroundColor: active ? 'rgba(168, 85, 247, 0.1)' : 'rgba(255, 255, 255, 0.05)',
        backdropFilter: luminousTokens.effects.backdropBlur,
        boxShadow: active ? luminousTokens.effects.glow : 'none',
        transition: 'all 300ms ease',
        marginBottom: '8px',
        cursor: 'pointer',
      }}
    >
      {/* Icon */}
      <div
        style={{ 
          flexShrink: 0, 
          width: '20px', 
          height: '20px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: active ? luminousTokens.colors.accent.purple : luminousTokens.colors.text.muted,
        }}
      >
        {icon}
      </div>
      
      {/* Label */}
      <span
        style={{ 
          flex: 1, 
          fontSize: '14px', 
          fontWeight: 500,
          color: active ? luminousTokens.colors.text.high : luminousTokens.colors.text.body,
        }}
      >
        {label}
      </span>
      
      {/* Voice vector bars for voice constraints */}
      {showVoiceVectors && (
        <VoiceVectorBars vectors={metadata.voiceVectors!} />
      )}
    </div>
  );
}
