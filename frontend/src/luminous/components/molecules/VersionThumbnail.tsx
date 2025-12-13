import { memo } from 'react';
import { luminousTokens } from '../../tokens';

interface VersionThumbnailProps {
  imageUrl: string;
  score: number;
  timestamp: Date;
  active: boolean;
  onClick: () => void;
}

/**
 * VersionThumbnail - Thumbnail component for Version Scrubber timeline
 * 
 * Displays a thumbnail image with score badge overlay in the Version Scrubber.
 * Used to navigate between different versions in a multi-turn session.
 * Active thumbnails receive highlight styling.
 * 
 * @param imageUrl - URL of the thumbnail image
 * @param score - Compliance score (0-100)
 * @param timestamp - Version creation timestamp
 * @param active - Whether this version is currently active
 * @param onClick - Callback triggered when thumbnail is clicked
 */
export const VersionThumbnail = memo(function VersionThumbnail({
  imageUrl,
  score,
  timestamp,
  active,
  onClick,
}: VersionThumbnailProps) {
  // Format timestamp to HH:MM
  const timeString = timestamp.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

  // Determine score badge color based on thresholds
  const getScoreColor = () => {
    if (score >= 95) return luminousTokens.colors.compliance.pass;
    if (score >= 70) return luminousTokens.colors.compliance.review;
    return luminousTokens.colors.compliance.critical;
  };

  return (
    <button
      onClick={onClick}
      data-testid="version-thumbnail"
      data-active={active}
      className={`relative flex-shrink-0 rounded-lg overflow-hidden transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
        active ? 'scale-105' : 'hover-scale'
      }`}
      style={{
        width: '80px',
        height: '80px',
        minWidth: '80px', // Prevent shrinking in flex container
        cursor: 'pointer',
        borderColor: active ? luminousTokens.colors.accent.blue : luminousTokens.colors.border,
        border: active ? `2px solid ${luminousTokens.colors.accent.blue}` : '1px solid',
      }}
      aria-label={`Load version from ${timeString} with ${score}% compliance score${active ? ' (currently active)' : ''}`}
    >
      {/* Thumbnail Image */}
      <img
        src={imageUrl}
        alt={`Version from ${timeString}`}
        className="w-full h-full object-cover"
        data-testid="thumbnail-image"
      />

      {/* Score Badge Overlay */}
      <div
        className="absolute top-1 right-1 px-2 py-0.5 rounded-md text-xs font-semibold"
        data-testid="score-badge"
        style={{
          backgroundColor: getScoreColor(),
          color: '#FFFFFF',
        }}
      >
        {score}%
      </div>

      {/* Timestamp Label */}
      <div
        className="absolute bottom-0 left-0 right-0 px-2 py-1 text-xs"
        style={{
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: luminousTokens.effects.backdropBlur,
          color: luminousTokens.colors.text.body,
        }}
      >
        {timeString}
      </div>

      {/* Active Indicator Glow */}
      {active && (
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            boxShadow: luminousTokens.effects.glowStrong,
          }}
        />
      )}
      
      {/* Mobile-specific styles */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @media (max-width: 767px) {
            [data-testid="version-thumbnail"] {
              width: 72px !important;
              height: 72px !important;
              min-width: 72px !important;
              /* Ensure minimum 44x44px touch target is met */
              min-height: 44px !important;
              /* Add more padding for easier touch interaction */
              margin: 4px;
            }
            
            [data-testid="version-thumbnail"]:active {
              transform: scale(0.95);
              transition: transform 0.1s ease;
            }
          }
          
          @media (max-width: 480px) {
            [data-testid="version-thumbnail"] {
              width: 64px !important;
              height: 64px !important;
              min-width: 64px !important;
            }
          }
        `
      }} />
    </button>
  );
});
