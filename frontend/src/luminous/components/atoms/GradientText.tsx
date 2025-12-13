import { useReducedMotion } from '../../../hooks/useReducedMotion';

interface GradientTextProps {
  children: string;
  animate?: boolean;
}

/**
 * GradientText - Animated gradient text component
 * 
 * Applies gradient background with text clipping for AI status indicators.
 * When animate is true, the gradient "breathes" - slowly panning across
 * the text to indicate the AI is working.
 * 
 * @param children - Text content to display
 * @param animate - Whether to animate the gradient (breathing effect)
 */
export function GradientText({ children, animate = false }: GradientTextProps) {
  const prefersReducedMotion = useReducedMotion();
  const shouldAnimate = animate && !prefersReducedMotion;
  return (
    <span className="relative inline-block overflow-hidden">
      <span
        className={`bg-clip-text text-transparent ${shouldAnimate ? 'animate-gradient-pan' : ''}`}
        style={{
          backgroundImage: 'linear-gradient(to right, #a855f7, #3b82f6, #a855f7)',
          backgroundSize: '200% auto',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        {children}
      </span>
      
      {/* Subtle blur glow behind text when animating */}
      {shouldAnimate && (
        <span 
          className="absolute inset-0 blur-lg animate-pulse pointer-events-none"
          style={{ 
            background: 'rgba(168, 85, 247, 0.2)',
            zIndex: -1,
          }}
        />
      )}
    </span>
  );
}
