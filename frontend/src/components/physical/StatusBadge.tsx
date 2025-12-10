import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { useTicker } from '../../hooks/useTicker';

interface StatusBadgeProps {
  score: number;
  onClick?: () => void;
  animate?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  score,
  onClick,
  animate = true
}) => {
  const displayScore = animate ? useTicker(score) : score;
  const isPassing = score >= 80;

  return (
    <div
      onClick={onClick}
      className={`
        flex items-center gap-2 px-3 py-1.5 rounded-full
        shadow-pressed border border-white/40
        cursor-pointer hover:opacity-80 transition-opacity
        ${isPassing
          ? 'bg-success/10 text-success'
          : 'bg-accent/10 text-accent'
        }
      `}
    >
      {isPassing ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
      <span className="font-mono text-[10px] font-bold">
        SCORE: {displayScore}%
      </span>
    </div>
  );
};

export default StatusBadge;
