/**
 * Color Contrast Utilities
 * 
 * Utilities for calculating and verifying WCAG color contrast ratios.
 * Ensures all text meets WCAG AA standards (4.5:1 ratio).
 */

/**
 * Convert hex color to RGB values
 * @param hex - Hex color string (e.g., "#FF0000" or "FF0000")
 * @returns RGB object with r, g, b values (0-255)
 */
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const cleanHex = hex.replace('#', '');
  const result = /^([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(cleanHex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

/**
 * Calculate relative luminance of a color
 * @param r - Red value (0-255)
 * @param g - Green value (0-255)
 * @param b - Blue value (0-255)
 * @returns Relative luminance (0-1)
 */
function getLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

/**
 * Calculate contrast ratio between two colors
 * @param color1 - First color (hex string)
 * @param color2 - Second color (hex string)
 * @returns Contrast ratio (1-21)
 */
export function getContrastRatio(color1: string, color2: string): number {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);
  
  if (!rgb1 || !rgb2) {
    throw new Error('Invalid hex color format');
  }
  
  const lum1 = getLuminance(rgb1.r, rgb1.g, rgb1.b);
  const lum2 = getLuminance(rgb2.r, rgb2.g, rgb2.b);
  
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  
  return (brightest + 0.05) / (darkest + 0.05);
}

/**
 * Check if contrast ratio meets WCAG AA standards
 * @param ratio - Contrast ratio
 * @param level - WCAG level ('AA' or 'AAA')
 * @param size - Text size ('normal' or 'large')
 * @returns Whether the ratio meets the standard
 */
export function meetsWCAGStandard(
  ratio: number, 
  level: 'AA' | 'AAA' = 'AA', 
  size: 'normal' | 'large' = 'normal'
): boolean {
  if (level === 'AA') {
    return size === 'large' ? ratio >= 3 : ratio >= 4.5;
  } else {
    return size === 'large' ? ratio >= 4.5 : ratio >= 7;
  }
}

/**
 * Audit color combinations for WCAG compliance
 * @param combinations - Array of [foreground, background] color pairs
 * @returns Audit results with compliance status
 */
export function auditColorContrast(combinations: Array<[string, string]>): Array<{
  foreground: string;
  background: string;
  ratio: number;
  compliant: boolean;
  level: 'AA' | 'AAA' | 'Fail';
}> {
  return combinations.map(([fg, bg]) => {
    const ratio = getContrastRatio(fg, bg);
    const meetsAA = meetsWCAGStandard(ratio, 'AA');
    const meetsAAA = meetsWCAGStandard(ratio, 'AAA');
    
    return {
      foreground: fg,
      background: bg,
      ratio: Math.round(ratio * 100) / 100,
      compliant: meetsAA,
      level: meetsAAA ? 'AAA' : meetsAA ? 'AA' : 'Fail',
    };
  });
}

/**
 * Luminous design system color contrast audit
 * Tests all text color combinations against backgrounds
 */
export function auditLuminousColors() {
  const background = '#101012'; // void
  const glassBackground = '#1a1a1c'; // Approximate glass surface over void
  
  const textColors = {
    body: '#94A3B8',    // Slate-400
    high: '#F1F5F9',    // High contrast
    muted: '#64748B',   // Slate-500
  };
  
  const combinations: Array<[string, string]> = [
    // Text on void background
    [textColors.body, background],
    [textColors.high, background],
    [textColors.muted, background],
    
    // Text on glass surface
    [textColors.body, glassBackground],
    [textColors.high, glassBackground],
    [textColors.muted, glassBackground],
  ];
  
  return auditColorContrast(combinations);
}