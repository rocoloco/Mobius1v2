import { memo, useMemo, useCallback } from 'react';
import { Download, CheckCircle, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { BoundingBox } from '../molecules/BoundingBox';
import { VersionThumbnail } from '../molecules/VersionThumbnail';
import { CanvasEmptyState } from '../molecules/CanvasEmptyState';
import { GlassPanel } from '../atoms/GlassPanel';
import { luminousTokens } from '../../tokens';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

interface Violation {
  id: string;
  severity: 'critical' | 'warning';
  message: string;
  bounding_box?: [number, number, number, number]; // [x, y, w, h] as percentages
}

interface Version {
  attempt_id: number;
  image_url: string;
  thumb_url: string;
  score: number;
  timestamp: string;
  prompt: string;
}

interface CanvasProps {
  imageUrl?: string;
  violations: Violation[];
  versions: Version[];
  currentVersion: number;
  complianceScore: number;
  status: 'generating' | 'auditing' | 'complete' | 'error' | 'idle';
  highlightedViolationId?: string | null;
  auditError?: boolean; // When audit fails but image succeeds
  onVersionChange: (index: number) => void;
  onAcceptCorrection: () => void;
  onShowToast?: (type: 'success' | 'warning' | 'error', message: string) => void;
}

/**
 * Canvas - Image viewport with bounding boxes and version scrubber
 * 
 * Central component displaying generated images with compliance annotations.
 * Wrapped with React.memo for performance optimization - re-renders only when props change.
 * 
 * Features:
 * - Image display with object-contain sizing
 * - Skeleton loader during generation
 * - "Scanning Compliance..." overlay during audit
 * - Bounding box overlays for violations
 * - Version Scrubber timeline for session history
 * - Conditional action buttons based on compliance score
 * 
 * @param imageUrl - URL of the current image
 * @param violations - Array of violation objects with bounding boxes
 * @param versions - Array of version history
 * @param currentVersion - Index of currently displayed version
 * @param complianceScore - Overall compliance score (0-100)
 * @param status - Current generation/audit status
 * @param highlightedViolationId - ID of violation to highlight (optional)
 * @param onVersionChange - Callback when version thumbnail is clicked
 * @param onAcceptCorrection - Callback when "Accept Auto-Correction" is clicked
 */
export const Canvas = memo(function Canvas({
  imageUrl,
  violations,
  versions,
  currentVersion,
  complianceScore,
  status,
  highlightedViolationId = null,
  auditError = false,
  onVersionChange,
  onAcceptCorrection,
  onShowToast,
}: CanvasProps) {
  const prefersReducedMotion = useReducedMotion();

  // Memoize Framer Motion variants to prevent recreation on each render
  const slideUpVariants = useMemo(() => ({
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: prefersReducedMotion ? 0 : 0.3,
        ease: "easeInOut" as const
      }
    },
    exit: { 
      opacity: 0, 
      y: 20,
      transition: { 
        duration: prefersReducedMotion ? 0 : 0.2
      }
    }
  }), [prefersReducedMotion]);

  const fadeInVariants = useMemo(() => ({
    hidden: { opacity: 0, scale: 0.95 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { 
        duration: prefersReducedMotion ? 0 : 0.3,
        ease: "easeInOut" as const
      }
    },
    exit: { 
      opacity: 0, 
      scale: 0.95,
      transition: { 
        duration: prefersReducedMotion ? 0 : 0.2
      }
    }
  }), [prefersReducedMotion]);

  // Memoize filtered violations with bounding boxes
  const violationsWithBoxes = useMemo(() => 
    violations.filter((v) => v.bounding_box),
    [violations]
  );

  // Memoize version change handler
  const handleVersionChange = useCallback((index: number) => {
    onVersionChange(index);
  }, [onVersionChange]);

  // Memoize download handler
  const handleDownload = useCallback(() => {
    if (!imageUrl) return;
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `brand-asset-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, [imageUrl]);

  // Memoize download with warning handler
  const handleDownloadWithWarning = useCallback(() => {
    if (onShowToast) {
      onShowToast('warning', 'Downloading without compliance audit - use with caution');
    }
    handleDownload();
  }, [onShowToast, handleDownload]);

  // Determine which action button to show based on compliance score
  const getActionButton = useCallback(() => {
    if (status !== 'complete' || !imageUrl) return null;

    // If audit failed but image succeeded, show download with warning
    if (auditError) {
      return (
        <button
          onClick={handleDownloadWithWarning}
          className="px-6 py-3 rounded-xl bg-gradient-to-br from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-semibold flex items-center gap-2 transition-all duration-300 hover-scale-glow"
          style={{
            boxShadow: `0 0 25px ${luminousTokens.colors.compliance.review}40`,
            minHeight: '44px',
          }}
          data-testid="download-with-warning-button"
        >
          <AlertTriangle className="w-5 h-5" />
          Download (No Audit)
        </button>
      );
    }

    if (complianceScore >= 95) {
      // Show Download/Export button for high scores
      return (
        <button
          onClick={handleDownload}
          className="px-6 py-3 rounded-xl bg-gradient-to-br from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-semibold flex items-center gap-2 transition-all duration-300 hover-scale-glow"
          style={{
            boxShadow: `0 0 25px ${luminousTokens.colors.compliance.pass}40`,
            minHeight: '44px',
          }}
          data-testid="download-button"
        >
          <Download className="w-5 h-5" />
          Download / Export
        </button>
      );
    } else if (complianceScore >= 70) {
      // Show Accept Auto-Correction button for medium scores
      return (
        <button
          onClick={onAcceptCorrection}
          className="px-6 py-3 rounded-xl bg-gradient-to-br from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-semibold flex items-center gap-2 transition-all duration-300 hover-scale-glow"
          style={{
            boxShadow: `0 0 25px ${luminousTokens.colors.compliance.review}40`,
            minHeight: '44px',
          }}
          data-testid="accept-correction-button"
        >
          <CheckCircle className="w-5 h-5" />
          Accept Auto-Correction
        </button>
      );
    }

    // No action button for scores < 70%
    return null;
  }, [status, imageUrl, auditError, complianceScore, handleDownload, handleDownloadWithWarning, onAcceptCorrection]);

  return (
    <GlassPanel className="h-full" spotlight={true} shimmer={true} data-testid="canvas">
      <div className="h-full flex flex-col overflow-hidden">
      {/* Image Viewport */}
      <div className="flex-1 relative overflow-hidden flex items-center justify-center p-4">
        {status === 'generating' && (
          // Skeleton Loader
          <div
            className={`w-full h-full rounded-lg ${!prefersReducedMotion ? 'animate-shimmer' : ''}`}
            style={{
              background: 'linear-gradient(90deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 100%)',
              backgroundSize: '200% 100%',
            }}
            data-testid="skeleton-loader"
          />
        )}

        {status === 'auditing' && imageUrl && (
          // Image with "Scanning Compliance..." overlay
          <div className="relative w-full h-full">
            <img
              src={imageUrl}
              alt="Generated brand asset"
              className="w-full h-full object-contain"
              data-testid="canvas-image"
            />
            <div
              className="absolute inset-0 flex items-center justify-center"
              style={{
                backgroundColor: 'rgba(16, 16, 18, 0.8)',
                backdropFilter: luminousTokens.effects.backdropBlur,
              }}
              data-testid="auditing-overlay"
            >
              <div className="text-center">
                <div
                  className="text-xl font-semibold mb-2"
                  style={{
                    background: luminousTokens.colors.accent.gradient,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  Scanning Compliance...
                </div>
                <div
                  className="w-64 h-1 rounded-full overflow-hidden"
                  style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
                >
                  <div
                    className={`h-full rounded-full w-2/5 ${!prefersReducedMotion ? 'animate-scanning-laser' : ''}`}
                    style={{
                      background: luminousTokens.colors.accent.gradient,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {status === 'complete' && imageUrl && (
          // Image with bounding boxes
          <div className="relative w-full h-full">
            <img
              src={imageUrl}
              alt="Generated brand asset"
              className="w-full h-full object-contain"
              data-testid="canvas-image"
            />
            
            {/* Bounding Boxes */}
            <AnimatePresence>
              {violationsWithBoxes.map((violation, index) => {
                  const [x, y, w, h] = violation.bounding_box!;
                  return (
                    <motion.div
                      key={violation.id}
                      variants={fadeInVariants}
                      initial="hidden"
                      animate="visible"
                      exit="exit"
                      style={{
                        position: 'absolute',
                        left: `${x}%`,
                        top: `${y}%`,
                        width: `${w}%`,
                        height: `${h}%`,
                      }}
                      transition={{
                        delay: prefersReducedMotion ? 0 : index * 0.1
                      }}
                    >
                      <BoundingBox
                        x={0}
                        y={0}
                        width={100}
                        height={100}
                        severity={violation.severity}
                        label={violation.message}
                        highlighted={highlightedViolationId === violation.id}
                      />
                    </motion.div>
                  );
                })}
            </AnimatePresence>
          </div>
        )}

        {status === 'error' && (
          // Error state
          <div className="text-center">
            <div
              className="text-lg font-semibold mb-2"
              style={{ color: luminousTokens.colors.compliance.critical }}
            >
              Generation Failed
            </div>
            <p
              className="text-sm"
              style={{ color: luminousTokens.colors.text.muted }}
            >
              Please try again or adjust your prompt
            </p>
          </div>
        )}

        {status === 'idle' && (
          // Idle state - The "Zero Point" awaiting command
          <CanvasEmptyState />
        )}
      </div>

      {/* Version Scrubber Timeline */}
      {versions.length > 0 && (
        <div
          className="flex-shrink-0 border-t border-white/10 px-4 py-3"
          data-testid="version-scrubber"
        >
          <div 
            className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide"
            style={{
              scrollBehavior: 'smooth',
              WebkitOverflowScrolling: 'touch', // Enable momentum scrolling on iOS
            }}
          >
            {versions.map((version, index) => (
              <VersionThumbnail
                key={version.attempt_id}
                imageUrl={version.thumb_url}
                score={version.score}
                timestamp={new Date(version.timestamp)}
                active={index === currentVersion}
                onClick={() => handleVersionChange(index)}
              />
            ))}
          </div>
          
          {/* Custom scrollbar styles for mobile */}
          <style dangerouslySetInnerHTML={{
            __html: `
              .scrollbar-hide {
                -ms-overflow-style: none;
                scrollbar-width: none;
              }
              .scrollbar-hide::-webkit-scrollbar {
                display: none;
              }
              
              @media (max-width: 767px) {
                .scrollbar-hide {
                  scroll-snap-type: x mandatory;
                  padding-bottom: 8px;
                }
                .scrollbar-hide > * {
                  scroll-snap-align: start;
                }
              }
            `
          }} />
        </div>
      )}

      {/* Action Button */}
      <AnimatePresence>
        {getActionButton() && (
          <motion.div
            variants={slideUpVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="flex-shrink-0 border-t border-white/10 px-4 py-4 flex justify-center"
            data-testid="action-button-container"
          >
            {getActionButton()}
          </motion.div>
        )}
      </AnimatePresence>
      </div>
    </GlassPanel>
  );
});

// Display name for debugging
Canvas.displayName = 'Canvas';
