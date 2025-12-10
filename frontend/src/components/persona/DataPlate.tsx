import React, { useState, useEffect } from 'react';
import { ShieldCheck } from 'lucide-react';
import type { Brand } from '../../types';

interface DataPlateProps {
  brand: Brand | null;
}

/**
 * The "Machine Data Plate" - FOR THE BRAND GUARDIAN
 * Visualizes constraints (Voice, Archetype) as fixed hardware specs to build trust.
 * Shows the AI is "read-only" and constrained by brand rules.
 */
export const DataPlate: React.FC<DataPlateProps> = ({ brand }) => {
  const [animate, setAnimate] = useState(false);

  // Trigger animation when brand changes (Cartridge Load Effect)
  useEffect(() => {
    if (brand) {
      setAnimate(true);
      const timer = setTimeout(() => setAnimate(false), 300);
      return () => clearTimeout(timer);
    }
  }, [brand?.id]);

  if (!brand) {
    return null;
  }

  return (
    <div
      className={`
        hidden lg:block absolute top-24 left-8 z-0
        opacity-50 hover:opacity-100
        transition-all duration-300
        select-none
        ${animate ? 'opacity-0 blur-sm translate-y-2' : 'opacity-100 blur-0 translate-y-0'}
      `}
    >
      <div className="flex flex-col gap-4">
        {/* Screw Head */}
        <div className="w-3 h-3 rounded-full bg-ink/10 shadow-[inset_1px_1px_2px_rgba(0,0,0,0.15)]" />

        {/* Technical Specs */}
        <div className="space-y-4 font-mono text-[9px] uppercase tracking-widest text-ink-muted">
          {/* Identity Core */}
          <div>
            <span className="block opacity-40 mb-1">Identity Core</span>
            <div className="flex items-center gap-2">
              <ShieldCheck size={12} className="text-ink" />
              <span className="font-bold text-ink border border-ink/20 px-1 rounded">
                {brand.archetype}
              </span>
            </div>
          </div>

          {/* Voice Vector */}
          <div>
            <span className="block opacity-40 mb-1">Voice Vector</span>
            <div className="space-y-2">
              <VoiceMeter label="Formal" value={brand.voiceVectors.formal} />
              <VoiceMeter label="Witty" value={brand.voiceVectors.witty} />
              <VoiceMeter label="Technical" value={brand.voiceVectors.technical} />
              <VoiceMeter label="Urgent" value={brand.voiceVectors.urgent} />
            </div>
          </div>

          {/* System Version */}
          <div className="pt-2 border-t border-ink/10 w-24">
            <span className="block opacity-40">System</span>
            <span className="text-ink">Mobius v2.4</span>
          </div>
        </div>
      </div>
    </div>
  );
};

interface VoiceMeterProps {
  label: string;
  value: number; // 0.0 to 1.0
}

const VoiceMeter: React.FC<VoiceMeterProps> = ({ label, value }) => {
  const percentage = Math.round(value * 100);

  return (
    <div className="flex items-center gap-2">
      <span className="w-12">{label}</span>
      <div className="w-16 h-1.5 bg-ink/10 rounded-full overflow-hidden shadow-pressed">
        <div
          className="h-full bg-ink/40 transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default DataPlate;
