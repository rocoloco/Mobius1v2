import React, { useRef, useState } from 'react';
import { luminousTokens } from '../../tokens';
import { generateNoisePattern } from '../../utils/noise';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean; // Static glow state (active/focus)
  spotlight?: boolean; // Interactive cursor spotlight
  noise?: boolean; // Organic texture
  shimmer?: boolean; // Entrance animation
  as?: React.ElementType;
  onClick?: () => void;
  [key: string]: any; // Allow additional props like data-testid
}

/**
 * GlassPanel - Unified Luminous glass component
 * 
 * A premium glassmorphism component that combines:
 * - Vertical light gradient (simulates light source)
 * - Interactive spotlight that follows cursor
 * - Specular border illumination
 * - Shimmer entrance animation
 * - Organic noise texture
 * - Milled edge highlight for 3D depth
 * 
 * @param glow - Static glow state for active/focus
 * @param spotlight - Enable interactive cursor spotlight
 * @param noise - Enable organic noise texture
 * @param shimmer - Enable entrance shimmer animation
 */
export function GlassPanel({
  children,
  className,
  glow = false,
  spotlight = false,
  noise = true,
  shimmer = false,
  as: Component = 'div',
  onClick,
  ...rest
}: GlassPanelProps) {
  // --- Spotlight Logic ---
  const prefersReducedMotion = useReducedMotion();
  const divRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!spotlight || !divRef.current) return;
    const rect = divRef.current.getBoundingClientRect();
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  // --- Visual Layer Construction ---
  // 1. The Base Gradient (Vertical Light Source)
  const baseGradient = 'linear-gradient(to bottom, rgba(255, 255, 255, 0.08), transparent)';
  
  // 2. The Noise Texture (Organic Feel)
  const noiseLayer = noise ? `, url("${generateNoisePattern(0.02)}")` : '';
  
  // 3. The "Milled Edge" Highlight (Inner Top Border)
  // Bump opacity from 0.2 to 0.4 on hover/glow for that "pop"
  const innerHighlight = glow || opacity > 0
    ? 'inset 0 1px 0 0 rgba(255, 255, 255, 0.4)'
    : 'inset 0 1px 0 0 rgba(255, 255, 255, 0.2)';
  
  // 4. The Glow Effect (Outer)
  const outerGlow = glow ? `, ${luminousTokens.effects.glow}` : '';

  return (
    <Component
      ref={divRef}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => spotlight && setOpacity(1)}
      onMouseLeave={() => spotlight && setOpacity(0)}
      className={cn(
        // Base Physics
        "relative overflow-hidden rounded-2xl backdrop-blur-md transition-all duration-300",
        // Border Physics (Light hits top harder)
        "border border-t-white/20 border-b-white/5 border-x-white/10",
        // Layout
        "group",
        className
      )}
      style={{
        background: `${baseGradient}${noiseLayer}`,
        backgroundSize: noise ? 'cover, 128px 128px' : 'cover',
        boxShadow: `${innerHighlight}${outerGlow}`,
      }}
      {...rest}
    >
      {/* LAYER 1: The Shimmer (Entrance Animation) */}
      {shimmer && (
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden rounded-2xl">
          <div 
            className="absolute top-0 h-full w-[50%] bg-gradient-to-r from-transparent via-white/10 to-transparent"
            style={{
              left: '-100%',
              transform: 'skewX(-20deg)',
              animation: !prefersReducedMotion ? 'shimmer 2.5s ease-out forwards' : 'none',
            }}
          />
        </div>
      )}

      {/* LAYER 2: The Spotlight (Interactive Light) */}
      {spotlight && (
        <div
          className="pointer-events-none absolute -inset-px transition-opacity duration-300 z-0"
          style={{
            opacity,
            background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(124, 58, 237, 0.15), transparent 40%)`,
          }}
        />
      )}

      {/* LAYER 3: The "Specular Border" (Follows Cursor) */}
      {/* This lights up the border closest to the mouse */}
      {spotlight && (
        <div
          className="absolute inset-0 rounded-2xl pointer-events-none z-10 transition-opacity duration-300"
          style={{
            opacity,
            background: `radial-gradient(400px circle at ${position.x}px ${position.y}px, rgba(255, 255, 255, 0.1), transparent 40%)`,
            maskImage: 'linear-gradient(black, black)',
            WebkitMaskImage: 'linear-gradient(black, black)',
            maskComposite: 'exclude',
            WebkitMaskComposite: 'xor',
            padding: '1px'
          }}
        />
      )}

      {/* LAYER 4: Content */}
      <div className="relative z-20 h-full w-full">
        {children}
      </div>

      {/* LAYER 5: Static Top Reflection (The "Lip") */}
      <div
        className="absolute inset-x-0 top-0 h-px rounded-t-2xl pointer-events-none z-30"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%)',
        }}
      />

      {/* Shimmer Animation Keyframes */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes shimmer {
            0% { left: -100%; opacity: 0; }
            10% { opacity: 1; }
            100% { left: 200%; opacity: 0; }
          }
        `
      }} />
    </Component>
  );
}
