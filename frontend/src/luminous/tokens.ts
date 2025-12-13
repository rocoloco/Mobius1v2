/**
 * Luminous Structuralism Design Tokens
 * 
 * Centralized design token system for the Luminous dashboard.
 * Defines colors, typography, effects, and animations following the
 * "Luminous Structuralism" design philosophy.
 */

export const luminousTokens = {
  colors: {
    // Background
    void: '#101012', // Deep Charcoal
    
    // Surfaces
    glass: 'rgba(255, 255, 255, 0.03)', // Translucent glass surface
    border: 'rgba(255, 255, 255, 0.08)', // Subtle borders
    
    // Accent colors
    accent: {
      gradient: 'linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)',
      purple: '#7C3AED',
      blue: '#2563EB',
    },
    
    // Compliance colors
    compliance: {
      pass: '#10B981',      // Neon Mint - scores ≥95%
      review: '#F59E0B',    // Amber - scores 70-95%
      critical: '#EF4444',  // Desaturated Red - scores <70%
    },
    
    // Text colors
    text: {
      body: '#94A3B8',      // Slate-400 - body text
      high: '#F1F5F9',      // High contrast text
      muted: '#8B8B8B',     // Custom muted text (WCAG AA compliant)
    },
  },
  
  typography: {
    fontFamily: {
      sans: '"Inter", "Geist Sans", system-ui, sans-serif',
      mono: '"JetBrains Mono", "Fira Code", monospace',
    },
    tracking: {
      tight: '-0.02em',
      normal: '0',
    },
  },
  
  effects: {
    // Enhanced multi-layer glow system
    glow: '0 0 20px rgba(37, 99, 235, 0.15), 0 0 40px rgba(37, 99, 235, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    glowStrong: '0 0 30px rgba(37, 99, 235, 0.3), 0 0 60px rgba(37, 99, 235, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15)',
    glowPurple: '0 0 20px rgba(124, 58, 237, 0.2), 0 0 40px rgba(124, 58, 237, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    
    // Backdrop blur with multiple layers
    backdropBlur: 'blur(12px)',
    backdropBlurStrong: 'blur(20px)',
    
    // Glass surface effects
    glassSurface: 'inset 0 1px 1px rgba(255, 255, 255, 0.1), inset 0 -1px 1px rgba(0, 0, 0, 0.1)',
    glassDepth: '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)',
    
    // Border glow effects
    borderGlow: '0 0 10px rgba(255, 255, 255, 0.1)',
    borderGlowAccent: '0 0 15px rgba(37, 99, 235, 0.3)',
  },
  
  animation: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
    easing: {
      smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
  },
} as const;

/**
 * Utility function to get compliance color based on score
 * @param score - Compliance score (0-100)
 * @returns Hex color string
 */
export function getComplianceColor(score: number): string {
  if (score >= 95) return luminousTokens.colors.compliance.pass;
  if (score >= 70) return luminousTokens.colors.compliance.review;
  return luminousTokens.colors.compliance.critical;
}

/**
 * Utility function to get connection status color
 * @param status - Connection status
 * @returns Tailwind color class
 */
export function getConnectionColor(status: 'connected' | 'disconnected' | 'connecting'): string {
  switch (status) {
    case 'connected':
      return 'bg-green-500';
    case 'disconnected':
      return 'bg-red-500';
    case 'connecting':
      return 'bg-yellow-500';
  }
}

/**
 * Type definitions for design tokens
 */
export type LuminousTokens = typeof luminousTokens;
export type ComplianceColor = keyof typeof luminousTokens.colors.compliance;
export type TextColor = keyof typeof luminousTokens.colors.text;
