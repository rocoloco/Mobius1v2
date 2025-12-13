import { useState } from 'react';
import { ComplianceGauge } from '../ComplianceGauge';

/**
 * ComplianceGauge Demo Page
 * 
 * Interactive demo showcasing the ComplianceGauge with:
 * - Different score values and color thresholds
 * - Violation list with severity grouping
 * - Clickable violations
 */
export function ComplianceGaugeDemo() {
  const [score, setScore] = useState(88);
  const [clickedViolation, setClickedViolation] = useState<string | null>(null);

  const mockViolations = [
    {
      id: 'v1',
      severity: 'critical' as const,
      message: 'Logo margin too small (8px, minimum 16px required)',
    },
    {
      id: 'v2',
      severity: 'critical' as const,
      message: 'Unauthorized font family detected: Arial',
    },
    {
      id: 'v3',
      severity: 'warning' as const,
      message: 'Color #2664EC is 1.2% off from brand color #2563EB',
    },
    {
      id: 'v4',
      severity: 'warning' as const,
      message: 'Text contrast ratio 4.2:1 (recommended 4.5:1)',
    },
    {
      id: 'v5',
      severity: 'info' as const,
      message: 'Consider using brand tagline for consistency',
    },
  ];

  const handleViolationClick = (violationId: string) => {
    setClickedViolation(violationId);
    setTimeout(() => setClickedViolation(null), 2000);
  };

  return (
    <div className="min-h-screen bg-[#101012] p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-white">ComplianceGauge Component Demo</h1>
          <p className="text-slate-400">Radial donut chart with violation list</p>
        </div>

        {/* Demo Controls */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white">Demo Controls</h2>
          
          <div className="space-y-4">
            {/* Score Slider */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Compliance Score: {score}%
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={score}
                onChange={(e) => setScore(Number(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>0% (Critical)</span>
                <span>70% (Review)</span>
                <span>95% (Pass)</span>
                <span>100%</span>
              </div>
            </div>

            {/* Preset Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => setScore(98)}
                className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg transition-colors"
              >
                Pass (98%)
              </button>
              
              <button
                onClick={() => setScore(85)}
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 text-white rounded-lg transition-colors"
              >
                Review (85%)
              </button>
              
              <button
                onClick={() => setScore(45)}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors"
              >
                Critical (45%)
              </button>
            </div>
          </div>

          {/* Color Threshold Info */}
          <div className="text-sm text-slate-400 bg-white/5 rounded-lg p-4">
            <p><strong>Color Thresholds:</strong></p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li className="text-green-400">≥95%: Green (Pass) - #10B981</li>
              <li className="text-yellow-400">70-95%: Amber (Review) - #F59E0B</li>
              <li className="text-red-400">&lt;70%: Red (Critical) - #EF4444</li>
            </ul>
          </div>

          {clickedViolation && (
            <div className="bg-purple-600/20 border border-purple-500/50 rounded-lg p-4">
              <p className="text-purple-300 text-sm">
                <strong>Violation Clicked:</strong> {clickedViolation}
              </p>
              <p className="text-purple-400 text-xs mt-1">
                In the real dashboard, this would highlight the corresponding bounding box on the Canvas
              </p>
            </div>
          )}
        </div>

        {/* Demo Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Demo */}
          <div className="md:col-span-2">
            <div className="h-[700px]">
              <ComplianceGauge
                score={score}
                violations={mockViolations}
                onViolationClick={handleViolationClick}
              />
            </div>
          </div>

          {/* Side Info */}
          <div className="space-y-6">
            {/* Violation Breakdown */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Violation Breakdown</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-red-400 text-sm">Critical</span>
                  <span className="text-white font-mono">2</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-yellow-400 text-sm">Warning</span>
                  <span className="text-white font-mono">2</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-400 text-sm">Info</span>
                  <span className="text-white font-mono">1</span>
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Features to Test</h3>
              <ul className="list-disc list-inside text-slate-400 space-y-2 text-sm">
                <li>Adjust score slider to see color changes</li>
                <li>Click violations to trigger focus event</li>
                <li>Scroll violation list</li>
                <li>Observe severity grouping (Critical → Warning → Info)</li>
                <li>Watch gauge animation</li>
              </ul>
            </div>

            {/* Empty State Demo */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Empty State</h3>
              <div className="h-[300px]">
                <ComplianceGauge
                  score={100}
                  violations={[]}
                  onViolationClick={() => {}}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
