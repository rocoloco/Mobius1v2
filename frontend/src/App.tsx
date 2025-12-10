import React, { useState } from 'react';
import { BrandProvider, useBrandContext } from './context';
import { Header, Vault } from './components/layout';
import { Workbench, Onboarding } from './views';

type View = 'workbench' | 'onboard';

const AppContent: React.FC = () => {
  const { brands, activeBrand, assets, setActiveBrandId, addBrand } = useBrandContext();

  const [isVaultOpen, setIsVaultOpen] = useState(false);
  const [view, setView] = useState<View>('workbench');

  // First-time user flow: if no brands, show onboarding
  const shouldShowOnboarding = brands.length === 0 || view === 'onboard';

  if (shouldShowOnboarding) {
    return (
      <Onboarding
        onComplete={(brandId) => {
          // In real implementation, this would add the new brand
          addBrand({
            id: brandId,
            name: 'New Brand',
            archetype: 'THE CREATOR',
            color: '#6c5ce7',
            voiceVectors: {
              formal: 0.5,
              witty: 0.5,
              technical: 0.5,
              urgent: 0.5,
            },
          });
          setView('workbench');
        }}
        onCancel={brands.length > 0 ? () => setView('workbench') : undefined}
      />
    );
  }

  return (
    <div className="h-screen w-full bg-background text-ink font-sans overflow-hidden flex flex-col relative selection:bg-accent selection:text-white">
      {/* HEADER */}
      <Header
        activeBrand={activeBrand}
        allBrands={brands}
        onSelectBrand={setActiveBrandId}
        onToggleVault={() => setIsVaultOpen(!isVaultOpen)}
        onAddBrand={() => setView('onboard')}
      />

      {/* MAIN WORKSPACE */}
      <div className="flex-1 relative flex overflow-hidden">
        {/* The Workbench (Canvas) */}
        <div
          className={`flex-1 transition-all duration-500 ${
            isVaultOpen ? 'mr-96' : 'mr-0'
          }`}
        >
          <Workbench activeBrand={activeBrand} />
        </div>

        {/* THE VAULT (Slide-out Gallery) */}
        <Vault
          isOpen={isVaultOpen}
          onClose={() => setIsVaultOpen(false)}
          assets={assets}
          onAssetClick={(asset) => {
            console.log('Asset clicked:', asset);
            // In real implementation, this could load the asset into the canvas
          }}
        />
      </div>
    </div>
  );
};

function App() {
  return (
    <BrandProvider>
      <AppContent />
    </BrandProvider>
  );
}

export default App;
