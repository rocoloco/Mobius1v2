import { Sparkles, Command } from 'lucide-react';
import { MonoText } from '../atoms/MonoText';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

/**
 * CanvasEmptyState - The "Zero Point" idle state for Canvas
 * 
 * Transforms the empty canvas from a boring placeholder into a 
 * "charged" state that feels like a high-end camera viewfinder
 * or fighter jet HUD awaiting command.
 * 
 * Features:
 * - Architectural dot grid background (precision/alignment)
 * - Breathing reticle centerpiece (system alive/listening)
 * - HUD-style corner brackets
 * - Technical status typography
 */
export function CanvasEmptyState() {
  const prefersReducedMotion = useReducedMotion();
  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center overflow-hidden">
      {/* 1. The Architectural Grid (Background) */}
      {/* Creates a precise dot grid that fades out at the edges */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.05) 1px, transparent 0)',
          backgroundSize: '24px 24px',
          maskImage: 'radial-gradient(ellipse at center, black 40%, transparent 80%)',
          WebkitMaskImage: 'radial-gradient(ellipse at center, black 40%, transparent 80%)'
        }}
      />

      {/* 2. The Breathing Reticle (Centerpiece) */}
      <div className="relative z-10 group cursor-default">
        {/* Outer Glow Ring */}
        <div 
          className="absolute inset-0 bg-purple-500/20 rounded-full blur-xl"
          style={{ animation: !prefersReducedMotion ? 'pulse-slow 3s ease-in-out infinite' : 'none' }}
        />
        
        {/* The Glass Container */}
        <div className="relative w-24 h-24 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-md flex items-center justify-center shadow-[inset_0_1px_0_0_rgba(255,255,255,0.2)] group-hover:border-purple-500/50 group-hover:shadow-[0_0_30px_rgba(124,58,237,0.3)] transition-all duration-500">
          <Sparkles
            className="w-10 h-10 text-white/50 group-hover:text-purple-400 transition-colors duration-500"
            strokeWidth={1.5}
          />
        </div>
        
        {/* Corner Brackets (The "HUD" feel) */}
        {/* Top Left */}
        <div className="absolute -top-4 -left-4 w-4 h-4 border-t border-l border-white/20 rounded-tl-lg group-hover:border-purple-500/50 transition-colors duration-300" />
        {/* Top Right */}
        <div className="absolute -top-4 -right-4 w-4 h-4 border-t border-r border-white/20 rounded-tr-lg group-hover:border-purple-500/50 transition-colors duration-300" />
        {/* Bottom Left */}
        <div className="absolute -bottom-4 -left-4 w-4 h-4 border-b border-l border-white/20 rounded-bl-lg group-hover:border-purple-500/50 transition-colors duration-300" />
        {/* Bottom Right */}
        <div className="absolute -bottom-4 -right-4 w-4 h-4 border-b border-r border-white/20 rounded-br-lg group-hover:border-purple-500/50 transition-colors duration-300" />
      </div>

      {/* 3. System Status Text */}
      <div className="mt-8 text-center space-y-2 relative z-10">
        <h2 className="text-xl font-medium text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60">
          Ready to Generate
        </h2>
        <div className="flex items-center gap-2 justify-center text-xs text-slate-500">
          <MonoText className="text-purple-400/80">SYSTEM_IDLE</MonoText>
          <span className="w-1 h-1 rounded-full bg-slate-600" />
          <span className="flex items-center gap-1.5">
            Press{' '}
            <kbd className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10 font-sans text-[10px] text-slate-400 flex items-center">
              <Command className="w-2.5 h-2.5 mr-0.5"/>K
            </kbd>{' '}
            for templates
          </span>
        </div>
      </div>

      {/* Animation Keyframes */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes pulse-slow {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.1); }
          }
        `
      }} />
    </div>
  );
}
