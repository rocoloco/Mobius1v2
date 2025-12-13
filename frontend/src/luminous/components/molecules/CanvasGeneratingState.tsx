import { memo } from 'react';
import { motion } from 'framer-motion';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

/**
 * CanvasGeneratingState - Premium "Assembling" state for Canvas
 * 
 * Transforms the waiting experience from a dead void into a living,
 * breathing stage that builds anticipation. Inspired by Jobs' philosophy:
 * "Don't make users wait - entertain them."
 * 
 * Features:
 * - Breathing pulse: Subtle gradient animation showing the system is alive
 * - Active language: "Assembling" instead of passive "Thinking"
 * - Spinning core: Focus point with elegant rotation
 * 
 * Note: Particle drift ("fireflies") is handled at the StudioLayout level
 * so particles can visually flow from Director → Canvas across panels.
 */
export const CanvasGeneratingState = memo(function CanvasGeneratingState() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <div 
      className="relative w-full h-full flex items-center justify-center overflow-hidden rounded-lg"
      data-testid="generating-state"
    >
      {/* 1. The Deep Breathing Pulse (The Heartbeat) */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at center, rgba(124, 58, 237, 0.08) 0%, rgba(59, 130, 246, 0.04) 40%, transparent 70%)',
          animation: !prefersReducedMotion ? 'canvasBreathing 3s ease-in-out infinite' : 'none',
        }}
      />

      {/* 2. Secondary ambient glow layer */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.03) 0%, transparent 50%, rgba(59, 130, 246, 0.03) 100%)',
          animation: !prefersReducedMotion ? 'canvasBreathing 4s ease-in-out infinite reverse' : 'none',
        }}
      />

      {/* 3. The Central Core (Focus Point) */}
      <div className="relative z-10 flex flex-col items-center">
        {/* Outer glow ring */}
        <div 
          className="absolute -inset-8 rounded-full opacity-30"
          style={{
            background: 'radial-gradient(circle, rgba(124, 58, 237, 0.4) 0%, transparent 70%)',
            animation: !prefersReducedMotion ? 'canvasBreathing 2s ease-in-out infinite' : 'none',
          }}
        />

        {/* The Spinning Core Ring */}
        <div 
          className="w-16 h-16 rounded-full mb-6 relative"
          style={{
            background: 'transparent',
          }}
        >
          {/* Spinning gradient border */}
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: 'conic-gradient(from 0deg, rgba(124, 58, 237, 0.8), rgba(59, 130, 246, 0.6), rgba(124, 58, 237, 0.2), rgba(124, 58, 237, 0.8))',
              animation: !prefersReducedMotion ? 'spinCore 2s linear infinite' : 'none',
              filter: 'blur(1px)',
            }}
          />
          {/* Inner cutout to create ring effect */}
          <div 
            className="absolute inset-[3px] rounded-full"
            style={{
              background: 'rgba(16, 16, 18, 0.9)',
            }}
          />
          {/* Center dot */}
          <div 
            className="absolute inset-0 flex items-center justify-center"
          >
            <div 
              className="w-2 h-2 rounded-full"
              style={{
                background: 'linear-gradient(135deg, #a78bfa, #60a5fa)',
                boxShadow: '0 0 10px rgba(167, 139, 250, 0.6)',
              }}
            />
          </div>
        </div>

        {/* The Text - Pulsing "ASSEMBLING" */}
        <motion.p 
          className="text-lg font-light tracking-[0.25em] uppercase"
          style={{
            background: 'linear-gradient(135deg, #c4b5fd 0%, #93c5fd 50%, #c4b5fd 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundSize: '200% 100%',
          }}
          animate={!prefersReducedMotion ? {
            opacity: [0.5, 1, 0.5],
            backgroundPosition: ['0% center', '100% center', '0% center'],
          } : {}}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          Assembling
        </motion.p>

        {/* Subtle subtext */}
        <p 
          className="mt-2 text-xs tracking-wider"
          style={{ color: 'rgba(148, 163, 184, 0.6)' }}
        >
          Creating your vision
        </p>
      </div>

      {/* Animation Keyframes */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes canvasBreathing {
            0%, 100% { 
              opacity: 0.4; 
              transform: scale(1); 
            }
            50% { 
              opacity: 0.8; 
              transform: scale(1.05); 
            }
          }
          
          @keyframes spinCore {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `
      }} />
    </div>
  );
});

CanvasGeneratingState.displayName = 'CanvasGeneratingState';
