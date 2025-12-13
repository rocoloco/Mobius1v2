import { useState } from 'react';
import { Canvas } from '../Canvas';

/**
 * Canvas Component Demo
 * 
 * Interactive demonstration of the Canvas organism component
 * showing different states and interactions.
 */
export function CanvasDemo() {
  const [status, setStatus] = useState<'generating' | 'auditing' | 'complete' | 'error'>('complete');
  const [currentVersion, setCurrentVersion] = useState(0);
  const [highlightedViolation, setHighlightedViolation] = useState<string | null>(null);

  const mockViolations = [
    {
      id: 'v1',
      severity: 'critical' as const,
      message: 'Logo too small',
      bounding_box: [10, 15, 25, 30] as [number, number, number, number],
    },
    {
      id: 'v2',
      severity: 'warning' as const,
      message: 'Color mismatch',
      bounding_box: [60, 20, 30, 25] as [number, number, number, number],
    },
    {
      id: 'v3',
      severity: 'critical' as const,
      message: 'Font not allowed',
      bounding_box: [15, 60, 40, 15] as [number, number, number, number],
    },
  ];

  const mockVersions = [
    {
      attempt_id: 1,
      image_url: 'https://via.placeholder.com/800x600/7C3AED/FFFFFF?text=Version+1',
      thumb_url: 'https://via.placeholder.com/80x80/7C3AED/FFFFFF?text=V1',
      score: 72,
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      prompt: 'Create a LinkedIn post with brand colors',
    },
    {
      attempt_id: 2,
      image_url: 'https://via.placeholder.com/800x600/2563EB/FFFFFF?text=Version+2',
      thumb_url: 'https://via.placeholder.com/80x80/2563EB/FFFFFF?text=V2',
      score: 88,
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      prompt: 'Fix the logo size issue',
    },
    {
      attempt_id: 3,
      image_url: 'https://via.placeholder.com/800x600/10B981/FFFFFF?text=Version+3',
      thumb_url: 'https://via.placeholder.com/80x80/10B981/FFFFFF?text=V3',
      score: 96,
      timestamp: new Date().toISOString(),
      prompt: 'Make it more professional',
    },
  ];

  const currentImageUrl = mockVersions[currentVersion]?.image_url;
  const currentScore = mockVersions[currentVersion]?.score || 0;

  return (
    <div className="min-h-screen bg-[#101012] p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-2">Canvas Component Demo</h1>
        <p className="text-white/60 mb-8">
          Interactive demonstration of the Canvas organism component
        </p>

        {/* Controls */}
        <div className="mb-6 p-4 bg-white/5 rounded-lg border border-white/10">
          <h2 className="text-white font-semibold mb-3">Controls</h2>
          <div className="flex gap-4 flex-wrap">
            <button
              onClick={() => setStatus('generating')}
              className={`px-4 py-2 rounded-lg ${
                status === 'generating'
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/10 text-white/60 hover:bg-white/20'
              }`}
            >
              Generating
            </button>
            <button
              onClick={() => setStatus('auditing')}
              className={`px-4 py-2 rounded-lg ${
                status === 'auditing'
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/10 text-white/60 hover:bg-white/20'
              }`}
            >
              Auditing
            </button>
            <button
              onClick={() => setStatus('complete')}
              className={`px-4 py-2 rounded-lg ${
                status === 'complete'
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/10 text-white/60 hover:bg-white/20'
              }`}
            >
              Complete
            </button>
            <button
              onClick={() => setStatus('error')}
              className={`px-4 py-2 rounded-lg ${
                status === 'error'
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/10 text-white/60 hover:bg-white/20'
              }`}
            >
              Error
            </button>
          </div>

          <div className="mt-4">
            <h3 className="text-white/80 text-sm mb-2">Highlight Violation:</h3>
            <div className="flex gap-2">
              <button
                onClick={() => setHighlightedViolation(null)}
                className={`px-3 py-1 rounded text-sm ${
                  highlightedViolation === null
                    ? 'bg-purple-600 text-white'
                    : 'bg-white/10 text-white/60 hover:bg-white/20'
                }`}
              >
                None
              </button>
              {mockViolations.map((v) => (
                <button
                  key={v.id}
                  onClick={() => setHighlightedViolation(v.id)}
                  className={`px-3 py-1 rounded text-sm ${
                    highlightedViolation === v.id
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/10 text-white/60 hover:bg-white/20'
                  }`}
                >
                  {v.id}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Canvas Component */}
        <div className="h-[600px]">
          <Canvas
            imageUrl={status === 'complete' || status === 'auditing' ? currentImageUrl : undefined}
            violations={mockViolations}
            versions={mockVersions}
            currentVersion={currentVersion}
            complianceScore={currentScore}
            status={status}
            highlightedViolationId={highlightedViolation}
            onVersionChange={(index) => {
              setCurrentVersion(index);
              console.log('Version changed to:', index);
            }}
            onAcceptCorrection={() => {
              console.log('Accept correction clicked');
              alert('Auto-correction accepted! (Demo)');
            }}
          />
        </div>

        {/* Info */}
        <div className="mt-6 p-4 bg-white/5 rounded-lg border border-white/10">
          <h2 className="text-white font-semibold mb-2">Current State</h2>
          <div className="text-white/60 text-sm space-y-1">
            <p>Status: <span className="text-white">{status}</span></p>
            <p>Current Version: <span className="text-white">{currentVersion + 1} / {mockVersions.length}</span></p>
            <p>Compliance Score: <span className="text-white">{currentScore}%</span></p>
            <p>Violations: <span className="text-white">{mockViolations.length}</span></p>
            <p>Highlighted: <span className="text-white">{highlightedViolation || 'None'}</span></p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CanvasDemo;
