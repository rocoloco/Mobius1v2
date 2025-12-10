/**
 * Mechanical Easing Functions and Animation Timing System
 * 
 * Provides realistic mechanical motion patterns for industrial interfaces
 */

import { industrialTokens } from './tokens';

/**
 * Mechanical easing presets
 */
export const mechanicalEasing = {
  // Primary mechanical easing with subtle bounce
  mechanical: industrialTokens.animations.mechanical.easing,
  
  // Variations for different mechanical behaviors
  spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  dampened: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  heavy: 'cubic-bezier(0.55, 0.085, 0.68, 0.53)',
  light: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  
  // Press-specific easing
  press: 'cubic-bezier(0.4, 0, 0.2, 1)',
  release: 'cubic-bezier(0.0, 0, 0.2, 1)',
} as const;

/**
 * Animation duration system
 */
export const animationDurations = {
  ...industrialTokens.animations.mechanical.duration,
  
  // Specialized durations
  press: industrialTokens.animations.press.duration,
  hover: '200ms',
  focus: '150ms',
  
  // Complex animations
  stateChange: '300ms',
  pageTransition: '500ms',
} as const;

/**
 * Animation utility class
 */
export class AnimationUtils {
  /**
   * Generate CSS transition string
   */
  static createTransition(
    properties: string[] = ['all'],
    duration: keyof typeof animationDurations = 'normal',
    easing: keyof typeof mechanicalEasing = 'mechanical'
  ): string {
    const durationValue = animationDurations[duration];
    const easingValue = mechanicalEasing[easing];
    
    return properties
      .map(prop => `${prop} ${durationValue} ${easingValue}`)
      .join(', ');
  }

  /**
   * Generate keyframe animation CSS
   */
  static createKeyframeAnimation(
    name: string,
    duration: keyof typeof animationDurations = 'normal',
    easing: keyof typeof mechanicalEasing = 'mechanical',
    fillMode: 'forwards' | 'backwards' | 'both' | 'none' = 'forwards'
  ): string {
    return `${name} ${animationDurations[duration]} ${mechanicalEasing[easing]} ${fillMode}`;
  }

  /**
   * Generate press animation styles
   */
  static getPressAnimation(): {
    transition: string;
    transformOrigin: string;
  } {
    return {
      transition: AnimationUtils.createTransition(['transform', 'box-shadow'], 'press', 'press'),
      transformOrigin: 'center center',
    };
  }

  /**
   * Generate hover animation styles
   */
  static getHoverAnimation(): {
    transition: string;
  } {
    return {
      transition: AnimationUtils.createTransition(['transform', 'box-shadow'], 'hover', 'light'),
    };
  }

  /**
   * Generate LED pulse animation
   */
  static getLEDPulseAnimation(duration: number = 2000): React.CSSProperties {
    return {
      animation: `ledPulse ${duration}ms ${mechanicalEasing.dampened} infinite`,
    };
  }

  /**
   * Validate animation timing
   * Ensures animations feel mechanical and realistic
   */
  static validateAnimationTiming(duration: number): boolean {
    // Mechanical animations should be between 100ms and 1000ms for good UX
    return duration >= 100 && duration <= 1000;
  }
}

/**
 * CSS Keyframes for mechanical animations
 */
export const mechanicalKeyframes = `
  @keyframes mechanicalPress {
    0% {
      transform: translateY(0);
    }
    100% {
      transform: translateY(2px);
    }
  }

  @keyframes mechanicalRelease {
    0% {
      transform: translateY(2px);
    }
    100% {
      transform: translateY(0);
    }
  }

  @keyframes ledPulse {
    0%, 100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.7;
      transform: scale(0.95);
    }
  }

  @keyframes mechanicalSlideIn {
    0% {
      opacity: 0;
      transform: translateY(20px);
    }
    100% {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes mechanicalFadeIn {
    0% {
      opacity: 0;
    }
    100% {
      opacity: 1;
    }
  }

  @keyframes screwRotate {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

/**
 * React hook for mechanical animations
 */
export const useMechanicalAnimation = (
  trigger: boolean,
  animationType: 'press' | 'hover' | 'focus' = 'press'
) => {
  const [isAnimating, setIsAnimating] = React.useState(false);

  React.useEffect(() => {
    if (trigger) {
      setIsAnimating(true);
      const duration = animationType === 'press' ? 100 : 200;
      
      const timer = setTimeout(() => {
        setIsAnimating(false);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [trigger, animationType]);

  const getAnimationStyle = (): React.CSSProperties => {
    switch (animationType) {
      case 'press':
        return AnimationUtils.getPressAnimation();
      case 'hover':
        return AnimationUtils.getHoverAnimation();
      default:
        return {};
    }
  };

  return {
    isAnimating,
    style: getAnimationStyle(),
  };
};

// Import React for hooks
import React from 'react';

export default AnimationUtils;