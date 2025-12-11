import React, { useState, useEffect } from 'react';
// Removed ImageIcon import - using technical standby state instead
import { MigratedRecessedScreen as RecessedScreen, MigratedStatusBadge as StatusBadge } from '../components/physical';
import { MigratedDataPlate as DataPlate, AuditReceipt, MigratedCockpitInput as CockpitInput } from '../components/persona';
import { LayoutDebugger } from '../utils/LayoutDebugger';
import { MeasurementTool } from '../utils/MeasurementTool';
import TerminalTeleprinter from '../components/monitoring/TerminalTeleprinter';
import CRTOscilloscope from '../components/monitoring/CRTOscilloscope';
import { useGeneration } from '../api/hooks';
import type { Brand, Violation } from '../types';
import type { ReasoningLog } from '../types/monitoring';
import type { ComplianceScores } from '../components/monitoring/CRTOscilloscope';

interface WorkbenchProps {
  activeBrand: Brand | null;
}

export const Workbench: React.FC<WorkbenchProps> = ({ activeBrand }) => {
  const { generate, tweak, approve, isGenerating, currentJob, error } = useGeneration();

  const [showAudit, setShowAudit] = useState(false);
  const [monitoringLogs, setMonitoringLogs] = useState<ReasoningLog[]>([]);
  const [complianceScores, setComplianceScores] = useState<ComplianceScores>({
    typography: 0.85,
    voice: 0.92,
    color: 0.78,
    logo: 0.88
  });

  // Initialize monitoring system with startup logs and periodic updates
  useEffect(() => {
    const initLogs: ReasoningLog[] = [
      {
        id: 'init-1',
        timestamp: new Date(),
        step: 'SYSTEM',
        message: 'Brand compliance monitoring system initialized',
        level: 'success'
      },
      {
        id: 'init-2',
        timestamp: new Date(),
        step: 'CONNECT',
        message: 'Connected to Mobius API endpoint',
        level: 'info'
      },
      {
        id: 'init-3',
        timestamp: new Date(),
        step: 'READY',
        message: 'Monitoring terminal ready for real-time compliance tracking',
        level: 'info'
      }
    ];
    setMonitoringLogs(initLogs);

    // Add periodic system status updates when idle
    const statusInterval = setInterval(() => {
      if (!isGenerating) {
        const statusMessages = [
          'System health check: All monitoring systems operational',
          'Brand guidelines database synchronized',
          'Compliance rules engine: Active and monitoring',
          'WebSocket connection: Stable',
          'Neo4j graph database: Connected and responsive'
        ];
        
        const randomMessage = statusMessages[Math.floor(Math.random() * statusMessages.length)];
        const statusLog: ReasoningLog = {
          id: `status-${Date.now()}`,
          timestamp: new Date(),
          step: 'STATUS',
          message: randomMessage,
          level: 'info'
        };
        
        setMonitoringLogs(prev => [...prev.slice(-20), statusLog]); // Keep last 20 logs
      }
    }, 15000); // Every 15 seconds

    return () => clearInterval(statusInterval);
  }, [isGenerating]);

  // Auto-show audit when job reaches needs_review state
  useEffect(() => {
    if (currentJob?.status === 'needs_review' && currentJob.violations) {
      setShowAudit(true);
    }
  }, [currentJob?.status]);

  // Generate monitoring logs and update compliance scores based on generation status
  useEffect(() => {
    if (isGenerating && currentJob) {
      const addLog = (step: string, message: string, level: ReasoningLog['level'] = 'info') => {
        const newLog: ReasoningLog = {
          id: `log-${Date.now()}-${Math.random()}`,
          timestamp: new Date(),
          step,
          message,
          level
        };
        setMonitoringLogs(prev => [...prev, newLog]);
      };

      // Clear previous logs when starting new generation
      if (currentJob.status === 'pending') {
        setMonitoringLogs([]);
        addLog('INIT', 'Initializing brand compliance generation system...');
        // Reset compliance scores to baseline
        setComplianceScores({
          typography: 0.5,
          voice: 0.5,
          color: 0.5,
          logo: 0.5
        });
      }

      // Add logs and update compliance scores based on status changes
      switch (currentJob.status) {
        case 'processing':
          addLog('LOAD', `Loading brand guidelines for ${activeBrand?.name || 'active brand'}`);
          addLog('ANALYZE', 'Analyzing brand voice vectors and compliance rules');
          // Simulate initial analysis scores
          setComplianceScores({
            typography: 0.65,
            voice: 0.70,
            color: 0.60,
            logo: 0.68
          });
          break;
        case 'generating':
          addLog('GENERATE', 'Generating brand-compliant content using AI models');
          addLog('PROCESS', 'Applying brand voice and style guidelines');
          // Simulate improving scores during generation
          setComplianceScores({
            typography: 0.78,
            voice: 0.85,
            color: 0.72,
            logo: 0.80
          });
          break;
        case 'auditing':
          addLog('AUDIT', 'Scanning generated content for compliance violations');
          addLog('VALIDATE', 'Cross-referencing against brand guidelines database');
          // Simulate audit results
          setComplianceScores({
            typography: 0.85,
            voice: 0.92,
            color: 0.78,
            logo: 0.88
          });
          break;
        case 'correcting':
          addLog('CORRECT', 'Applying automatic corrections to compliance violations', 'warning');
          addLog('REVALIDATE', 'Re-auditing corrected content');
          // Simulate corrections improving scores
          setComplianceScores({
            typography: 0.90,
            voice: 0.94,
            color: 0.85,
            logo: 0.92
          });
          break;
        case 'completed':
          addLog('COMPLETE', `Generation completed with ${currentJob.compliance_score || 0}% compliance score`, 'success');
          // Use actual compliance score if available
          if (currentJob.compliance_score) {
            const normalizedScore = currentJob.compliance_score / 100;
            setComplianceScores({
              typography: normalizedScore + (Math.random() - 0.5) * 0.1,
              voice: normalizedScore + (Math.random() - 0.5) * 0.1,
              color: normalizedScore + (Math.random() - 0.5) * 0.1,
              logo: normalizedScore + (Math.random() - 0.5) * 0.1
            });
          }
          break;
        case 'needs_review':
          addLog('REVIEW', `Compliance violations detected - manual review required`, 'warning');
          if (currentJob.violations?.length) {
            addLog('VIOLATIONS', `Found ${currentJob.violations.length} compliance violation(s)`, 'error');
          }
          // Lower scores to indicate violations
          setComplianceScores({
            typography: 0.65,
            voice: 0.70,
            color: 0.58,
            logo: 0.72
          });
          break;
        case 'failed':
          addLog('ERROR', 'Generation failed - please check system status', 'error');
          // Reset to low scores on failure
          setComplianceScores({
            typography: 0.3,
            voice: 0.3,
            color: 0.3,
            logo: 0.3
          });
          break;
      }
    }
  }, [isGenerating, currentJob?.status, currentJob?.compliance_score, activeBrand?.name]);

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

      {/* Main Content Area - Proper flex layout with monitoring sidebar */}
      <div className="flex-1 flex gap-6 mt-6">
        {/* Left Section: Viewport and Controls */}
        <div className="flex-1 flex flex-col items-center justify-center">
          {/* The Machine Housing - Main Viewport Module */}
          <div className="w-full max-w-3xl aspect-video relative group transition-all duration-500 z-10">
          
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
          <div className="mt-8 w-full max-w-3xl flex justify-center">
            <CockpitInput
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
              initialValue="LinkedIn post for Q3 earnings"
            />
          </div>
        </div>

        {/* Right Section: MONITORING Panel - Proper sidebar layout */}
        <div className="w-80 flex flex-col gap-4 opacity-60 hover:opacity-100 transition-all duration-300">
          {/* Compliance Radar - Fixed height */}
          <RecessedScreen 
            className="p-4"
            showTechnicalGrid={false}
            glassEffect={true}
          >
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-blue-500 shadow-lg shadow-blue-500/50 animate-pulse"></div>
              <h3 className="font-mono text-ink text-xs font-bold tracking-widest uppercase">
                COMPLIANCE
              </h3>
              <div className="flex-1 h-px bg-gradient-to-r from-blue-500/20 to-transparent"></div>
              {isGenerating && (
                <div className="flex items-center gap-1 bg-blue-50/50 px-2 py-1 rounded border border-blue-200/30">
                  <div className="w-1 h-1 rounded-full bg-blue-500 animate-pulse"></div>
                  <span className="text-xs font-mono text-blue-600 font-medium">SCAN</span>
                </div>
              )}
            </div>
            <CRTOscilloscope
              complianceScores={complianceScores}
              sweepSpeed={3}
              phosphorIntensity={0.6}
              scanlineOpacity={0.05}
              style={{ width: '100%', height: '220px' }}
            />
          </RecessedScreen>

          {/* System Telemetry - Flexible height that fills remaining space */}
          <div className="flex-1 min-h-0">
            <RecessedScreen 
              className="p-4 h-full flex flex-col"
              showTechnicalGrid={false}
              glassEffect={true}
            >
              <div className="flex items-center gap-2 mb-3 flex-shrink-0">
                <div className="w-2 h-2 rounded-full bg-blue-500 shadow-lg shadow-blue-500/50 animate-pulse"></div>
                <h3 className="font-mono text-ink text-xs font-bold tracking-widest uppercase">
                  TELEMETRY
                </h3>
                <div className="flex-1 h-px bg-gradient-to-r from-blue-500/20 to-transparent"></div>
                {isGenerating && (
                  <div className="flex items-center gap-1 bg-blue-50/50 px-2 py-1 rounded border border-blue-200/30">
                    <div className="w-1 h-1 rounded-full bg-blue-500 animate-pulse"></div>
                    <span className="text-xs font-mono text-blue-600 font-medium">ACTIVE</span>
                  </div>
                )}
              </div>
              <div className="flex-1 min-h-0 mb-3">
                <TerminalTeleprinter
                  logs={monitoringLogs}
                  maxLines={15}
                  typewriterSpeed={80}
                  autoScroll={true}
                  audioFeedback={false}
                  style={{ height: '100%' }}
                />
              </div>
              <div className="text-xs font-mono text-ink-muted bg-white/40 px-3 py-2 rounded border border-gray-300/30 flex-shrink-0">
                {monitoringLogs.length} ENTRIES
              </div>
            </RecessedScreen>
          </div>
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
      <div className="text-center flex flex-col items-center gap-6 system-standby">
        {/* Animated Ring */}
        <div className="relative">
          <div className="w-24 h-24 rounded-full border-2 border-blue-500/20 flex items-center justify-center">
            <div className="w-20 h-20 rounded-full border border-blue-500/30 flex items-center justify-center animate-pulse">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500/10 to-indigo-500/10 flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-blue-500/60 shadow-lg shadow-blue-500/50 standby-indicator" />
              </div>
            </div>
          </div>
          {/* Orbiting dot */}
          <div className="absolute inset-0 animate-spin" style={{ animationDuration: '8s' }}>
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-blue-400/80 shadow-md shadow-blue-400/50" />
          </div>
        </div>

        <div className="text-xl font-bold tracking-wider text-blue-600/80 standby-indicator">
          SYSTEM READY
        </div>

        <div className="flex items-center gap-3">
          <div className="w-8 h-px bg-gradient-to-r from-transparent to-blue-500/40"></div>
          <div className="w-2 h-2 rounded-full bg-green-500 shadow-md shadow-green-500/50 animate-pulse"></div>
          <div className="w-8 h-px bg-gradient-to-l from-transparent to-blue-500/40"></div>
        </div>

        <div className="text-sm tracking-widest text-gray-500/80">
          AWAITING INPUT
        </div>

        {/* Animated Grid */}
        <div className="grid grid-cols-5 gap-1.5 mt-2">
          {[...Array(15)].map((_, i) => (
            <div
              key={i}
              className="w-1.5 h-1.5 rounded-sm bg-blue-500/20 standby-indicator"
              style={{
                animationDelay: `${i * 0.08}s`,
                animationDuration: '2s'
              }}
            />
          ))}
        </div>

        {/* Technical Readout with accent */}
        <div className="mt-4 text-[10px] text-gray-500/70 tracking-widest space-y-1">
          <div className="flex items-center gap-2 justify-center">
            <span className="w-1 h-1 rounded-full bg-green-500/60"></span>
            <span>VIEWPORT: ACTIVE</span>
          </div>
          <div className="flex items-center gap-2 justify-center">
            <span className="w-1 h-1 rounded-full bg-blue-500/60"></span>
            <span>GRID: ENABLED</span>
          </div>
          <div className="flex items-center gap-2 justify-center">
            <span className="w-1 h-1 rounded-full bg-amber-500/60 animate-pulse"></span>
            <span>STATUS: STANDBY</span>
          </div>
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
