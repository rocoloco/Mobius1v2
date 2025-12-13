/**
 * Noise Texture Utilities
 * 
 * Generates SVG noise patterns for adding subtle texture to glass surfaces.
 * This prevents the "too clean" digital look and adds organic tactile quality.
 */

/**
 * Generate a data URI for an SVG noise pattern
 * @param opacity - Opacity of the noise (0-1)
 * @param scale - Scale of the noise pattern (default: 1)
 * @returns Data URI string for use in CSS background-image
 */
export function generateNoisePattern(opacity: number = 0.02, scale: number = 1): string {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${100 * scale}" height="${100 * scale}">
      <filter id="noise">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" stitchTiles="stitch"/>
        <feColorMatrix type="saturate" values="0"/>
      </filter>
      <rect width="100%" height="100%" filter="url(#noise)" opacity="${opacity}"/>
    </svg>
  `;
  
  return `data:image/svg+xml;base64,${btoa(svg)}`;
}

/**
 * CSS string for applying noise texture as background
 */
export const noiseTexture = {
  subtle: `url("${generateNoisePattern(0.015)}")`,
  medium: `url("${generateNoisePattern(0.03)}")`,
  strong: `url("${generateNoisePattern(0.05)}")`,
};

/**
 * Apply noise texture to an element via inline style
 * @param intensity - 'subtle' | 'medium' | 'strong'
 * @returns Style object for React components
 */
export function getNoiseStyle(intensity: 'subtle' | 'medium' | 'strong' = 'subtle') {
  return {
    backgroundImage: noiseTexture[intensity],
    backgroundRepeat: 'repeat',
    backgroundSize: '100px 100px',
  };
}
