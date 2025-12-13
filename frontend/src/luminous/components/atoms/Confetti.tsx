import { useEffect, useState } from 'react';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

interface ConfettiProps {
  trigger: boolean;
  onComplete?: () => void;
}

/**
 * Confetti - Lightweight CSS-based confetti animation
 * 
 * Triggers a confetti celebration when the trigger prop becomes true.
 * Uses CSS animations for performance and respects reduced motion preferences.
 * 
 * @param trigger - Whether to trigger the confetti animation
 * @param onComplete - Callback when animation completes
 */
export function Confetti({ trigger, onComplete }: ConfettiProps) {
  const [isAnimating, setIsAnimating] = useState(false);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    if (trigger && !prefersReducedMotion) {
      setIsAnimating(true);
      
      // Complete animation after 3 seconds
      const timer = setTimeout(() => {
        setIsAnimating(false);
        onComplete?.();
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [trigger, prefersReducedMotion, onComplete]);

  if (!isAnimating || prefersReducedMotion) {
    return null;
  }

  // Generate confetti pieces with random properties
  const confettiPieces = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    delay: Math.random() * 2,
    duration: 2 + Math.random() * 2,
    color: [
      '#7C3AED', // Purple
      '#2563EB', // Blue
      '#10B981', // Green
      '#F59E0B', // Amber
      '#EF4444', // Red
      '#EC4899', // Pink
    ][Math.floor(Math.random() * 6)],
    rotation: Math.random() * 360,
  }));

  return (
    <div
      className="fixed inset-0 pointer-events-none z-50"
      data-testid="confetti"
      aria-hidden="true"
    >
      {confettiPieces.map((piece) => (
        <div
          key={piece.id}
          className="absolute w-2 h-2 opacity-90"
          style={{
            left: `${piece.left}%`,
            top: '-10px',
            backgroundColor: piece.color,
            borderRadius: '2px',
            animation: `confetti-fall ${piece.duration}s linear ${piece.delay}s forwards`,
            transform: `rotate(${piece.rotation}deg)`,
          }}
        />
      ))}
      
      {/* CSS Animation keyframes */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes confetti-fall {
            0% {
              transform: translateY(-10px) rotate(0deg);
              opacity: 1;
            }
            100% {
              transform: translateY(100vh) rotate(720deg);
              opacity: 0;
            }
          }
        `
      }} />
    </div>
  );
}