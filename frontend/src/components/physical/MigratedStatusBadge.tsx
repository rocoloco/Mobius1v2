/**
 * Migrated Status Badge - Uses Polished Industrial Design System
 * 
 * This component replaces the original StatusBadge with the polished industrial design system
 * while maintaining backward compatibility with the existing API.
 */

import React from 'react';
import { PolishedIndustrialCard } from '../../design-system/components/PolishedIndustrialCard';
import { IndustrialIndicator } from '../../design-system/components/IndustrialIndicator';
import { useTicker } from '../../hooks/useTicker';

interface MigratedStatusBadgeProps {
  score: number;
  onClick?: () => void;
  animate?: boolean;
}

export const MigratedStatusBadge: React.FC<MigratedStatusBadgeProps> = ({
  score,
  onClick,
  animate = true
}) => {
  const displayScore = animate ? useTicker(score) : score;
  const isPassing = score >= 80;
  
  // Determine status for industrial indicator
  const indicatorStatus = isPassing ? 'success' : 'error';
  
  return (
    <PolishedIndustrialCard
      variant="interactive"
      size="sm"
      status={isPassing ? 'active' : 'warning'}
      onClick={onClick}
      className="cursor-pointer hover:scale-105 transition-transform duration-200 min-w-fit"
      manufacturing={{
        bolts: false, // Keep it clean for a badge
        texture: 'smooth'
      }}
      style={{
        padding: '8px 12px',
        borderRadius: '9999px', // Make it pill-shaped
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        minWidth: 'fit-content'
      }}
    >
      <div className="flex items-center gap-2">
        <IndustrialIndicator
          status={indicatorStatus}
          size="sm"
          glow={true}
        />
        <span className="font-mono text-[10px] font-bold tracking-wider uppercase">
          SCORE: {displayScore}%
        </span>
      </div>
    </PolishedIndustrialCard>
  );
};

export default MigratedStatusBadge;