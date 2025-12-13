import { luminousTokens } from '../../tokens';

interface BoundingBoxProps {
  x: number;
  y: number;
  width: number;
  height: number;
  severity: 'critical' | 'warning';
  label: string;
  highlighted?: boolean;
}

/**
 * BoundingBox - Visual overlay component for compliance violations
 * 
 * Renders an absolutely positioned div overlay on the Canvas to indicate
 * areas where brand compliance violations were detected. The box uses
 * dashed borders with color-coded severity (red for critical, amber for warning).
 * Includes a label tag attached to the box displaying the violation description.
 * 
 * @param x - X coordinate (percentage or pixels)
 * @param y - Y coordinate (percentage or pixels)
 * @param width - Width (percentage or pixels)
 * @param height - Height (percentage or pixels)
 * @param severity - Violation severity level ('critical' or 'warning')
 * @param label - Violation description text
 * @param highlighted - Whether this box should be highlighted (dimming others)
 */
export function BoundingBox({
  x,
  y,
  width,
  height,
  severity,
  label,
  highlighted = false,
}: BoundingBoxProps) {
  // Determine border color based on severity
  const getBorderColor = () => {
    return severity === 'critical'
      ? luminousTokens.colors.compliance.critical
      : luminousTokens.colors.compliance.review;
  };

  const borderColor = getBorderColor();

  return (
    <div
      data-testid="bounding-box"
      data-severity={severity}
      data-highlighted={highlighted}
      className="absolute pointer-events-none transition-opacity duration-300"
      style={{
        left: `${x}%`,
        top: `${y}%`,
        width: `${width}%`,
        height: `${height}%`,
        border: `1px dashed ${borderColor}`,
        opacity: highlighted ? 1 : 0.6,
        boxShadow: highlighted ? `0 0 15px ${borderColor}` : 'none',
      }}
    >
      {/* Label Tag */}
      <div
        data-testid="bounding-box-label"
        className="absolute -top-6 left-0 px-2 py-1 rounded text-xs font-medium whitespace-nowrap"
        style={{
          backgroundColor: borderColor,
          color: '#FFFFFF',
          pointerEvents: 'auto',
        }}
      >
        {label}
      </div>
    </div>
  );
}
