/**
 * CRT Visual Effects System
 * 
 * Implements authentic CRT monitor visual effects including:
 * - Scanline overlay with CSS animations
 * - Phosphor glow effects and curved screen styling
 * - Realistic CRT noise and flicker effects
 * - Optimized SVG rendering for smooth 60fps performance
 */

export interface CRTEffectsConfig {
  phosphorColor: string;
  scanlineOpacity: number;
  curvature: number;
  glowIntensity: number;
  noiseLevel: number;
  flickerIntensity: number;
  scanlineSpeed: number;
}

export const defaultCRTConfig: CRTEffectsConfig = {
  phosphorColor: '#00ff41', // Classic phosphor green
  scanlineOpacity: 0.1,
  curvature: 0.02,
  glowIntensity: 0.8,
  noiseLevel: 0.05,
  flickerIntensity: 0.02,
  scanlineSpeed: 2, // seconds for full sweep
};

/**
 * Generate CSS styles for CRT effects
 */
export const generateCRTStyles = (config: CRTEffectsConfig = defaultCRTConfig) => {
  return {
    // Main CRT container styles
    crtContainer: {
      position: 'relative' as const,
      background: '#000',
      borderRadius: '8px',
      overflow: 'hidden',
      filter: `
        contrast(1.1) 
        brightness(1.1) 
        saturate(1.2)
        drop-shadow(0 0 ${config.glowIntensity * 20}px ${config.phosphorColor}40)
      `,
      // Curved screen effect
      transform: `perspective(1000px) rotateX(${config.curvature}deg)`,
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
          radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.1) 100%),
          linear-gradient(90deg, transparent 50%, rgba(0,0,0,0.03) 50%, rgba(0,0,0,0.03) 52%, transparent 52%)
        `,
        pointerEvents: 'none',
        zIndex: 10,
      },
    },

    // Phosphor screen surface
    phosphorScreen: {
      position: 'relative' as const,
      width: '100%',
      height: '100%',
      background: '#001100',
      color: config.phosphorColor,
      fontFamily: '"JetBrains Mono", monospace',
      textShadow: `
        0 0 5px ${config.phosphorColor},
        0 0 10px ${config.phosphorColor},
        0 0 15px ${config.phosphorColor}
      `,
      animation: `crt-flicker ${3 + Math.random() * 2}s infinite linear`,
    },

    // Scanline overlay
    scanlines: {
      position: 'absolute' as const,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: `
        repeating-linear-gradient(
          0deg,
          transparent,
          transparent 2px,
          rgba(0, 255, 65, ${config.scanlineOpacity}) 2px,
          rgba(0, 255, 65, ${config.scanlineOpacity}) 4px
        )
      `,
      pointerEvents: 'none',
      zIndex: 5,
      animation: `scanline-sweep ${config.scanlineSpeed}s infinite linear`,
    },

    // CRT noise overlay
    noiseOverlay: {
      position: 'absolute' as const,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      opacity: config.noiseLevel,
      background: `
        repeating-conic-gradient(
          from 0deg,
          transparent 0deg,
          rgba(255, 255, 255, 0.03) 1deg,
          transparent 2deg
        )
      `,
      pointerEvents: 'none',
      zIndex: 3,
      animation: 'crt-noise 0.1s infinite linear',
    },

    // Glow effect for content
    glowContent: {
      filter: `
        drop-shadow(0 0 3px ${config.phosphorColor})
        drop-shadow(0 0 6px ${config.phosphorColor})
        drop-shadow(0 0 9px ${config.phosphorColor})
      `,
    },
  };
};

/**
 * CSS keyframe animations for CRT effects
 */
export const crtKeyframes = `
  @keyframes crt-flicker {
    0% { opacity: 1; }
    98% { opacity: 1; }
    99% { opacity: 0.98; }
    100% { opacity: 1; }
  }

  @keyframes scanline-sweep {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
  }

  @keyframes crt-noise {
    0% { transform: translate(0, 0) rotate(0deg); }
    10% { transform: translate(-1px, -1px) rotate(1deg); }
    20% { transform: translate(1px, 0px) rotate(0deg); }
    30% { transform: translate(0px, 1px) rotate(-1deg); }
    40% { transform: translate(-1px, 0px) rotate(1deg); }
    50% { transform: translate(1px, 1px) rotate(0deg); }
    60% { transform: translate(0px, -1px) rotate(-1deg); }
    70% { transform: translate(-1px, 1px) rotate(1deg); }
    80% { transform: translate(1px, -1px) rotate(0deg); }
    90% { transform: translate(0px, 0px) rotate(-1deg); }
    100% { transform: translate(0px, 0px) rotate(0deg); }
  }

  @keyframes radar-sweep {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  @keyframes phosphor-glow {
    0%, 100% { 
      filter: brightness(1) drop-shadow(0 0 5px currentColor);
    }
    50% { 
      filter: brightness(1.1) drop-shadow(0 0 8px currentColor);
    }
  }
`;

/**
 * SVG filter definitions for CRT effects
 */
export const crtSVGFilters = `
  <defs>
    <!-- Phosphor glow filter -->
    <filter id="phosphor-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge> 
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <!-- CRT curvature filter -->
    <filter id="crt-curve" x="-10%" y="-10%" width="120%" height="120%">
      <feOffset in="SourceGraphic" dx="0" dy="0" result="offset"/>
      <feGaussianBlur in="offset" stdDeviation="0.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <!-- Scanline effect -->
    <filter id="scanlines" x="0%" y="0%" width="100%" height="100%">
      <feFlood flood-color="#00ff41" flood-opacity="0.1"/>
      <feComposite in="SourceGraphic"/>
    </filter>
  </defs>
`;

/**
 * Performance optimization utilities for 60fps rendering
 */
export class CRTPerformanceOptimizer {
  private animationFrame: number | null = null;
  private lastFrameTime = 0;
  private frameCount = 0;
  private fps = 0;

  /**
   * Monitor frame rate and adjust effects if needed
   */
  startPerformanceMonitoring(callback?: (fps: number) => void) {
    const measureFrame = (currentTime: number) => {
      this.frameCount++;
      
      if (currentTime - this.lastFrameTime >= 1000) {
        this.fps = this.frameCount;
        this.frameCount = 0;
        this.lastFrameTime = currentTime;
        
        if (callback) {
          callback(this.fps);
        }
        
        // Auto-adjust effects if FPS drops below 50
        if (this.fps < 50) {
          this.reduceCRTEffects();
        }
      }
      
      this.animationFrame = requestAnimationFrame(measureFrame);
    };
    
    this.animationFrame = requestAnimationFrame(measureFrame);
  }

  /**
   * Stop performance monitoring
   */
  stopPerformanceMonitoring() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }
  }

  /**
   * Reduce CRT effects for better performance
   */
  private reduceCRTEffects() {
    // Reduce scanline opacity
    const scanlineElements = document.querySelectorAll('.crt-scanlines');
    scanlineElements.forEach(el => {
      (el as HTMLElement).style.opacity = '0.05';
    });
    
    // Reduce glow intensity
    const glowElements = document.querySelectorAll('.crt-glow');
    glowElements.forEach(el => {
      (el as HTMLElement).style.filter = 'drop-shadow(0 0 2px currentColor)';
    });
  }

  /**
   * Get current FPS
   */
  getCurrentFPS(): number {
    return this.fps;
  }
}

/**
 * Utility function to inject CRT styles into document
 */
export const injectCRTStyles = () => {
  const styleId = 'crt-effects-styles';
  
  // Remove existing styles if present
  const existingStyle = document.getElementById(styleId);
  if (existingStyle) {
    existingStyle.remove();
  }
  
  // Create and inject new styles
  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = crtKeyframes;
  document.head.appendChild(style);
};

export default {
  generateCRTStyles,
  crtKeyframes,
  crtSVGFilters,
  CRTPerformanceOptimizer,
  injectCRTStyles,
  defaultCRTConfig,
};