import React, { useState, useEffect } from 'react';
import { Image as ImageIcon } from 'lucide-react';
import { RecessedScreen, StatusBadge, HardwareScrew } from '../components/physical';
import { DataPlate, AuditReceipt, CockpitInput } from '../components/persona';
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
    <main className="flex-1 flex flex-col items-center justify-center p-6 pb-32 relative">
      {/* BRAND GUARDIAN: The Data Plate (Top Left) */}
      <DataPlate brand={activeBrand} />

      {/* The Machine Housing */}
      <div className="w-full max-w-4xl aspect-video bg-surface rounded-[2rem] shadow-soft p-3 relative group transition-all duration-500 z-10">
        {/* The Deep Screen */}
        <RecessedScreen className="w-full h-full flex items-center justify-center">
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

        {/* Hardware Screws */}
        <HardwareScrew className="absolute top-5 left-5" />
        <HardwareScrew className="absolute top-5 right-5" />
        <HardwareScrew className="absolute bottom-5 left-5" />
        <HardwareScrew className="absolute bottom-5 right-5" />
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

      {/* OPERATOR: The Cockpit Control Deck */}
      <CockpitInput
        onGenerate={handleGenerate}
        isGenerating={isGenerating}
        initialValue="LinkedIn post for Q3 earnings"
      />
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
      <div className="text-center opacity-30 flex flex-col items-center gap-4">
        <ImageIcon size={48} />
        <span className="font-black text-3xl tracking-tight text-ink">
          PREVIEW
        </span>
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
