/**
 * Migrated Data Plate - Uses Polished Industrial Design System
 * 
 * This component replaces the original DataPlate with the polished industrial design system
 * while maintaining backward compatibility with the existing API.
 */

import React, { useState, useEffect } from 'react';
import { PolishedIndustrialCard } from '../../design-system/components/PolishedIndustrialCard';
import { IndustrialIndicator } from '../../design-system/components/IndustrialIndicator';
import type { Brand } from '../../types';

interface MigratedDataPlateProps {
  brand: Brand | null;
}

/**
 * The "Machine Data Plate" - FOR THE BRAND GUARDIAN
 * Visualizes constraints (Voice, Archetype) as fixed hardware specs to build trust.
 * Shows the AI is "read-only" and constrained by brand rules.
 */
export const MigratedDataPlate: React.FC<MigratedDataPlateProps> = ({ brand }) => {
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
        hidden xl:block absolute top-24 z-0 w-56
        opacity-50 hover:opacity-100
        transition-all duration-300
        select-none
        ${animate ? 'opacity-0 blur-sm translate-y-2' : 'opacity-100 blur-0 translate-y-0'}
      `}
      style={{ right: 'calc(50% + 448px + 32px)' }}
    >
      <PolishedIndustrialCard
        variant="status"
        size="sm"
        neumorphic={true}
        manufacturing={{
          bolts: 'torx',
          texture: 'brushed'
        }}
        className="w-full"
      >
        <div className="space-y-4 font-mono text-[9px] uppercase tracking-widest text-gray-600">
          {/* Identity Core */}
          <div>
            <span className="block opacity-60 mb-2 text-gray-500">Identity Core</span>
            <div className="flex items-center gap-2">
              <IndustrialIndicator status="on" size="sm" glow={true} />
              <span className="font-bold text-gray-800 border border-gray-300 px-2 py-1 rounded text-[8px]">
                {brand.archetype}
              </span>
            </div>
          </div>

          {/* Voice Vector */}
          <div>
            <span className="block opacity-60 mb-2 text-gray-500">Voice Vector</span>
            <div className="space-y-2">
              <VoiceMeter label="Formal" value={brand.voiceVectors.formal} />
              <VoiceMeter label="Witty" value={brand.voiceVectors.witty} />
              <VoiceMeter label="Technical" value={brand.voiceVectors.technical} />
              <VoiceMeter label="Urgent" value={brand.voiceVectors.urgent} />
            </div>
          </div>

          {/* System Version */}
          <div className="pt-2 border-t border-gray-300/50">
            <span className="block opacity-60 text-gray-500">System</span>
            <span className="text-gray-800 font-semibold">Mobius v2.4</span>
          </div>
        </div>
      </PolishedIndustrialCard>
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
      <span className="w-12 text-[8px]">{label}</span>
      <div className="w-16 h-1.5 bg-gray-300/50 rounded-full overflow-hidden relative">
        <div
          className="h-full bg-blue-500/70 transition-all duration-500 rounded-full"
          style={{
            width: `${percentage}%`,
            boxShadow: 'inset 1px 1px 2px rgba(0,0,0,0.1)'
          }}
        />
      </div>
    </div>
  );
};

export default MigratedDataPlate;