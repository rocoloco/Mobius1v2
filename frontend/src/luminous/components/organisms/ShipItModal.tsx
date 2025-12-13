import React, { useState, useCallback } from 'react';
import { X, Download, Share2, Copy, Sparkles, Plus, CheckCircle } from 'lucide-react';
import { GlassPanel } from '../atoms/GlassPanel';
import { luminousTokens } from '../../tokens';
import { motion, AnimatePresence } from 'framer-motion';

interface ShipItModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  complianceScore: number;
  prompt: string;
  onCreateSimilar: () => void;
  onTryDifferentSizes: () => void;
  onStartFresh: () => void;
  onDownload: () => void;
  assetName?: string;
  isDownloading?: boolean;
}

/**
 * ShipItModal - Post-approval celebration and next actions modal
 * 
 * Appears after user clicks "Ship It" to celebrate their decision and offer
 * immediate next steps. Follows the enhanced "Ship It" flow design.
 */
export const ShipItModal: React.FC<ShipItModalProps> = ({
  isOpen,
  onClose,
  imageUrl,
  complianceScore,
  prompt,
  onCreateSimilar,
  onTryDifferentSizes,
  onStartFresh,
  onDownload,
  assetName = 'Your Asset',
  isDownloading = false,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopyLink = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(imageUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy link:', err);
    }
  }, [imageUrl]);

  const handleShare = useCallback(async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: assetName,
          text: `Check out this brand asset I created: "${prompt}"`,
          url: imageUrl,
        });
      } catch (err) {
        console.error('Failed to share:', err);
      }
    } else {
      // Fallback to copy link
      handleCopyLink();
    }
  }, [assetName, prompt, imageUrl, handleCopyLink]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }}
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        >
          <GlassPanel className="relative" glow shimmer>
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 transition-colors duration-200 flex items-center justify-center z-10"
              aria-label="Close modal"
            >
              <X size={16} style={{ color: luminousTokens.colors.text.body }} />
            </button>

            <div className="p-8">
              {/* Celebration Header */}
              <div className="text-center mb-8">
                <div className="flex items-center justify-center mb-4">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                    <CheckCircle className="w-8 h-8 text-white" />
                  </div>
                </div>
                <h2 
                  className="text-2xl font-bold mb-2"
                  style={{ color: luminousTokens.colors.text.high }}
                >
                  🚀 Shipped Successfully!
                </h2>
                <p 
                  className="text-sm"
                  style={{ color: luminousTokens.colors.text.body }}
                >
                  Your asset has been saved to your library with {complianceScore}% compliance
                </p>
              </div>

              {/* Image Preview */}
              <div className="mb-8">
                <div className="relative rounded-xl overflow-hidden bg-white/5 border border-white/10">
                  <img
                    src={imageUrl}
                    alt="Shipped asset"
                    className="w-full h-48 object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
                </div>
              </div>

              {/* Quick Actions */}
              <div className="mb-8">
                <h3 
                  className="text-lg font-semibold mb-4"
                  style={{ color: luminousTokens.colors.text.high }}
                >
                  Quick Actions
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={onDownload}
                    disabled={isDownloading}
                    className="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-purple-500/30 transition-all duration-300 flex items-center gap-3 disabled:opacity-50"
                  >
                    <Download className="w-5 h-5" style={{ color: luminousTokens.colors.accent.blue }} />
                    <div className="text-left">
                      <div 
                        className="font-medium text-sm"
                        style={{ color: luminousTokens.colors.text.high }}
                      >
                        {isDownloading ? 'Downloading...' : 'Download'}
                      </div>
                      <div 
                        className="text-xs"
                        style={{ color: luminousTokens.colors.text.muted }}
                      >
                        High-res PNG
                      </div>
                    </div>
                  </button>

                  <button
                    onClick={handleShare}
                    className="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-purple-500/30 transition-all duration-300 flex items-center gap-3"
                  >
                    {copied ? (
                      <CheckCircle className="w-5 h-5" style={{ color: luminousTokens.colors.compliance.pass }} />
                    ) : (
                      <Share2 className="w-5 h-5" style={{ color: luminousTokens.colors.accent.purple }} />
                    )}
                    <div className="text-left">
                      <div 
                        className="font-medium text-sm"
                        style={{ color: luminousTokens.colors.text.high }}
                      >
                        {copied ? 'Copied!' : 'Share'}
                      </div>
                      <div 
                        className="text-xs"
                        style={{ color: luminousTokens.colors.text.muted }}
                      >
                        Copy link
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Next Steps */}
              <div className="mb-6">
                <h3 
                  className="text-lg font-semibold mb-4"
                  style={{ color: luminousTokens.colors.text.high }}
                >
                  What's Next?
                </h3>
                <div className="space-y-3">
                  <button
                    onClick={onCreateSimilar}
                    className="w-full p-4 rounded-xl bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 hover:from-purple-600/30 hover:to-blue-600/30 transition-all duration-300 flex items-center gap-4"
                  >
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div className="text-left flex-1">
                      <div 
                        className="font-medium"
                        style={{ color: luminousTokens.colors.text.high }}
                      >
                        Create Another Like This
                      </div>
                      <div 
                        className="text-sm"
                        style={{ color: luminousTokens.colors.text.body }}
                      >
                        Generate variations with the same style and approach
                      </div>
                    </div>
                  </button>

                  <button
                    onClick={onTryDifferentSizes}
                    className="w-full p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-amber-500/30 transition-all duration-300 flex items-center gap-4"
                  >
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-600 to-orange-600 flex items-center justify-center">
                      <Copy className="w-5 h-5 text-white" />
                    </div>
                    <div className="text-left flex-1">
                      <div 
                        className="font-medium"
                        style={{ color: luminousTokens.colors.text.high }}
                      >
                        Try Different Sizes
                      </div>
                      <div 
                        className="text-sm"
                        style={{ color: luminousTokens.colors.text.body }}
                      >
                        Instagram story, LinkedIn banner, business card
                      </div>
                    </div>
                  </button>

                  <button
                    onClick={onStartFresh}
                    className="w-full p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-green-500/30 transition-all duration-300 flex items-center gap-4"
                  >
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-600 to-emerald-600 flex items-center justify-center">
                      <Plus className="w-5 h-5 text-white" />
                    </div>
                    <div className="text-left flex-1">
                      <div 
                        className="font-medium"
                        style={{ color: luminousTokens.colors.text.high }}
                      >
                        Start Fresh
                      </div>
                      <div 
                        className="text-sm"
                        style={{ color: luminousTokens.colors.text.body }}
                      >
                        Begin a new creative session
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Footer */}
              <div className="text-center pt-4 border-t border-white/10">
                <p 
                  className="text-xs"
                  style={{ color: luminousTokens.colors.text.muted }}
                >
                  Your creative choices help improve our AI for future generations
                </p>
              </div>
            </div>
          </GlassPanel>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};