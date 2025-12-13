/**
 * StudioLayout - The "Immersive Trinity" Layout
 * 
 * A 3-column layout optimized for creative workflow:
 * - Director (25%): Input/chat - the steering wheel
 * - Canvas (50%): Output/image - the stage (never moves)
 * - Critic (25%): Analysis - sleeps until generation completes
 * 
 * State-driven visual hierarchy:
 * - Idle: Director active, Canvas normal, Critic sleeping
 * - Generating: Director dimmed, Canvas glowing, Critic sleeping
 * - Complete: Director active, Canvas normal, Critic awake
 * 
 * During generation, "firefly" particles flow from Director → Canvas,
 * visualizing the user's ideas being assembled into an image.
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

type LayoutState = 'idle' | 'generating' | 'complete';

interface StudioLayoutProps {
  director: React.ReactNode;
  canvas: React.ReactNode;
  critic: React.ReactNode;
  /** Current state of the generation workflow */
  state: LayoutState;
}

// Particle configuration for the "ideas flowing" effect
const IDEA_PARTICLES = [
  { id: 1, startY: '15%', delay: 0, duration: 3.5, size: 10, yWave: 25 },
  { id: 2, startY: '30%', delay: 0.4, duration: 3.2, size: 7, yWave: -18 },
  { id: 3, startY: '45%', delay: 0.8, duration: 3.8, size: 12, yWave: 30 },
  { id: 4, startY: '60%', delay: 1.2, duration: 3.4, size: 8, yWave: -22 },
  { id: 5, startY: '75%', delay: 1.6, duration: 3.6, size: 9, yWave: 20 },
  { id: 6, startY: '25%', delay: 0.2, duration: 4.0, size: 6, yWave: -15 },
  { id: 7, startY: '55%', delay: 1.0, duration: 3.3, size: 11, yWave: 28 },
  { id: 8, startY: '85%', delay: 1.4, duration: 3.7, size: 8, yWave: -20 },
  { id: 9, startY: '40%', delay: 0.6, duration: 3.9, size: 7, yWave: 18 },
  { id: 10, startY: '70%', delay: 1.8, duration: 3.1, size: 10, yWave: -25 },
];

export function StudioLayout({
  director,
  canvas,
  critic,
  state,
}: StudioLayoutProps) {
  const prefersReducedMotion = useReducedMotion();

  const transition = {
    duration: prefersReducedMotion ? 0 : 0.5,
    ease: 'easeOut' as const,
  };

  // Director dims during generation
  const directorOpacity = state === 'generating' ? 0.6 : 1;
  
  // Canvas glows during generation
  const canvasGlow = state === 'generating';
  
  // Show particles during generation
  const showParticles = state === 'generating' && !prefersReducedMotion;

  return (
    <div
      className="studio-layout h-full flex relative"
      style={{ padding: '24px 32px 32px 32px', gap: '24px' }}
      data-testid="studio-layout"
    >
      {/* Idea Particles - Flow from Director to Canvas during generation */}
      <AnimatePresence>
        {showParticles && (
          <div 
            className="absolute pointer-events-none"
            style={{ 
              zIndex: 50,
              // Position over Director + Canvas area
              top: '24px',
              bottom: '32px', 
              left: '32px',
              // Span Director (25%) + gap (24px) + Canvas (50%) = ~75% + gap
              right: '25%',
              overflow: 'hidden',
            }}
          >
            {IDEA_PARTICLES.map((particle) => (
              <motion.div
                key={particle.id}
                className="absolute rounded-full"
                style={{
                  width: particle.size,
                  height: particle.size,
                  background: `radial-gradient(circle, rgba(167, 139, 250, 0.95) 0%, rgba(96, 165, 250, 0.6) 50%, transparent 100%)`,
                  boxShadow: '0 0 12px rgba(167, 139, 250, 0.5), 0 0 24px rgba(139, 92, 246, 0.3)',
                  top: particle.startY,
                }}
                initial={{ 
                  left: '5%',
                  opacity: 0,
                  scale: 0.2,
                }}
                animate={{
                  left: ['5%', '85%'], // Travel from Director to center of Canvas
                  y: [0, particle.yWave, 0, -particle.yWave * 0.5, 0],
                  opacity: [0, 1, 1, 1, 0],
                  scale: [0.2, 1, 1.1, 0.9, 0.3],
                }}
                exit={{
                  opacity: 0,
                  scale: 0,
                  transition: { duration: 0.3 }
                }}
                transition={{
                  duration: particle.duration,
                  delay: particle.delay,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  times: [0, 0.15, 0.5, 0.85, 1],
                }}
              />
            ))}
          </div>
        )}
      </AnimatePresence>

      {/* Director Zone - 25% width */}
      <motion.div
        className="studio-director overflow-hidden"
        style={{ width: '25%', minWidth: 0 }}
        animate={{ opacity: directorOpacity }}
        transition={transition}
        data-testid="zone-director"
      >
        {director}
      </motion.div>

      {/* Canvas Zone - 50% width - THE ROCK. Never resizes. */}
      <motion.div
        className="studio-canvas overflow-hidden relative"
        style={{ width: '50%', minWidth: 0 }}
        data-testid="zone-canvas"
      >
        {/* Glow effect during generation */}
        {canvasGlow && (
          <motion.div
            className="absolute inset-0 pointer-events-none rounded-3xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={transition}
            style={{
              boxShadow: '0 0 60px rgba(139, 92, 246, 0.3), 0 0 120px rgba(139, 92, 246, 0.15)',
              zIndex: 10,
            }}
          />
        )}
        {canvas}
      </motion.div>

      {/* Critic Zone - 25% width - The "Wake Up" Panel */}
      <div
        className="studio-critic overflow-hidden"
        style={{ width: '25%', minWidth: 0 }}
        data-testid="zone-critic"
      >
        {critic}
      </div>

      {/* Responsive styles */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @media (max-width: 1023px) {
            .studio-layout {
              flex-direction: column !important;
              padding: 16px !important;
              gap: 16px !important;
            }
            
            .studio-director,
            .studio-canvas,
            .studio-critic {
              width: 100% !important;
            }
            
            .studio-director { height: 40vh; min-height: 300px; }
            .studio-canvas { min-height: 400px; flex: 1; }
            .studio-critic { min-height: 300px; }
          }
        `
      }} />
    </div>
  );
}
