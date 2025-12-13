import React, { useRef, useState } from 'react';
import { luminousTokens } from '../../tokens';

interface SpotlightCardProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * SpotlightCard - Premium hover effect component
 * 
 * Creates a radial gradient spotlight that follows the cursor,
 * simulating light interaction with a glass surface.
 * This adds the "aware" premium feel to cards.
 */
export function SpotlightCard({ children, className = '' }: SpotlightCardProps) {
  const divRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!divRef.current) return;
    const rect = divRef.current.getBoundingClientRect();
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  return (
    <div
      ref={divRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
      className={`relative rounded-2xl border border-t-white/20 border-b-white/5 border-x-white/10 backdrop-blur-md overflow-hidden ${className}`}
      style={{ 
        backdropFilter: luminousTokens.effects.backdropBlur,
        // Vertical gradient simulating light hitting top of glass + milled edge highlight
        background: 'linear-gradient(to bottom, rgba(255, 255, 255, 0.08), transparent)',
        boxShadow: 'inset 0 1px 0 0 rgba(255, 255, 255, 0.2)',
      }}
    >
      {/* The Spotlight Overlay */}
      <div
        className="pointer-events-none absolute -inset-px transition duration-300"
        style={{
          opacity,
          background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(124, 58, 237, 0.15), transparent 40%)`,
        }}
      />
      
      {/* Content */}
      <div className="relative h-full z-10">
        {children}
      </div>
    </div>
  );
}
