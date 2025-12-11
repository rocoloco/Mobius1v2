import React from 'react';
import { X, Download, Copy } from 'lucide-react';
import { MigratedStatusBadge as StatusBadge } from '../physical';
import type { Asset } from '../../types';

interface VaultProps {
  isOpen: boolean;
  onClose: () => void;
  assets: Asset[];
  onAssetClick?: (asset: Asset) => void;
}

export const Vault: React.FC<VaultProps> = ({
  isOpen,
  onClose,
  assets,
  onAssetClick,
}) => {
  // Group assets by date
  const groupedAssets = assets.reduce((groups, asset) => {
    const date = new Date(asset.createdAt).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
    if (!groups[date]) groups[date] = [];
    groups[date].push(asset);
    return groups;
  }, {} as Record<string, Asset[]>);

  return (
    <div
      className={`
        absolute top-0 right-0 h-full w-96
        bg-surface shadow-[-10px_0_30px_rgba(0,0,0,0.05)]
        border-l border-white/50 z-30
        transition-transform duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]
        ${isOpen ? 'translate-x-0' : 'translate-x-full'}
      `}
    >
      {/* Header */}
      <div className="h-16 border-b border-ink/5 flex items-center justify-between px-6">
        <span className="font-bold text-xs uppercase tracking-widest text-ink">
          Asset Vault
        </span>
        <button
          onClick={onClose}
          className="text-ink-muted hover:text-ink transition-colors"
        >
          <X size={16} />
        </button>
      </div>

      {/* Scrollable Grid */}
      <div className="p-4 overflow-y-auto h-[calc(100vh-64px)] space-y-4">
        {assets.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-ink-muted/50 text-sm font-mono">
              No assets generated yet
            </div>
          </div>
        ) : (
          Object.entries(groupedAssets).map(([date, dateAssets]) => (
            <div key={date}>
              {/* Date Header */}
              <div className="text-[10px] font-mono text-ink-muted/50 uppercase text-center mb-3">
                {date === new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                  ? 'Today'
                  : date
                }
              </div>

              {/* Asset Cards */}
              <div className="space-y-4">
                {dateAssets.map((asset) => (
                  <AssetCard
                    key={asset.id}
                    asset={asset}
                    onClick={() => onAssetClick?.(asset)}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

interface AssetCardProps {
  asset: Asset;
  onClick?: () => void;
}

const AssetCard: React.FC<AssetCardProps> = ({ asset, onClick }) => {
  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    // Copy image URL to clipboard
    navigator.clipboard.writeText(asset.imageUrl);
  };

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    // Trigger download
    window.open(asset.imageUrl, '_blank');
  };

  return (
    <div
      onClick={onClick}
      className="
        bg-[#f4f6f8] rounded-xl p-3 shadow-pressed border border-white/50
        group cursor-pointer hover:scale-[1.02] transition-transform
      "
    >
      {/* Image Preview */}
      <div className="aspect-square bg-gray-200 rounded-lg mb-3 overflow-hidden relative">
        {asset.imageUrl ? (
          <img
            src={asset.imageUrl}
            alt={asset.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs text-ink-muted font-mono">
              {asset.name}
            </span>
          </div>
        )}

        {/* Score Badge - shows on hover */}
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <StatusBadge score={asset.complianceScore} animate={false} />
        </div>
      </div>

      {/* Footer */}
      <div className="flex justify-between items-center">
        <span className="text-[10px] font-bold text-ink-muted truncate w-24">
          {asset.name}
        </span>
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleCopy}
            className="text-ink-muted hover:text-accent transition-colors"
          >
            <Copy size={12} />
          </button>
          <button
            onClick={handleDownload}
            className="text-ink-muted hover:text-accent transition-colors"
          >
            <Download size={12} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Vault;
