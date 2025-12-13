/**
 * Property-Based Test: GlassPanel Glow Effect
 * 
 * **Feature: luminous-dashboard-v2, Property 1 (Partial): GlassPanel applies glow when prop is true**
 * **Validates: Requirements 1.12, 12.3**
 * 
 * Tests that the GlassPanel component correctly applies the glow effect
 * when the glow prop is true, and does not apply it when false.
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { render } from '@testing-library/react';
import { GlassPanel } from '../GlassPanel';
import { luminousTokens } from '../../../tokens';

describe('Property Test: GlassPanel Glow Effect', () => {
  /**
   * Property 1 (Partial): GlassPanel applies glow when prop is true
   * For any glow prop value (true or false), the GlassPanel should correctly
   * apply or omit the glow box-shadow effect.
   */
  it('should apply glow effect when glow prop is true and omit it when false', () => {
    fc.assert(
      fc.property(
        fc.boolean(),
        fc.string({ minLength: 1, maxLength: 50 }), // Generate random content
        (glowProp: boolean, content: string) => {
          // Render the GlassPanel with the generated glow prop
          const { container } = render(
            <GlassPanel glow={glowProp}>
              {content}
            </GlassPanel>
          );
          
          // Get the rendered div element
          const panelElement = container.firstChild as HTMLElement;
          
          // Get the computed style
          const computedStyle = window.getComputedStyle(panelElement);
          const boxShadow = computedStyle.boxShadow;
          
          // When glow is true, box-shadow should match the glow token
          // When glow is false, box-shadow should be 'none' or empty
          if (glowProp) {
            // The element should have the glow box-shadow applied
            // Note: The actual computed value might differ slightly from the token
            // due to browser rendering, so we check if it's not 'none'
            expect(boxShadow).not.toBe('none');
            expect(boxShadow).not.toBe('');
            
            // Verify the inline style contains the glow effect
            const inlineStyle = panelElement.style.boxShadow;
            expect(inlineStyle).toBe(luminousTokens.effects.glow);
          } else {
            // When glow is false, should have depth shadows instead
            // The enhanced glassmorphism always has some shadow for depth
            const inlineStyle = panelElement.style.boxShadow;
            expect(inlineStyle).toContain('rgba(0, 0, 0, 0.3)'); // Contains depth shadow
            expect(inlineStyle).not.toBe('none');
          }
          
          // Verify the content is rendered
          expect(panelElement.textContent).toBe(content);
          
          // Verify glassmorphism classes are always present
          // Note: bg-white/5 is now applied via inline background style, not class
          expect(panelElement.className).toContain('backdrop-blur-md');
          expect(panelElement.className).toContain('border');
          expect(panelElement.className).toContain('border-white/10');
          expect(panelElement.className).toContain('rounded-2xl');
          
          // Verify background is set via inline style
          expect(panelElement.style.background).toBeTruthy();
          
          return true;
        }
      ),
      { numRuns: 100 } // Run 100 iterations as specified in design document
    );
  });

  /**
   * Additional property test: GlassPanel preserves custom className
   * For any custom className provided, it should be applied alongside the base classes
   */
  it('should preserve custom className while maintaining glassmorphism styling', () => {
    fc.assert(
      fc.property(
        fc.boolean(),
        fc.string({ minLength: 1, maxLength: 30 }).filter(s => !s.includes(' ')), // Single class name
        (glowProp: boolean, customClass: string) => {
          const { container } = render(
            <GlassPanel glow={glowProp} className={customClass}>
              Test Content
            </GlassPanel>
          );
          
          const panelElement = container.firstChild as HTMLElement;
          
          // Custom class should be present
          expect(panelElement.className).toContain(customClass);
          
          // Base glassmorphism classes should still be present
          // Note: bg-white/5 is now applied via inline background style
          expect(panelElement.className).toContain('backdrop-blur-md');
          
          // Verify background is set via inline style
          expect(panelElement.style.background).toBeTruthy();
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});
