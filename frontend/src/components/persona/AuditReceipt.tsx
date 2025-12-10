import React from 'react';
import { ChevronUp, AlertTriangle, Sparkles } from 'lucide-react';
import { PhysicalButton } from '../physical';
import type { Violation } from '../../types';

interface AuditReceiptProps {
  violations: Violation[];
  onClose: () => void;
  onAutoCorrect: () => void;
  onIgnore: () => void;
}

/**
 * The "Audit Receipt" - FOR THE EFFICIENCY OPERATOR
 * Slides up like a physical printout.
 * Explains the "Why" and offers a "Fix It" button for one-click resolution.
 */
export const AuditReceipt: React.FC<AuditReceiptProps> = ({
  violations,
  onClose,
  onAutoCorrect,
  onIgnore,
}) => {
  const primaryViolation = violations[0];

  if (!primaryViolation) {
    return null;
  }

  return (
    <div className="absolute bottom-28 w-96 bg-[#f8f9fa] shadow-soft rounded-2xl p-0 border border-white/60 animate-in z-30 overflow-hidden font-sans">
      {/* Header */}
      <div className="bg-[#f0f2f5] p-3 border-b border-ink/5 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <span className="text-[10px] font-bold uppercase text-ink tracking-widest">
            Audit Failed
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-ink-muted hover:text-ink transition-colors"
        >
          <ChevronUp size={14} className="rotate-180" />
        </button>
      </div>

      {/* Content */}
      <div className="p-5 space-y-4">
        {/* The Violation */}
        <div className="flex gap-3 items-start">
          <div className="mt-0.5 text-accent bg-accent/10 p-1.5 rounded-lg">
            <AlertTriangle size={16} />
          </div>
          <div>
            <p className="text-xs font-bold text-ink">
              {primaryViolation.ruleId}: {primaryViolation.category}
            </p>
            <p className="text-[11px] text-ink-muted mt-1 leading-relaxed">
              {primaryViolation.description}
              {primaryViolation.fixSuggestion && (
                <>
                  {' '}
                  <span className="font-mono text-ink bg-ink/5 px-1 rounded">
                    {primaryViolation.fixSuggestion}
                  </span>
                </>
              )}
            </p>
          </div>
        </div>

        {/* Show additional violations count if more than one */}
        {violations.length > 1 && (
          <div className="text-[10px] text-ink-muted font-mono">
            +{violations.length - 1} more violation{violations.length > 2 ? 's' : ''}
          </div>
        )}

        <div className="w-full h-px bg-ink/5" />

        {/* The Fix */}
        <div className="flex gap-3 items-center">
          <div className="text-xs font-bold text-ink-muted uppercase tracking-wide flex-1">
            Suggested Fix
          </div>
          <PhysicalButton variant="ghost" onClick={onIgnore}>
            Ignore
          </PhysicalButton>
          <PhysicalButton
            className="gap-2 text-accent"
            onClick={onAutoCorrect}
          >
            <Sparkles size={12} /> Auto-Correct
          </PhysicalButton>
        </div>
      </div>

      {/* Decorative "Tear off" bottom */}
      <div className="h-1 w-full bg-[repeating-linear-gradient(90deg,transparent,transparent_4px,#e0e5ec_4px,#e0e5ec_8px)] opacity-50" />
    </div>
  );
};

export default AuditReceipt;
