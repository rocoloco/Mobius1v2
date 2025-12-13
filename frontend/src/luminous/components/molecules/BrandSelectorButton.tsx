import React from 'react';
import { Sparkles, ChevronDown } from 'lucide-react';
import { luminousTokens } from '../../tokens';

interface BrandGraphSummary {
  name: string;
  ruleCount: number;
  colorCount: number;
  archetype?: string;
  logoUrl?: string;
}

interface BrandSelectorButtonProps {
  brandGraph?: BrandGraphSummary | null;
  isGenerating?: boolean;
  onClick?: () => void;
  showSelectPrompt?: boolean;
  brandsLoading?: boolean;
}

/**
 * BrandSelectorButton - Button for selecting/displaying current brand
 * 
 * Shows either:
 * - "Select Brand" with pulsing highlight when no brand selected
 * - Brand name with attributes when brand is selected
 * - Loading state when brands are being fetched
 */
export const BrandSelectorButton: React.FC<BrandSelectorButtonProps> = ({
  brandGraph,
  isGenerating = false,
  onClick,
  showSelectPrompt = false,
  brandsLoading = false,
}) => {
  // Loading state
  if (brandsLoading && !brandGraph) {
    return (
      <div className="flex items-center gap-3 flex-1 min-w-0" style={{ padding: '6px 8px', marginLeft: '-8px' }}>
        <div className="w-4 h-4 rounded-full border-2 border-purple-500/30 border-t-purple-500 animate-spin flex-shrink-0" />
        <span 
          className="text-sm font-medium"
          style={{ color: luminousTokens.colors.text.muted }}
        >
          Loading brands...
        </span>
      </div>
    );
  }

  // Select brand prompt state - single row since it's just "Select Brand"
  if (showSelectPrompt || !brandGraph) {
    return (
      <button
        onClick={onClick}
        className="flex items-center gap-3 hover:bg-white/5 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50 rounded-lg cursor-pointer flex-1 min-w-0 animate-pulse"
        style={{ 
          padding: '6px 8px', 
          marginLeft: '-8px',
          backgroundColor: 'rgba(245, 158, 11, 0.1)', // Subtle amber highlight
          border: '1px solid rgba(245, 158, 11, 0.2)',
        }}
        data-testid="brand-selector-button"
        aria-label="Select a brand to get started"
      >
        <Sparkles 
          size={16} 
          className="flex-shrink-0"
          style={{ color: luminousTokens.colors.accent.purple }}
        />
        <span 
          className="text-sm font-medium truncate"
          style={{ color: luminousTokens.colors.text.high }}
        >
          Select Brand
        </span>
        <ChevronDown 
          size={14} 
          className="flex-shrink-0 ml-auto"
          style={{ color: luminousTokens.colors.text.muted }}
        />
      </button>
    );
  }

  // Brand selected state - two-row layout
  return (
    <button
      onClick={onClick}
      className="flex flex-col gap-1 hover:bg-white/5 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50 rounded-lg cursor-pointer flex-1 min-w-0"
      style={{ padding: '6px 8px', marginLeft: '-8px' }}
      data-testid="brand-graph-indicator"
      aria-label={`${brandGraph.name} Brand Graph. Click to change brand.`}
    >
      {/* Top row: Brand name with icon and chevron */}
      <div className="flex items-center gap-2 w-full">
        {/* Brand logo or fallback to Sparkles icon */}
        {brandGraph.logoUrl ? (
          <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center">
            <img
              src={brandGraph.logoUrl}
              alt={`${brandGraph.name} logo`}
              className={`max-w-10 max-h-10 object-contain ${isGenerating ? 'animate-pulse' : ''}`}
              onError={(e) => {
                // Hide the image and show Sparkles fallback
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                const container = target.parentElement;
                if (container) {
                  container.innerHTML = `<svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="${luminousTokens.colors.accent.purple}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${isGenerating ? 'animate-pulse' : ''}"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.582a.5.5 0 0 1 0 .963L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>`;
                }
              }}
            />
          </div>
        ) : (
          <Sparkles 
            size={38} 
            className={`flex-shrink-0 ${isGenerating ? 'animate-pulse' : ''}`}
            style={{ color: luminousTokens.colors.accent.purple }}
          />
        )}
        <span 
          className="text-sm font-medium truncate flex-1"
          style={{ color: luminousTokens.colors.text.high }}
        >
          {brandGraph.name}
        </span>
        <ChevronDown 
          size={14} 
          className="flex-shrink-0"
          style={{ color: luminousTokens.colors.text.muted }}
        />
      </div>
      
      {/* Bottom row: Details - centered */}
      <div className="flex items-center justify-center gap-2 w-full">
        <span 
          className="text-[11px] font-mono px-2 py-1 rounded-full"
          style={{ 
            color: luminousTokens.colors.text.muted,
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
          }}
        >
          {brandGraph.colorCount} colors{brandGraph.ruleCount > 0 ? ` · ${brandGraph.ruleCount} rules` : ''}
        </span>
        {brandGraph.archetype && (
          <span 
            className="text-[11px] hidden md:inline"
            style={{ color: luminousTokens.colors.text.muted }}
          >
            {brandGraph.archetype}
          </span>
        )}
      </div>
    </button>
  );
};