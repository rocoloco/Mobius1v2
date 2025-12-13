import { useState } from 'react';
import { MonoText } from '../atoms/MonoText';
import { luminousTokens } from '../../tokens';

interface ColorSwatchProps {
  detected: string;  // Hex code of detected color
  brand: string;     // Hex code of brand color
  distance: number;  // Color distance metric
  pass: boolean;     // Whether the color passes compliance
}

/**
 * ColorSwatch - Split pill component showing detected vs. brand color
 * 
 * Displays a split pill with detected color on the left half and brand color
 * on the right half. Shows hex codes using MonoText and displays distance
 * metric in a tooltip.
 * 
 * Used in the TwinData panel to visualize color compliance.
 * 
 * @param detected - Hex code of the detected color (e.g., "#2664EC")
 * @param brand - Hex code of the brand color (e.g., "#2563EB")
 * @param distance - Color distance metric (e.g., 1.2)
 * @param pass - Whether the color passes compliance check
 */
export function ColorSwatch({ detected, brand, distance, pass }: ColorSwatchProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  
  // Format tooltip text
  const tooltipText = `Distance: ${distance.toFixed(1)} (${pass ? 'Pass' : 'Fail'})`;
  
  return (
    <div
      style={{
        position: 'relative',
        marginBottom: '16px',
      }}
      data-testid="color-swatch"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Split pill container */}
      <div 
        style={{
          display: 'flex',
          alignItems: 'center',
          borderRadius: '16px',
          overflow: 'hidden',
          border: `1px solid ${luminousTokens.colors.border}`,
        }}
      >
        {/* Left half - Detected color */}
        <div
          data-testid="detected-color-dot"
          style={{
            flex: 1,
            padding: '12px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: detected,
          }}
        >
          <MonoText className="text-xs font-semibold drop-shadow-lg">
            {detected.toUpperCase()}
          </MonoText>
        </div>
        
        {/* Divider */}
        <div style={{ width: '1px', height: '32px', backgroundColor: luminousTokens.colors.border }} />
        
        {/* Right half - Brand color */}
        <div
          data-testid="brand-color-dot"
          style={{
            flex: 1,
            padding: '12px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: brand,
          }}
        >
          <MonoText className="text-xs font-semibold drop-shadow-lg">
            {brand.toUpperCase()}
          </MonoText>
        </div>
      </div>
      
      {/* Tooltip - Shows on hover */}
      {showTooltip && (
        <div
          style={{
            position: 'absolute',
            bottom: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            marginBottom: '8px',
            padding: '8px 16px',
            borderRadius: '8px',
            backgroundColor: 'rgba(0, 0, 0, 0.95)',
            backdropFilter: luminousTokens.effects.backdropBlur,
            border: `1px solid ${luminousTokens.colors.border}`,
            whiteSpace: 'nowrap',
            zIndex: 50,
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          }}
        >
          <div 
            style={{ 
              fontSize: '12px', 
              fontFamily: 'monospace',
              color: pass ? luminousTokens.colors.compliance.pass : luminousTokens.colors.compliance.critical,
            }}
          >
            {tooltipText}
          </div>
          {/* Tooltip arrow */}
          <div 
            style={{
              position: 'absolute',
              top: '100%',
              left: '50%',
              transform: 'translateX(-50%)',
              width: 0,
              height: 0,
              borderLeft: '6px solid transparent',
              borderRight: '6px solid transparent',
              borderTop: '6px solid rgba(0, 0, 0, 0.95)',
            }}
          />
        </div>
      )}
    </div>
  );
}
