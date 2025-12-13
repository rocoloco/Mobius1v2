import { GlassPanel } from '../atoms/GlassPanel';
import { MonoText } from '../atoms/MonoText';
import { ColorSwatch } from '../molecules/ColorSwatch';
import { luminousTokens } from '../../tokens';

interface DetectedFont {
  family: string;
  weight: string;
  allowed: boolean;
}

interface TwinDataProps {
  detectedColors: string[];
  brandColors: string[];
  detectedFonts: DetectedFont[];
}

/**
 * Calculate color distance using simple Euclidean distance in RGB space
 * This is a simplified version - production would use Delta E (CIE76/2000)
 */
function calculateColorDistance(hex1: string, hex2: string): number {
  const rgb1 = hexToRgb(hex1);
  const rgb2 = hexToRgb(hex2);
  
  if (!rgb1 || !rgb2) return 0;
  
  const rDiff = rgb1.r - rgb2.r;
  const gDiff = rgb1.g - rgb2.g;
  const bDiff = rgb1.b - rgb2.b;
  
  return Math.sqrt(rDiff * rDiff + gDiff * gDiff + bDiff * bDiff) / 255 * 100;
}

/**
 * Convert hex color to RGB
 */
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

/**
 * Find the nearest brand color for a detected color
 */
function findNearestBrandColor(detectedColor: string, brandColors: string[]): {
  brandColor: string;
  distance: number;
} {
  if (brandColors.length === 0) {
    return { brandColor: detectedColor, distance: 0 };
  }
  
  let minDistance = Infinity;
  let nearestColor = brandColors[0];
  
  for (const brandColor of brandColors) {
    const distance = calculateColorDistance(detectedColor, brandColor);
    if (distance < minDistance) {
      minDistance = distance;
      nearestColor = brandColor;
    }
  }
  
  return { brandColor: nearestColor, distance: minDistance };
}

/**
 * TwinData - Visual token inspector panel
 * 
 * Displays the "Compressed Digital Twin" - detected visual tokens (colors, fonts)
 * from the generated image analysis. Shows color swatches comparing detected colors
 * to nearest brand colors, and lists detected fonts with compliance status.
 * 
 * Used in the Bento Grid layout to provide transparency into what the AI detected
 * in the generated image.
 * 
 * @param detectedColors - Array of hex color codes detected in the image
 * @param brandColors - Array of hex color codes from the brand guidelines
 * @param detectedFonts - Array of font objects with family, weight, and compliance status
 */
export function TwinData({ 
  detectedColors, 
  brandColors, 
  detectedFonts 
}: TwinDataProps) {
  // Calculate color matches
  const colorMatches = detectedColors.map(detected => {
    const { brandColor, distance } = findNearestBrandColor(detected, brandColors);
    // Pass if distance is less than 5% (threshold for "close enough")
    const pass = distance < 5;
    return { detected, brand: brandColor, distance, pass };
  });

  return (
    <GlassPanel className="h-full" spotlight={true}>
      <div 
        className="flex flex-col gap-4 h-full" 
        style={{ padding: '24px' }}
        data-testid="twin-data"
      >
        {/* Header */}
        <div className="flex-shrink-0">
          <h2 className="text-base font-semibold text-slate-100">
            Compressed Digital Twin
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Detected visual tokens
          </p>
        </div>
        
        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto space-y-4">
          {/* Colors Section */}
          <div>
            <h3 
              className="text-xs font-semibold mb-2"
              style={{ color: luminousTokens.colors.text.high }}
            >
              Colors
            </h3>
            
            {colorMatches.length === 0 ? (
              <div className="text-slate-400 text-sm py-4">
                No colors detected
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                {colorMatches.map((match, index) => (
                  <ColorSwatch
                    key={`${match.detected}-${index}`}
                    detected={match.detected}
                    brand={match.brand}
                    distance={match.distance}
                    pass={match.pass}
                  />
                ))}
              </div>
            )}
          </div>
          
          {/* Fonts Section */}
          <div>
            <h3 
              className="text-xs font-semibold mb-2"
              style={{ color: luminousTokens.colors.text.high }}
            >
              Fonts
            </h3>
            
            {detectedFonts.length === 0 ? (
              <div className="text-slate-400 text-sm py-4">
                No fonts detected
              </div>
            ) : (
              <div className="space-y-2">
                {detectedFonts.map((font, index) => (
                  <div
                    key={`${font.family}-${font.weight}-${index}`}
                    className="flex items-center justify-between px-4 py-3 rounded-lg"
                    style={{
                      backgroundColor: luminousTokens.colors.glass,
                      borderColor: luminousTokens.colors.border,
                      border: '1px solid',
                    }}
                    data-testid="font-item"
                  >
                    {/* Font name */}
                    <MonoText className="text-sm">
                      {`${font.family}-${font.weight}`}
                    </MonoText>
                    
                    {/* Compliance status */}
                    <span
                      className="text-xs px-2 py-1 rounded"
                      style={{
                        color: font.allowed 
                          ? luminousTokens.colors.compliance.pass 
                          : luminousTokens.colors.compliance.critical,
                        backgroundColor: font.allowed
                          ? 'rgba(16, 185, 129, 0.1)'
                          : 'rgba(239, 68, 68, 0.1)',
                      }}
                      data-testid="font-compliance-status"
                    >
                      {font.allowed ? '(Allowed)' : '(Forbidden)'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}
