/**
 * BentoGrid Layout Component
 * 
 * Implements a CSS Grid layout dividing the dashboard into four distinct zones:
 * - Director (left column, full height) - includes Brand Graph context
 * - Canvas (center, full height) - expanded to use former Context Deck space
 * - Compliance Gauge (top-right)
 * - Twin Data (bottom-right)
 * 
 * Responsive: Collapses to single column on mobile (<768px)
 * 
 * Requirements: 3.1-3.9
 */

import React from 'react';
import { motion } from 'framer-motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface BentoGridProps {
  director: React.ReactNode;
  canvas: React.ReactNode;
  gauge: React.ReactNode;
  twin: React.ReactNode;
  /** @deprecated Context Deck merged into Director - kept for backwards compatibility */
  context?: React.ReactNode;
}

export function BentoGrid({
  director,
  canvas,
  gauge,
  twin,
}: BentoGridProps) {
  const prefersReducedMotion = useReducedMotion();

  const layoutTransition = {
    duration: prefersReducedMotion ? 0 : 0.3,
    ease: "easeInOut" as const
  };

  return (
    <motion.div
      className="bento-grid grid"
      style={{ padding: '24px 32px 32px 32px', gap: '24px' }}
      data-testid="bento-grid"
      layout
      transition={layoutTransition}
    >
      {/* Director Zone - Left column, full height */}
      <motion.div
        className="overflow-hidden zone-director"
        data-testid="zone-director"
        layout
        transition={layoutTransition}
      >
        {director}
      </motion.div>

      {/* Canvas Zone - Center, full height (expanded) */}
      <motion.div
        className="overflow-hidden zone-canvas"
        data-testid="zone-canvas"
        layout
        transition={layoutTransition}
      >
        {canvas}
      </motion.div>

      {/* Compliance Gauge Zone - Top-right */}
      <motion.div
        className="zone-gauge"
        data-testid="zone-gauge"
        layout
        transition={layoutTransition}
      >
        {gauge}
      </motion.div>

      {/* Twin Data Zone - Bottom-right */}
      <motion.div
        className="zone-twin"
        data-testid="zone-twin"
        layout
        transition={layoutTransition}
      >
        {twin}
      </motion.div>

      {/* Inline styles for grid template areas */}
      <style dangerouslySetInnerHTML={{
        __html: `
          .bento-grid {
            height: 100%;
            box-sizing: border-box;
            grid-template-columns: 1fr 1.8fr 1fr;
            grid-template-rows: 1fr 1.2fr;
            grid-template-areas:
              "director canvas gauge"
              "director canvas twin";
          }
          
          .zone-director { grid-area: director; min-height: 0; }
          .zone-canvas { grid-area: canvas; min-height: 0; }
          .zone-gauge { grid-area: gauge; min-height: 0; }
          .zone-twin { grid-area: twin; min-height: 0; }
          
          @media (max-width: 767px) {
            .bento-grid {
              grid-template-columns: 1fr;
              grid-template-rows: auto;
              grid-template-areas:
                "director"
                "canvas"
                "gauge"
                "twin";
              padding: 16px !important;
              gap: 16px !important;
            }
            
            .zone-director { height: 45vh; min-height: 350px; }
            .zone-canvas { min-height: 500px; }
            .zone-gauge { min-height: 400px; }
            .zone-twin { min-height: 400px; }
          }
          
          @media (min-width: 768px) and (max-width: 1023px) {
            .bento-grid {
              padding: 20px !important;
              gap: 20px !important;
            }
          }
        `
      }} />
    </motion.div>
  );
}
