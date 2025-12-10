/**
 * Property-Based Test: Neumorphic Shadow Consistency
 * 
 * **Feature: industrial-design-system, Property 1: Neumorphic shadow consistency**
 * **Validates: Requirements 1.1, 1.2**
 * 
 * Tests that all neumorphic shadows follow the exact dual-shadow pattern
 * with correct colors and positioning for unidirectional illumination compliance.
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { NeumorphicUtils, ShadowVariant, ShadowType } from '../neumorphic';
import { tokenUtils } from '../tokens';

describe('Property Test: Neumorphic Shadow Consistency', () => {
  /**
   * Property 1: Neumorphic shadow consistency
   * For any component using neumorphic styling, the rendered CSS should contain 
   * dual shadows with the exact pattern for raised/recessed surfaces
   */
  it('should maintain dual shadow pattern with correct colors for all variants and types', () => {
    fc.assert(
      fc.property(
        // Generate all valid combinations of shadow variants and types
        fc.constantFrom('subtle', 'normal', 'deep' as const),
        fc.constantFrom('raised', 'recessed' as const),
        (variant: ShadowVariant, type: ShadowType) => {
          // Get the shadow CSS from the token system
          const shadowCSS = tokenUtils.getShadow(variant, type);
          
          // Validate the shadow follows the dual-shadow pattern
          const isValidPattern = validateDualShadowPattern(shadowCSS, type);
          
          // Validate colors are correct
          const hasCorrectColors = validateShadowColors(shadowCSS);
          
          // Validate positioning follows unidirectional illumination
          const hasCorrectPositioning = validateShadowPositioning(shadowCSS, type);
          
          return isValidPattern && hasCorrectColors && hasCorrectPositioning;
        }
      ),
      { numRuns: 100 } // Run 100 iterations as specified in design document
    );
  });

  /**
   * Property test for NeumorphicUtils shadow class generation
   */
  it('should generate consistent CSS class names for all shadow variants', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('subtle', 'normal', 'deep' as const),
        fc.constantFrom('raised', 'recessed' as const),
        (variant: ShadowVariant, type: ShadowType) => {
          const className = NeumorphicUtils.getShadowClass(variant, type);
          
          // Validate class name format
          const expectedPattern = `shadow-neumorphic-${type}-${variant}`;
          return className === expectedPattern;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property test for inline shadow styles
   */
  it('should generate consistent inline shadow styles for all variants', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('subtle', 'normal', 'deep' as const),
        fc.constantFrom('raised', 'recessed' as const),
        (variant: ShadowVariant, type: ShadowType) => {
          const style = NeumorphicUtils.getShadowStyle(variant, type);
          
          // Validate style object has boxShadow property
          const hasBoxShadow = 'boxShadow' in style && typeof style.boxShadow === 'string';
          
          if (!hasBoxShadow) return false;
          
          // Validate the boxShadow follows the pattern
          const shadowCSS = style.boxShadow as string;
          return validateDualShadowPattern(shadowCSS, type) && 
                 validateShadowColors(shadowCSS) &&
                 validateShadowPositioning(shadowCSS, type);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property test for shadow pattern validation utility
   */
  it('should correctly validate shadow patterns using NeumorphicUtils.validateShadowPattern', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('subtle', 'normal', 'deep' as const),
        fc.constantFrom('raised', 'recessed' as const),
        (variant: ShadowVariant, type: ShadowType) => {
          const shadowCSS = tokenUtils.getShadow(variant, type);
          
          // All valid neumorphic shadows should pass validation
          return NeumorphicUtils.validateShadowPattern(shadowCSS);
        }
      ),
      { numRuns: 100 }
    );
  });
});

/**
 * Helper function to validate dual shadow pattern
 */
function validateDualShadowPattern(shadowCSS: string, type: ShadowType): boolean {
  // Remove any whitespace and split by comma
  const shadowParts = shadowCSS.split(',').map(s => s.trim());
  
  // Must have exactly 2 shadow parts (dual shadow)
  if (shadowParts.length !== 2) return false;
  
  // For recessed shadows, both parts should start with 'inset'
  if (type === 'recessed') {
    return shadowParts.every(part => part.startsWith('inset'));
  }
  
  // For raised shadows, neither part should have 'inset'
  return shadowParts.every(part => !part.includes('inset'));
}

/**
 * Helper function to validate shadow colors
 */
function validateShadowColors(shadowCSS: string): boolean {
  // Must contain both the dark shadow color (#babecc) and light shadow color (#ffffff)
  const hasDarkShadow = shadowCSS.includes('#babecc');
  const hasLightShadow = shadowCSS.includes('#ffffff');
  
  return hasDarkShadow && hasLightShadow;
}

/**
 * Helper function to validate shadow positioning for unidirectional illumination
 */
function validateShadowPositioning(shadowCSS: string, type: ShadowType): boolean {
  // Extract shadow parts
  const shadowParts = shadowCSS.split(',').map(s => s.trim());
  
  for (const part of shadowParts) {
    // Remove 'inset' if present to get the positioning values
    const cleanPart = part.replace(/^inset\s+/, '');
    
    // Extract the positioning values (x, y, blur, color)
    const values = cleanPart.split(/\s+/);
    
    if (values.length < 4) return false;
    
    const xOffset = parseInt(values[0]);
    const yOffset = parseInt(values[1]);
    const blurRadius = parseInt(values[2]);
    
    // Validate that blur radius is positive
    if (blurRadius <= 0) return false;
    
    // For unidirectional illumination, shadows should follow the light source pattern
    // Light source is from top-left (-1, -1), creating consistent shadow directions
    
    // Based on the actual shadow values:
    // Raised: dark shadow (4px 4px) = bottom-right, light shadow (-4px -4px) = top-left
    // Recessed: dark shadow (4px 4px) = bottom-right, light shadow (-4px -4px) = top-left
    // The inset keyword changes the visual effect but not the offset directions
    
    if (part.includes('#babecc')) {
      // Dark shadow should always be bottom-right (positive offsets)
      if (xOffset <= 0 || yOffset <= 0) return false;
    }
    
    if (part.includes('#ffffff')) {
      // Light shadow should always be top-left (negative offsets)
      if (xOffset >= 0 || yOffset >= 0) return false;
    }
  }
  
  return true;
}