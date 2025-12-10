import React, { useState } from 'react';
import { Command, ChevronDown, Plus, LayoutGrid, Settings } from 'lucide-react';
import { PhysicalButton } from '../physical';
import type { Brand } from '../../types';

interface HeaderProps {
  activeBrand: Brand | null;
  allBrands: Brand[];
  onSelectBrand: (brandId: string) => void;
  onToggleVault: () => void;
  onAddBrand: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeBrand,
  allBrands,
  onSelectBrand,
  onToggleVault,
  onAddBrand,
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="h-16 px-6 flex items-center justify-between z-20 shrink-0 bg-background/80 backdrop-blur-md border-b border-white/20">
      {/* LEFT: The Cartridge Slot */}
      <div className="relative">
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="flex items-center gap-4 group p-2 rounded-xl hover:bg-surface transition-colors"
        >
          {/* Logo Icon */}
          <div className="w-10 h-10 rounded-xl bg-surface shadow-soft flex items-center justify-center text-accent group-hover:scale-95 transition-transform">
            <Command size={20} strokeWidth={3} />
          </div>

          {/* Text Info */}
          <div className="flex flex-col items-start justify-center h-full">
            <span className="font-black text-xs tracking-tight leading-none mb-1 text-ink/40">
              MOBIUS<span className="font-normal">OS</span>
            </span>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-success shadow-glow-success" />
              <span className="text-xs text-ink font-bold font-mono uppercase tracking-wider leading-none">
                {activeBrand?.name || 'SELECT BRAND'}
              </span>
              <ChevronDown size={10} className="text-ink-muted" />
            </div>
          </div>
        </button>

        {/* The Dropdown Menu (Cartridge Case) */}
        {isMenuOpen && (
          <>
            {/* Backdrop to close menu */}
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsMenuOpen(false)}
            />

            <div className="absolute top-16 left-0 w-64 bg-surface shadow-soft rounded-xl p-2 border border-white/40 z-20 animate-slide-in-from-top animate-fade-in">
              <div className="text-[9px] font-bold text-ink-muted uppercase tracking-widest px-3 py-2">
                Select Cartridge
              </div>

              {allBrands.map((brand) => (
                <button
                  key={brand.id}
                  onClick={() => {
                    onSelectBrand(brand.id);
                    setIsMenuOpen(false);
                  }}
                  className={`
                    w-full text-left px-3 py-2.5 rounded-lg text-xs font-mono mb-1
                    flex items-center gap-2 transition-colors
                    ${activeBrand?.id === brand.id
                      ? 'bg-ink/5 text-ink font-bold'
                      : 'text-ink-muted hover:bg-white/50'
                    }
                  `}
                >
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: brand.color }}
                  />
                  {brand.name}
                </button>
              ))}

              <div className="h-px bg-ink/5 my-1" />

              <button
                onClick={() => {
                  onAddBrand();
                  setIsMenuOpen(false);
                }}
                className="w-full text-left px-3 py-2 rounded-lg text-xs font-bold text-accent hover:bg-accent/5 flex items-center gap-2"
              >
                <Plus size={12} /> New Brand...
              </button>
            </div>
          </>
        )}
      </div>

      {/* RIGHT: Global Tools */}
      <div className="flex items-center gap-3">
        {/* The Vault Toggle */}
        <PhysicalButton
          variant="default"
          onClick={onToggleVault}
          className="!px-3 !h-9 gap-2 text-ink-muted"
        >
          <LayoutGrid size={16} />
          <span className="hidden md:inline">VAULT</span>
        </PhysicalButton>

        <PhysicalButton variant="icon" className="!w-9 !h-9">
          <Settings size={16} />
        </PhysicalButton>

        {/* User Avatar */}
        <div className="w-9 h-9 rounded-full bg-surface flex items-center justify-center overflow-hidden border-2 border-surface shadow-soft">
          <img
            src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
            alt="User"
            className="w-full h-full"
          />
        </div>
      </div>
    </header>
  );
};

export default Header;
