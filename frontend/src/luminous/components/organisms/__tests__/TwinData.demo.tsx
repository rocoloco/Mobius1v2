import { useState } from 'react';
import { TwinData } from '../TwinData';

/**
 * TwinData Demo Page
 * 
 * Interactive demo showcasing the TwinData inspector with:
 * - Color swatches comparing detected vs brand colors
 * - Font detection with compliance status
 * - Different data scenarios
 */
export function TwinDataDemo() {
  const [scenario, setScenario] = useState<'full' | 'partial' | 'empty'>('full');

  const scenarios = {
    full: {
      detectedColors: ['#2664EC', '#10B981', '#F59E0B', '#EF4444'],
      brandColors: ['#2563EB', '#10B981', '#F59E0B', '#DC2626'],
      detectedFonts: [
        { family: 'Inter', weight: 'Bold', allowed: true },
        { family: 'Inter', weight: 'Regular', allowed: true },
        { family: 'JetBrains Mono', weight: 'Medium', allowed: true },
        { family: 'Arial', weight: 'Bold', allowed: false },
      ],
    },
    partial: {
      detectedColors: ['#2563EB', '#10B981'],
      brandColors: ['#2563EB', '#10B981', '#F59E0B'],
      detectedFonts: [
        { family: 'Inter', weight: 'Bold', allowed: true },
      ],
    },
    empty: {
      detectedColors: [],
      brandColors: ['#2563EB', '#10B981', '#F59E0B'],
      detectedFonts: [],
    },
  };

  const currentData = scenarios[scenario];

  return (
    <div className="min-h-screen bg-[#101012] p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-white">TwinData Component Demo</h1>
          <p className="text-slate-400">Visual token inspector (colors & fonts)</p>
        </div>

        {/* Demo Controls */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white">Demo Controls</h2>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm text-slate-400 mb-3">Select a data scenario:</p>
              
              <div className="flex gap-4">
                <button
                  onClick={() => setScenario('full')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    scenario === 'full'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/5 text-slate-400 hover:bg-white/10'
                  }`}
                >
                  Full Data
                </button>
                
                <button
                  onClick={() => setScenario('partial')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    scenario === 'partial'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/5 text-slate-400 hover:bg-white/10'
                  }`}
                >
                  Partial Data
                </button>
                
                <button
                  onClick={() => setScenario('empty')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    scenario === 'empty'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/5 text-slate-400 hover:bg-white/10'
                  }`}
                >
                  Empty State
                </button>
              </div>
            </div>
          </div>

          <div className="text-sm text-slate-400 bg-white/5 rounded-lg p-4">
            <p><strong>Current Scenario:</strong> {scenario}</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Detected Colors: {currentData.detectedColors.length}</li>
              <li>Brand Colors: {currentData.brandColors.length}</li>
              <li>Detected Fonts: {currentData.detectedFonts.length}</li>
            </ul>
          </div>
        </div>

        {/* Demo Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Demo */}
          <div className="md:col-span-2">
            <div className="h-[700px]">
              <TwinData
                detectedColors={currentData.detectedColors}
                brandColors={currentData.brandColors}
                detectedFonts={currentData.detectedFonts}
              />
            </div>
          </div>

          {/* Side Info */}
          <div className="space-y-6">
            {/* Color Distance Explanation */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Color Distance</h3>
              <div className="space-y-3 text-sm">
                <p className="text-slate-400">
                  Each color swatch shows:
                </p>
                <ul className="list-disc list-inside text-slate-400 space-y-1 text-xs">
                  <li>Left half: Detected color</li>
                  <li>Right half: Nearest brand color</li>
                  <li>Tooltip: Distance metric</li>
                  <li>Pass/Fail indicator</li>
                </ul>
                <div className="bg-white/5 rounded p-3 mt-3">
                  <p className="text-xs text-slate-400">
                    <strong className="text-green-400">Pass:</strong> Distance &lt; 5%
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    <strong className="text-red-400">Fail:</strong> Distance ≥ 5%
                  </p>
                </div>
              </div>
            </div>

            {/* Font Compliance */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Font Compliance</h3>
              <div className="space-y-3 text-sm">
                <p className="text-slate-400">
                  Each font shows:
                </p>
                <ul className="list-disc list-inside text-slate-400 space-y-1 text-xs">
                  <li>Font family and weight</li>
                  <li>Compliance status badge</li>
                  <li>Monospace formatting</li>
                </ul>
                <div className="bg-white/5 rounded p-3 mt-3">
                  <p className="text-xs text-green-400">
                    <strong>(Allowed)</strong> - Font is in brand guidelines
                  </p>
                  <p className="text-xs text-red-400 mt-1">
                    <strong>(Forbidden)</strong> - Font violates guidelines
                  </p>
                </div>
              </div>
            </div>

            {/* Example Data */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Example Colors</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded" style={{ backgroundColor: '#2664EC' }}></div>
                  <span className="text-xs font-mono text-slate-400">#2664EC</span>
                  <span className="text-xs text-slate-500">→</span>
                  <div className="w-6 h-6 rounded" style={{ backgroundColor: '#2563EB' }}></div>
                  <span className="text-xs font-mono text-slate-400">#2563EB</span>
                </div>
                <p className="text-xs text-slate-400">
                  Detected color is 1.2% off from brand color
                </p>
              </div>
            </div>

            {/* Features */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Features to Test</h3>
              <ul className="list-disc list-inside text-slate-400 space-y-2 text-sm">
                <li>Switch between scenarios</li>
                <li>Hover over color swatches for distance tooltip</li>
                <li>Observe split pill design for colors</li>
                <li>Check font compliance badges</li>
                <li>Scroll through long lists</li>
                <li>View empty states</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
