/**
 * Design System Test Utilities
 * 
 * Utilities for testing the industrial design system components
 */

import { NeumorphicUtils } from './neumorphic';
import { industrialTokens } from './tokens';

/**
 * Test utilities for validating design system compliance
 */
export class DesignSystemTestUtils {
  /**
   * Validate that a shadow follows neumorphic pattern
   */
  static validateNeumorphicShadow(shadowCSS: string): boolean {
    return NeumorphicUtils.validateShadowPattern(shadowCSS);
  }

  /**
   * Test shadow depth scaling
   */
  static testShadowDepthScaling(): boolean {
    const subtleShadow = industrialTokens.shadows.neumorphic.raised.subtle;
    const normalShadow = industrialTokens.shadows.neumorphic.raised.normal;
    const deepShadow = industrialTokens.shadows.neumorphic.raised.deep;

    // All should be valid neumorphic patterns
    return [subtleShadow, normalShadow, deepShadow].every(shadow => 
      this.validateNeumorphicShadow(shadow)
    );
  }

  /**
   * Test LED color coding compliance
   */
  static testLEDColorCoding(): boolean {
    const colors = industrialTokens.colors.led;
    
    // Verify industrial standard colors
    const expectedColors = {
      error: '#e17055',
      on: '#00b894', 
      warning: '#fdcb6e',
      off: '#74b9ff'
    };

    return Object.entries(expectedColors).every(([status, expectedColor]) => 
      colors[status as keyof typeof colors] === expectedColor
    );
  }

  /**
   * Test mechanical easing function
   */
  static testMechanicalEasing(): boolean {
    const easing = industrialTokens.animations.mechanical.easing;
    return easing === 'cubic-bezier(0.34, 1.56, 0.64, 1)';
  }

  /**
   * Run all design system validation tests
   */
  static runAllTests(): { passed: boolean; results: Record<string, boolean> } {
    const results = {
      shadowDepthScaling: this.testShadowDepthScaling(),
      ledColorCoding: this.testLEDColorCoding(),
      mechanicalEasing: this.testMechanicalEasing(),
    };

    const passed = Object.values(results).every(result => result);

    return { passed, results };
  }
}

export default DesignSystemTestUtils;