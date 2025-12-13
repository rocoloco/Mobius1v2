import { memo, useMemo, useCallback, useState, useEffect } from 'react';
import { Download, CheckCircle, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { BoundingBox } from '../molecules/BoundingBox';
import { VersionThumbnail } from '../molecules/VersionThumbnail';
import { CanvasEmptyState } from '../molecules/CanvasEmptyState';
import { CanvasGeneratingState } from '../molecules/CanvasGeneratingState';
import { ShipItModal } from './ShipItModal';
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
  // Ship It modal handlers
  onCreateSimilar?: () => void;
  onTryDifferentSizes?: () => void;
  onStartFresh?: () => void;
  currentPrompt?: string;
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
 * @param onAcceptCorrection - Callback when "Ship It" is clicked
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
  onCreateSimilar,
  onTryDifferentSizes,
  onStartFresh,
  currentPrompt = '',
}: CanvasProps) {
  const prefersReducedMotion = useReducedMotion();
  
  // Track when image first appears for exit animation
  const [showImageReveal, setShowImageReveal] = useState(false);
  
  // Ship It modal state
  const [showShipItModal, setShowShipItModal] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  
  // Trigger reveal animation when transitioning from generating to auditing/complete
  useEffect(() => {
    if ((status === 'auditing' || status === 'complete') && imageUrl) {
      setShowImageReveal(true);
      // Reset after animation completes
      const timer = setTimeout(() => setShowImageReveal(false), 800);
      return () => clearTimeout(timer);
    }
  }, [status, imageUrl]);

  // Enhanced Ship It handler - shows modal first, then processes approval
  const handleShipIt = useCallback(async () => {
    // First show the celebration modal
    setShowShipItModal(true);
    
    // Process the approval in the background
    try {
      await onAcceptCorrection();
    } catch (error) {
      console.error('Error shipping asset:', error);
      onShowToast?.('error', 'Failed to ship asset');
    }
  }, [onAcceptCorrection, onShowToast]);

  // Download handler for modal
  const handleModalDownload = useCallback(async () => {
    if (!imageUrl) return;
    
    setIsDownloading(true);
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `asset-${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      onShowToast?.('success', 'Asset downloaded successfully');
    } catch (error) {
      console.error('Download failed:', error);
      onShowToast?.('error', 'Failed to download asset');
    } finally {
      setIsDownloading(false);
    }
  }, [imageUrl, onShowToast]);

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

  // Image reveal animation - the "arrival" moment
  const imageRevealVariants = useMemo(() => ({
    hidden: { 
      opacity: 0, 
      scale: 0.92,
      filter: 'blur(10px) brightness(1.5)',
    },
    visible: { 
      opacity: 1, 
      scale: 1,
      filter: 'blur(0px) brightness(1)',
      transition: { 
        duration: prefersReducedMotion ? 0 : 0.6,
        ease: [0.25, 0.46, 0.45, 0.94] as const, // Custom easing for premium feel
      }
    },
  }), [prefersReducedMotion]);

  // Generating state exit animation - needs all three states for AnimatePresence
  const generatingExitVariants = useMemo(() => ({
    initial: {
      opacity: 1,
      scale: 1,
      filter: 'blur(0px)',
    },
    animate: {
      opacity: 1,
      scale: 1,
      filter: 'blur(0px)',
    },
    exit: {
      opacity: 0,
      scale: 1.15,
      filter: 'blur(12px)',
      transition: {
        duration: prefersReducedMotion ? 0 : 0.5,
        ease: 'easeIn' as const,
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
  const handleDownload = useCallback(async () => {
    if (!imageUrl) return;
    
    try {
      // Fetch the image to ensure it's available and handle CORS properly
      const response = await fetch(imageUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch image: ${response.status}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      // Create download link
      const link = document.createElement('a');
      link.href = url;
      link.download = `brand-asset-${Date.now()}.png`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up object URL
      window.URL.revokeObjectURL(url);
      
      // Show success feedback
      onShowToast?.('success', 'Asset downloaded successfully');
      
    } catch (error) {
      console.error('Download failed:', error);
      onShowToast?.('error', 'Failed to download asset. Please try again.');
    }
  }, [imageUrl, onShowToast]);

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
      // Show Download button for high scores - matches Luminous design system
      return (
        <button
          onClick={handleDownload}
          className="px-6 py-3 rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-semibold flex items-center gap-2 transition-all duration-300 group"
          style={{
            boxShadow: luminousTokens.effects.glow,
            minHeight: '44px',
          }}
          data-testid="download-button"
        >
          <Download className="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
          Download
        </button>
      );
    } else if (complianceScore >= 70) {
      // Show Ship It button for medium scores - respects user aesthetic judgment
      return (
        <button
          onClick={handleShipIt}
          className="px-6 py-3 rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-semibold flex items-center gap-2 transition-all duration-300 group"
          style={{
            boxShadow: luminousTokens.effects.glow,
            minHeight: '44px',
          }}
          data-testid="ship-it-button"
        >
          <CheckCircle className="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
          Ship It
        </button>
      );
    }

    // No action button for scores < 70%
    return null;
  }, [status, imageUrl, auditError, complianceScore, handleDownload, handleDownloadWithWarning, handleShipIt]);

  // Cache the action button result to avoid double computation
  const actionButton = getActionButton();

  return (
    <>
    <GlassPanel className="h-full" spotlight={true} shimmer={true} data-testid="canvas">
      <div className="h-full flex flex-col overflow-hidden">
      {/* Image Viewport */}
      <div className="flex-1 relative overflow-hidden flex items-center justify-center p-4">
        <AnimatePresence mode="wait">
        {status === 'generating' && (
          // Premium "Assembling" State with breathing pulse and particles
          <motion.div
            key="generating"
            className="w-full h-full"
            variants={generatingExitVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <CanvasGeneratingState />
          </motion.div>
        )}

        {status === 'auditing' && imageUrl && (
          // Image with "Scanning Compliance..." overlay - includes reveal animation
          <motion.div 
            key="auditing"
            className="relative w-full h-full"
            variants={imageRevealVariants}
            initial={showImageReveal ? "hidden" : false}
            animate="visible"
          >
            <img
              src={imageUrl}
              alt="Generated brand asset"
              className="w-full h-full object-contain"
              data-testid="canvas-image"
            />
            <motion.div
              className="absolute inset-0 flex items-center justify-center"
              style={{
                backgroundColor: 'rgba(16, 16, 18, 0.8)',
                backdropFilter: luminousTokens.effects.backdropBlur,
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.3 }}
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
            </motion.div>
          </motion.div>
        )}

        {status === 'complete' && imageUrl && (
          // Image with bounding boxes - includes reveal animation on first appearance
          <motion.div 
            key="complete"
            className="relative w-full h-full"
            variants={imageRevealVariants}
            initial={showImageReveal ? "hidden" : false}
            animate="visible"
          >
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
          </motion.div>
        )}

        {status === 'error' && (
          // Error state
          <motion.div 
            key="error"
            className="text-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
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
          </motion.div>
        )}

        {status === 'idle' && (
          // Idle state - The "Zero Point" awaiting command
          <motion.div
            key="idle"
            className="w-full h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            <CanvasEmptyState />
          </motion.div>
        )}
        </AnimatePresence>
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
        {actionButton && (
          <motion.div
            variants={slideUpVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="flex-shrink-0 border-t border-white/10 px-4 py-4 flex justify-center"
            data-testid="action-button-container"
          >
            {actionButton}
          </motion.div>
        )}
      </AnimatePresence>
      </div>
    </GlassPanel>

    {/* Ship It Modal */}
    <ShipItModal
      isOpen={showShipItModal}
      onClose={() => setShowShipItModal(false)}
      imageUrl={imageUrl || ''}
      complianceScore={complianceScore}
      prompt={currentPrompt}
      onCreateSimilar={() => {
        setShowShipItModal(false);
        onCreateSimilar?.();
      }}
      onTryDifferentSizes={() => {
        setShowShipItModal(false);
        onTryDifferentSizes?.();
      }}
      onStartFresh={() => {
        setShowShipItModal(false);
        onStartFresh?.();
      }}
      onDownload={handleModalDownload}
      isDownloading={isDownloading}
    />
  </>
  );
});

// Display name for debugging
Canvas.displayName = 'Canvas';
