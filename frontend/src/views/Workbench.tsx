import React, { useState, useEffect } from 'react';
// Removed ImageIcon import - using technical standby state instead
import { MigratedRecessedScreen as RecessedScreen, MigratedStatusBadge as StatusBadge, HardwareScrew } from '../components/physical';
import { MigratedDataPlate as DataPlate, AuditReceipt, MigratedCockpitInput as CockpitInput } from '../components/persona';
import { GenerationHistory } from '../components/persona/GenerationHistory';
import { LayoutDebugger } from '../utils/LayoutDebugger';
import { MeasurementTool } from '../utils/MeasurementTool';
import { useGeneration } from '../api/hooks';
import type { Brand, Violation } from '../types';

interface WorkbenchProps {
  activeBrand: Brand | null;
}

export const Workbench: React.FC<WorkbenchProps> = ({ activeBrand }) => {
  const { generate, tweak, approve, isGenerating, currentJob, error } = useGeneration();

  const [showAudit, setShowAudit] = useState(false);

  // Auto-show audit when job reaches needs_review state
  useEffect(() => {
    if (currentJob?.status === 'needs_review' && currentJob.violations) {
      setShowAudit(true);
    }
  }, [currentJob?.status]);

  const handleGenerate = async (prompt: string) => {
    if (!activeBrand) {
      console.error('No active brand selected');
      return;
    }

    try {
      setShowAudit(false);
      await generate(activeBrand.id, prompt);
    } catch (err) {
      console.error('Generation failed:', err);
    }
  };

  const handleAutoCorrect = async () => {
    if (!currentJob?.job_id || !currentJob.violations?.[0]) return;

    try {
      setShowAudit(false);

      // Build tweak instructions from first violation
      const violation = currentJob.violations[0];
      const instructions = violation.fix_suggestion
        ? `Apply fix for ${violation.category}: ${violation.fix_suggestion}`
        : `Fix ${violation.category}: ${violation.description}`;

      await tweak(currentJob.job_id, instructions);
    } catch (err) {
      console.error('Auto-correct failed:', err);
    }
  };

  const handleIgnore = async () => {
    if (!currentJob?.job_id) return;

    try {
      await approve(currentJob.job_id);
      setShowAudit(false);
    } catch (err) {
      console.error('Approve failed:', err);
    }
  };

  // Convert API violations to component format
  const violations: Violation[] = currentJob?.violations?.map(v => ({
    category: v.category,
    ruleId: v.category, // API doesn't provide ruleId, use category
    description: v.description,
    fixSuggestion: v.fix_suggestion || '',
    severity: v.severity,
  })) || [];

  // Show error state
  if (error) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="text-center">
          <div className="text-accent mb-4">⚠️</div>
          <p className="text-ink-muted">{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 flex flex-col p-6 relative surface-texture">
      {/* BRAND GUARDIAN: The Data Plate (Top Left) - Identity Core Module */}
      <DataPlate brand={activeBrand} />

      {/* GENERATION MEMORY: The History Panel (Top Right) - Recent Generations */}
      {/* Position: starts at center + half viewport width (448px) + gap (32px) */}
      <div
        className="hidden xl:block absolute top-24 z-0 w-56"
        style={{ left: 'calc(50% + 448px + 32px)' }}
      >
        <GenerationHistory />
      </div>

      {/* Main Content Area - Centered horizontally but flows vertically */}
      <div className="flex-1 flex flex-col items-center justify-center">
        {/* The Machine Housing - Main Viewport Module */}
        <div className="w-full max-w-4xl aspect-video relative group transition-all duration-500 z-10">
        
        {/* Cooling Vents - Bottom Edge */}
        <div className="absolute bottom-1 left-8 right-8 h-2 cooling-vents rounded-sm opacity-60"></div>
        {/* The Deep Screen - Industrial Viewport */}
        <RecessedScreen 
          className="w-full h-full flex items-center justify-center" 
          showTechnicalGrid={true}
          gridColor="#3b82f6"
          glassEffect={true}
        >
          {isGenerating ? (
            <GeneratingState status={currentJob?.status} progress={currentJob?.progress || 0} />
          ) : (
            <PreviewState
              imageUrl={currentJob?.current_image_url || null}
              score={currentJob?.compliance_score || null}
              onScoreClick={() => setShowAudit(!showAudit)}
            />
          )}
        </RecessedScreen>

        </div>

        {/* OPERATOR: The Cockpit Control Deck - Positioned below the viewport */}
        <div className="mt-12 w-full max-w-4xl flex justify-center">
          <CockpitInput
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
            initialValue="LinkedIn post for Q3 earnings"
          />
        </div>
      </div>

      {/* OPERATOR: The Audit Receipt (Slides up) */}
      {showAudit && violations.length > 0 && (
        <AuditReceipt
          violations={violations}
          onClose={() => setShowAudit(false)}
          onAutoCorrect={handleAutoCorrect}
          onIgnore={handleIgnore}
        />
      )}

      {/* Debug Tools - Press 'D' for layout guides, 'M' for measurements */}
      <LayoutDebugger />
      <MeasurementTool />
    </main>
  );
};

