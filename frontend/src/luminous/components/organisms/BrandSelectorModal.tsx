import React, { useState, useCallback } from 'react';
import { X, Check, Sparkles } from 'lucide-react';
import { GlassPanel } from '../atoms/GlassPanel';
import { luminousTokens } from '../../tokens';
import { motion, AnimatePresence } from 'framer-motion';

interface Brand {
  id: string;
  name: string;
  colorCount?: number;
  ruleCount?: number;
  archetype?: string;
  logoUrl?: string;
}

interface BrandSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  brands: Brand[];
  selectedBrandId: string | null;
  onSelectBrand: (brandId: string) => void;
  loading?: boolean;
}

/**
 * BrandSelectorModal - Modal for selecting a brand from available options
 * 
 * Appears when user clicks "Select Brand" button in Director header.
 * Shows list of available brands with radio button selection.
 */
export const BrandSelectorModal: React.FC<BrandSelectorModalProps> = ({
  isOpen,
  onClose,
  brands,
  selectedBrandId,
  onSelectBrand,
  loading = false,
}) => {
  const [tempSelectedId, setTempSelectedId] = useState<string | null>(selectedBrandId);

  const handleBrandSelect = useCallback((brandId: string) => {
    setTempSelectedId(brandId);
  }, []);

  const handleConfirm = useCallback(() => {
    if (tempSelectedId) {
      onSelectBrand(tempSelectedId);
      onClose();
    }
  }, [tempSelectedId, onSelectBrand, onClose]);

  const handleCancel = useCallback(() => {
    setTempSelectedId(selectedBrandId);
    onClose();
  }, [selectedBrandId, onClose]);

  // Reset temp selection when modal opens
  React.useEffect(() => {
    if (isOpen) {
      setTempSelectedId(selectedBrandId);
    }
  }, [isOpen, selectedBrandId]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }}
        onClick={handleCancel}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-md max-h-[80vh] overflow-hidden"
        >
          <GlassPanel className="relative" glow shimmer>
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/10">
              <h2 
                className="text-xl font-semibold"
                style={{ color: luminousTokens.colors.text.high }}
              >
                Select Brand
              </h2>
              <button
                onClick={handleCancel}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 transition-colors duration-200 flex items-center justify-center"
                aria-label="Close modal"
              >
                <X size={16} style={{ color: luminousTokens.colors.text.body }} />
              </button>
            </div>

            {/* Brand List */}
            <div className="p-6 max-h-96 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-6 h-6 rounded-full border-2 border-purple-500/30 border-t-purple-500 animate-spin" />
                  <span 
                    className="ml-3 text-sm"
                    style={{ color: luminousTokens.colors.text.muted }}
                  >
                    Loading brands...
                  </span>
                </div>
              ) : brands.length === 0 ? (
                <div className="text-center py-8">
                  <p 
                    className="text-sm"
                    style={{ color: luminousTokens.colors.text.muted }}
                  >
                    No brands available
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {brands.map((brand) => (
                    <button
                      key={brand.id}
                      onClick={() => handleBrandSelect(brand.id)}
                      className={`w-full p-4 rounded-xl border transition-all duration-200 flex items-center gap-3 text-left ${
                        tempSelectedId === brand.id
                          ? 'border-purple-500/50 bg-purple-500/10'
                          : 'border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/20'
                      }`}
                    >
                      {/* Radio Button */}
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                        tempSelectedId === brand.id
                          ? 'border-purple-500 bg-purple-500'
                          : 'border-white/30'
                      }`}>
                        {tempSelectedId === brand.id && (
                          <Check size={12} className="text-white" />
                        )}
                      </div>

                      {/* Brand Logo */}
                      <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center">
                        {brand.logoUrl ? (
                          <img
                            src={brand.logoUrl}
                            alt={`${brand.name} logo`}
                            className="max-w-10 max-h-10 object-contain"
                            onError={(e) => {
                              // Hide the image and show Sparkles fallback
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                              const container = target.parentElement;
                              if (container) {
                                container.innerHTML = `<svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="${luminousTokens.colors.accent.purple}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.582a.5.5 0 0 1 0 .963L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>`;
                              }
                            }}
                          />
                        ) : (
                          <Sparkles 
                            size={38} 
                            style={{ color: luminousTokens.colors.accent.purple }}
                          />
                        )}
                      </div>

                      {/* Brand Info */}
                      <div className="flex-1 min-w-0">
                        <div 
                          className="font-medium truncate"
                          style={{ color: luminousTokens.colors.text.high }}
                        >
                          {brand.name}
                        </div>
                        {(brand.colorCount !== undefined || brand.ruleCount !== undefined) && (
                          <div 
                            className="text-xs mt-1"
                            style={{ color: luminousTokens.colors.text.muted }}
                          >
                            {brand.colorCount !== undefined && `${brand.colorCount} colors`}
                            {brand.colorCount !== undefined && brand.ruleCount !== undefined && ' · '}
                            {brand.ruleCount !== undefined && `${brand.ruleCount} rules`}
                          </div>
                        )}
                        {brand.archetype && (
                          <div 
                            className="text-xs mt-1"
                            style={{ color: luminousTokens.colors.text.muted }}
                          >
                            {brand.archetype}
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-white/10">
              <button
                onClick={handleCancel}
                className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors duration-200"
                style={{ color: luminousTokens.colors.text.body }}
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={!tempSelectedId}
                className="px-4 py-2 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium transition-all duration-200"
                style={{
                  boxShadow: tempSelectedId ? luminousTokens.effects.glow : 'none',
                }}
              >
                Select Brand
              </button>
            </div>
          </GlassPanel>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};