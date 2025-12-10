/**
 * Property-Based Test: Shadow Depth Pattern Preservation
 * 
 * **Feature: industrial-design-system, Property 2: Shadow depth pattern preservation**
 * **Validates: Requirements 1.3**
 * 
 * Tests that shadow depth variants maintain dual-shadow structure with proportional
 * scaling while preserving the #babecc and #ffffff color scheme.
 */

import { describe, it } from 'vitest';
import * as fc from 'fast-check';
import { tokenUtils } from '../tokens';
import type { ShadowVariant, ShadowType } from '../neumorphic';

describe('Property Test: Shadow Depth Pattern Preservation', () => {
  /**
   * Property 2: Shadow depth pattern preservation
   * For any shadow depth variant (subtle, normal, deep), the dual-shadow structure 
   * should be maintained with proportional scaling of shadow distances while 
   * preserving the #babecc and #ffffff color scheme
   */
  it('should maintain dual shadow structure with proportional scaling across all depth variants', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('raised', 'recessed' as const),
        (type: ShadowType) => {
          // Get all three depth variants for the given type
          const subtleShadow = tokenUtils.getShadow('subtle', type);
          const normalShadow = tokenUtils.getShadow('normal', type);
          const deepShadow = tokenUtils.getShadow('deep', type);
          
          // Extract shadow measurements for each variant
          const subtleMetrics = extractShadowMetrics(subtleShadow);
          const normalMetrics = extractShadowMetrics(normalShadow);
          const deepMetrics = extractShadowMetrics(deepShadow);
          
          // Validate all variants maintain dual shadow structure
          const allHaveDualShadows = [subtleMetrics, normalMetrics, deepMetrics]
            .every(metrics => metrics.shadowCount === 2);
          
          // Validate proportional scaling relationships
          const hasProportionalScaling = validateProportionalScaling(
            subtleMetrics, normalMetrics, deepMetrics
          );
          
          // Validate color scheme preservation
          const preservesColorScheme = [subtleShadow, normalShadow, deepShadow]
            .every(shadow => validateColorScheme(shadow));
          
          return allHaveDualShadows && hasProportionalScaling && preservesColorScheme;
        }
      ),
      { numRuns: 100 }
    );
  });
});

/**
 * Interface for shadow metrics extracted from CSS
 */
interface ShadowMetrics {
  shadowCount: number;
  darkShadow: {
    xOffset: number;
    yOffset: number;
    blurRadius: number;
  };
  lightShadow: {
    xOffset: number;
    yOffset: number;
    blurRadius: number;
  };
}

/**
 * Extract shadow measurements from CSS shadow string
 */
function extractShadowMetrics(shadowCSS: string): ShadowMetrics {
  const shadowParts = shadowCSS.split(',').map(s => s.trim());
  
  const metrics: ShadowMetrics = {
    shadowCount: shadowParts.length,
    darkShadow: { xOffset: 0, yOffset: 0, blurRadius: 0 },
    lightShadow: { xOffset: 0, yOffset: 0, blurRadius: 0 }
  };
  
  shadowParts.forEach(part => {
    // Remove 'inset' if present
    const cleanPart = part.replace(/^inset\s+/, '');
    const values = cleanPart.split(/\s+/);
    
    if (values.length >= 4) {
      const xOffset = parseInt(values[0]);
      const yOffset = parseInt(values[1]);
      const blurRadius = parseInt(values[2]);
      
      // Identify dark vs light shadow by color
      if (part.includes('#babecc')) {
        metrics.darkShadow = { xOffset, yOffset, blurRadius };
      } else if (part.includes('#ffffff')) {
        metrics.lightShadow = { xOffset, yOffset, blurRadius };
      }
    }
  });
  
  return metrics;
}

/**
 * Validate proportional scaling between shadow variants
 */
function validateProportionalScaling(
  subtle: ShadowMetrics, 
  normal: ShadowMetrics, 
  deep: ShadowMetrics
): boolean {
  // Expected scaling ratios based on design tokens (0.5, 1.0, 1.5)
  const expectedSubtleRatio = 0.5;
  const expectedDeepRatio = 1.5;
  
  // Check dark shadow scaling
  const darkSubtleRatio = Math.abs(subtle.darkShadow.xOffset) / Math.abs(normal.darkShadow.xOffset);
  const darkDeepRatio = Math.abs(deep.darkShadow.xOffset) / Math.abs(normal.darkShadow.xOffset);
  
  // Check light shadow scaling  
  const lightSubtleRatio = Math.abs(subtle.lightShadow.xOffset) / Math.abs(normal.lightShadow.xOffset);
  const lightDeepRatio = Math.abs(deep.lightShadow.xOffset) / Math.abs(normal.lightShadow.xOffset);
  
  // Check blur radius scaling
  const blurSubtleRatio = subtle.darkShadow.blurRadius / normal.darkShadow.blurRadius;
  const blurDeepRatio = deep.darkShadow.blurRadius / normal.darkShadow.blurRadius;
  
  // Allow small tolerance for floating point calculations
  const tolerance = 0.01;
  
  return Math.abs(darkSubtleRatio - expectedSubtleRatio) < tolerance &&
         Math.abs(darkDeepRatio - expectedDeepRatio) < tolerance &&
         Math.abs(lightSubtleRatio - expectedSubtleRatio) < tolerance &&
         Math.abs(lightDeepRatio - expectedDeepRatio) < tolerance &&
         Math.abs(blurSubtleRatio - expectedSubtleRatio) < tolerance &&
         Math.abs(blurDeepRatio - expectedDeepRatio) < tolerance;
}

/**
 * Validate that shadow maintains correct color scheme
 */
function validateColorScheme(shadowCSS: string): boolean {
  // Must contain both required colors
  const hasDarkColor = shadowCSS.includes('#babecc');
  const hasLightColor = shadowCSS.includes('#ffffff');
  
  // Must not contain any other colors
  const colorMatches = shadowCSS.match(/#[0-9a-fA-F]{6}/g) || [];
  const onlyValidColors = colorMatches.every(color => 
    color.toLowerCase() === '#babecc' || color.toLowerCase() === '#ffffff'
  );
  
  return hasDarkColor && hasLightColor && onlyValidColors;
}