/**
 * Foundation Layer Tests
 * 
 * Tests for the Industrial Design System foundation layer
 */

import { describe, it, expect } from 'vitest';
import { DesignSystemTestUtils } from '../test-utils';
import { industrialTokens, tokenUtils } from '../tokens';
import { NeumorphicUtils } from '../neumorphic';
import { AnimationUtils, mechanicalEasing } from '../animations';

describe('Industrial Design System - Foundation Layer', () => {
  describe('Design Tokens', () => {
    it('should have all required color tokens', () => {
      expect(industrialTokens.colors.surface.primary).toBe('#e0e5ec');
      expect(industrialTokens.colors.shadows.light).toBe('#ffffff');
      expect(industrialTokens.colors.shadows.dark).toBe('#babecc');
    });

    it('should have LED color coding compliance', () => {
      expect(DesignSystemTestUtils.testLEDColorCoding()).toBe(true);
    });

    it('should have mechanical easing function', () => {
      expect(DesignSystemTestUtils.testMechanicalEasing()).toBe(true);
    });
  });

  describe('Neumorphic Shadows', () => {
    it('should generate valid neumorphic shadows', () => {
      const raisedShadow = tokenUtils.getShadow('normal', 'raised');
      const recessedShadow = tokenUtils.getShadow('normal', 'recessed');
      
      expect(NeumorphicUtils.validateShadowPattern(raisedShadow)).toBe(true);
      expect(NeumorphicUtils.validateShadowPattern(recessedShadow)).toBe(true);
    });

    it('should maintain shadow depth scaling', () => {
      expect(DesignSystemTestUtils.testShadowDepthScaling()).toBe(true);
    });

    it('should generate press physics styles', () => {
      const pressStyles = NeumorphicUtils.getPressStyles();
      
      expect(pressStyles.default).toHaveProperty('boxShadow');
      expect(pressStyles.pressed).toHaveProperty('boxShadow');
      expect(pressStyles.pressed).toHaveProperty('transform');
    });
  });

  describe('Animation System', () => {
    it('should have mechanical easing functions', () => {
      expect(mechanicalEasing.mechanical).toBe('cubic-bezier(0.34, 1.56, 0.64, 1)');
    });

    it('should create valid transitions', () => {
      const transition = AnimationUtils.createTransition(['transform'], 'normal', 'mechanical');
      expect(transition).toContain('transform');
      expect(transition).toContain('250ms');
      expect(transition).toContain('cubic-bezier(0.34, 1.56, 0.64, 1)');
    });

    it('should validate animation timing', () => {
      expect(AnimationUtils.validateAnimationTiming(250)).toBe(true);
      expect(AnimationUtils.validateAnimationTiming(50)).toBe(false); // Too fast
      expect(AnimationUtils.validateAnimationTiming(2000)).toBe(false); // Too slow
    });
  });

  describe('Manufacturing Details', () => {
    it('should generate screw styles', () => {
      const screwStyle = NeumorphicUtils.getScrewStyle();
      
      expect(screwStyle.width).toBe('8px');
      expect(screwStyle.height).toBe('8px');
      expect(screwStyle.borderRadius).toBe('50%');
      expect(screwStyle.position).toBe('absolute');
    });

    it('should generate vent slot styles', () => {
      const ventStyle = NeumorphicUtils.getVentSlotStyle();
      expect(ventStyle.background).toContain('repeating-linear-gradient');
    });
  });

  describe('LED Indicators', () => {
    it('should generate LED glow styles', () => {
      const glowStyle = NeumorphicUtils.getLEDGlowStyle('on', 1);
      
      expect(glowStyle.backgroundColor).toBe('#00b894');
      expect(glowStyle.boxShadow).toContain('0 0');
    });

    it('should handle off state correctly', () => {
      const offStyle = NeumorphicUtils.getLEDGlowStyle('off', 1);
      expect(offStyle.boxShadow).toBe('none');
    });
  });

  describe('Surface Textures', () => {
    it('should generate surface texture styles', () => {
      const smoothTexture = NeumorphicUtils.getSurfaceTexture('smooth');
      const brushedTexture = NeumorphicUtils.getSurfaceTexture('brushed');
      const texturedSurface = NeumorphicUtils.getSurfaceTexture('textured');
      
      expect(Object.keys(smoothTexture)).toHaveLength(0);
      expect(brushedTexture.background).toContain('linear-gradient');
      expect(texturedSurface.background).toContain('radial-gradient');
    });
  });

  describe('Complete System Validation', () => {
    it('should pass all design system tests', () => {
      const { passed, results } = DesignSystemTestUtils.runAllTests();
      
      expect(passed).toBe(true);
      expect(results.shadowDepthScaling).toBe(true);
      expect(results.ledColorCoding).toBe(true);
      expect(results.mechanicalEasing).toBe(true);
    });
  });
});