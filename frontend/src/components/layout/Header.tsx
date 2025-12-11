import React, { useState } from 'react';
import { Command, ChevronDown, Plus, LayoutGrid } from 'lucide-react';
import { MigratedPhysicalButton as PhysicalButton, IndustrialUserAvatar } from '../physical';
import type { Brand } from '../../types';

interface HeaderProps {
  activeBrand: Brand | null;
  allBrands: Brand[];
  onSelectBrand: (brandId: string) => void;
  onToggleVault: () => void;
  onAddBrand: () => void;
  onShowDemo?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeBrand,
  allBrands,
  onSelectBrand,
  onToggleVault,
  onAddBrand,
  onShowDemo,
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="h-16 px-6 flex items-center justify-between z-20 shrink-0 bg-background/80 backdrop-blur-md">
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
        {/* Demo Button */}
        {onShowDemo && (
          <PhysicalButton
            variant="default"
            onClick={onShowDemo}
            className="!px-3 !h-9 gap-2 text-accent"
          >
            <span className="hidden md:inline">DESIGN SYSTEM</span>
          </PhysicalButton>
        )}

        {/* The Vault Toggle */}
        <PhysicalButton
          variant="default"
          onClick={onToggleVault}
          className="!px-3 !h-9 gap-2 text-ink-muted"
        >
          <LayoutGrid size={16} />
          <span className="hidden md:inline">VAULT</span>
        </PhysicalButton>

        {/* User Avatar - handles both profile and settings */}
        <IndustrialUserAvatar 
          size="md" 
          role="operator"
          status="online"
          className="hover:scale-105 transition-transform duration-200"
          onClick={() => {
            // TODO: Open user menu with profile AND settings options
            console.log('User menu clicked - will show profile, settings, logout, etc.');
          }}
        />
      </div>
    </header>
  );
};

export default Header;