// --- Sub-components ---

interface GeneratingStateProps {
  status?: string;
  progress: number;
}

const GeneratingState: React.FC<GeneratingStateProps> = ({ status, progress }) => {
  const statusLabels: Record<string, string> = {
    pending: 'Initializing...',
    processing: 'Processing Request...',
    generating: 'Generating Assets...',
    auditing: 'Auditing Compliance...',
    correcting: 'Applying Corrections...',
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="w-16 h-16 rounded-full border-4 border-ink-muted/20 border-t-accent animate-spin" />
      <span className="font-mono text-xs text-ink-muted uppercase tracking-widest">
        {status ? statusLabels[status] || 'Processing...' : 'Generating Assets...'}
      </span>
      {progress > 0 && progress < 100 && (
        <div className="w-48 h-2 bg-ink/10 rounded-full overflow-hidden shadow-pressed">
          <div
            className="h-full bg-accent transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
};

interface PreviewStateProps {
  imageUrl: string | null;
  score: number | null;
  onScoreClick: () => void;
}

const PreviewState: React.FC<PreviewStateProps> = ({
  imageUrl,
  score,
  onScoreClick,
}) => (
  <div className="relative w-full h-full flex items-center justify-center">
    {imageUrl ? (
      <img
        src={imageUrl}
        alt="Generated asset"
        className="max-w-full max-h-full object-contain rounded-lg"
      />
    ) : (
      <div className="text-center opacity-40 flex flex-col items-center gap-6 system-standby">
        <div className="text-2xl font-bold tracking-wider text-blue-600/60 standby-indicator">
          SYSTEM READY
        </div>
        <div className="w-16 h-px bg-blue-600/30"></div>
        <div className="text-lg tracking-widest text-gray-500">
          AWAITING INPUT
        </div>
        <div className="grid grid-cols-3 gap-2 mt-4">
          {[...Array(9)].map((_, i) => (
            <div 
              key={i} 
              className="w-2 h-2 border border-blue-600/20 bg-blue-600/5 standby-indicator"
              style={{ animationDelay: `${i * 0.1}s` }}
            />
          ))}
        </div>
        
        {/* Technical Readout */}
        <div className="mt-6 text-xs text-gray-400 tracking-widest opacity-60">
          <div>VIEWPORT: ACTIVE</div>
          <div>GRID: ENABLED</div>
          <div>STATUS: STANDBY</div>
        </div>
      </div>
    )}

    {/* OPERATOR: The Confidence Score (Top Right) */}
    {score !== null && (
      <div className="absolute top-6 right-6 z-20">
        <StatusBadge score={score} onClick={onScoreClick} />
      </div>
    )}
  </div>
);

export default Workbench;
