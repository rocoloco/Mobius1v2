/**
 * BentoGrid Layout Component
 * 
 * Implements a CSS Grid layout dividing the dashboard into five distinct zones:
 * - Director (top-left, 2 rows)
 * - Context Deck (bottom-left, 1 row)
 * - Canvas (center, 3 rows)
 * - Compliance Gauge (top-right, 1 row)
 * - Twin Data (bottom-right, 2 rows)
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
  context: React.ReactNode;
  twin: React.ReactNode;
}

export function BentoGrid({
  director,
  canvas,
  gauge,
  context,
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
      {/* Director Zone - Top-left, spans 2 rows */}
      <motion.div
        className="overflow-hidden zone-director"
        data-testid="zone-director"
        layout
        transition={layoutTransition}
      >
        {director}
      </motion.div>

      {/* Canvas Zone - Center, spans 3 rows */}
      <motion.div
        className="overflow-hidden zone-canvas"
        data-testid="zone-canvas"
        layout
        transition={layoutTransition}
      >
        {canvas}
      </motion.div>

      {/* Compliance Gauge Zone - Top-right, spans 1 row */}
      <motion.div
        className="zone-gauge"
        data-testid="zone-gauge"
        layout
        transition={layoutTransition}
      >
        {gauge}
      </motion.div>

      {/* Context Deck Zone - Bottom-left, spans 1 row */}
      <motion.div
        className="zone-context"
        data-testid="zone-context"
        layout
        transition={layoutTransition}
      >
        {context}
      </motion.div>

      {/* Twin Data Zone - Bottom-right, spans 2 rows */}
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
            grid-template-columns: 1fr 1.5fr 1fr;
            grid-template-rows: 1fr 1fr 1.4fr;
            grid-template-areas:
              "director canvas gauge"
              "director canvas twin"
              "context canvas twin";
          }
          
          .zone-director { grid-area: director; min-height: 0; }
          .zone-canvas { grid-area: canvas; min-height: 0; }
          .zone-gauge { grid-area: gauge; min-height: 0; }
          .zone-context { grid-area: context; min-height: 0; }
          .zone-twin { grid-area: twin; min-height: 0; }
          
          @media (max-width: 767px) {
            .bento-grid {
              grid-template-columns: 1fr;
              grid-template-rows: auto;
              grid-template-areas:
                "director"
                "canvas"
                "gauge"
                "twin"
                "context";
              padding: 16px !important;
              gap: 16px !important;
            }
            
            .zone-director { height: 40vh; min-height: 300px; }
            .zone-canvas { min-height: 500px; }
            .zone-gauge { min-height: 400px; }
            .zone-twin { min-height: 400px; }
            .zone-context { min-height: 300px; }
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
