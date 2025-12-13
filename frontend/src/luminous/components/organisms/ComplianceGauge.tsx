import { memo, useMemo, useEffect, useState, useCallback } from 'react';
import { Pie } from '@visx/shape';
import { Group } from '@visx/group';
import { LinearGradient } from '@visx/gradient';
import { ViolationItem } from '../molecules/ViolationItem';
import { GlassPanel } from '../atoms/GlassPanel';
import { Confetti } from '../atoms/Confetti';
import { luminousTokens, getComplianceColor } from '../../tokens';
import { useKeyboardNavigation } from '../../../hooks/useKeyboardNavigation';

interface Violation {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
}

interface ComplianceGaugeProps {
  score: number;
  violations: Violation[];
  onViolationClick: (violationId: string) => void;
  auditUnavailable?: boolean; // When audit service is unavailable
}

/**
 * ComplianceGauge - Radial donut chart with violation list
 * 
 * Wrapped with React.memo for performance optimization - re-renders only when props change.
 * 
 * Displays overall brand compliance score as a visual donut chart
 * with color-coded thresholds:
 * - ≥95%: Green (Pass)
 * - 70-95%: Amber (Review)
 * - <70%: Red (Critical)
 * 
 * Below the gauge, violations are grouped by severity and displayed
 * in a scrollable list. Clicking a violation triggers focus on the
 * corresponding Canvas bounding box.
 * 
 * @param score - Compliance score (0-100)
 * @param violations - Array of violation objects
 * @param onViolationClick - Callback when violation is clicked
 */
export const ComplianceGauge = memo(function ComplianceGauge({
  score,
  violations,
  onViolationClick,
  auditUnavailable = false,
}: ComplianceGaugeProps) {
  // Clamp score to 0-100 range
  const clampedScore = Math.max(0, Math.min(100, score));
  
  // Confetti state
  const [showConfetti, setShowConfetti] = useState(false);
  const [previousScore, setPreviousScore] = useState(clampedScore);
  
  // Trigger confetti when score reaches ≥95% from a lower score
  useEffect(() => {
    if (!auditUnavailable && clampedScore >= 95 && previousScore < 95) {
      setShowConfetti(true);
    }
    setPreviousScore(clampedScore);
  }, [clampedScore, previousScore, auditUnavailable]);
  
  // Get color based on score threshold or grey if audit unavailable
  const gaugeColor = auditUnavailable 
    ? luminousTokens.colors.text.muted 
    : getComplianceColor(clampedScore);
  
  // Group violations by severity
  const groupedViolations = useMemo(() => {
    const groups = {
      critical: [] as Violation[],
      warning: [] as Violation[],
      info: [] as Violation[],
    };
    
    violations.forEach((violation) => {
      groups[violation.severity].push(violation);
    });
    
    return groups;
  }, [violations]);
  
  // Flatten grouped violations in order: Critical, Warning, Info
  const orderedViolations = useMemo(() => {
    return [
      ...groupedViolations.critical,
      ...groupedViolations.warning,
      ...groupedViolations.info,
    ];
  }, [groupedViolations]);

  // Memoize keyboard navigation select handler
  const handleKeyboardSelect = useCallback((index: number) => {
    const violation = orderedViolations[index];
    if (violation) {
      onViolationClick(violation.id);
    }
  }, [orderedViolations, onViolationClick]);

  // Keyboard navigation for violation list
  const { containerRef, focusedIndex } = useKeyboardNavigation({
    itemCount: orderedViolations.length,
    onSelect: handleKeyboardSelect,
  });

  // Memoize violation click handler factory
  const createViolationClickHandler = useCallback((violationId: string) => () => {
    onViolationClick(violationId);
  }, [onViolationClick]);
  
  // Chart dimensions - memoized as constants
  const chartDimensions = useMemo(() => {
    const width = 120;
    const height = 120;
    const margin = 4; // Add margin to prevent clipping
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = (Math.min(width, height) / 2) - margin;
    const innerRadius = radius * 0.65; // Donut hole
    return { width, height, centerX, centerY, radius, innerRadius };
  }, []);

  const { width, height, centerX, centerY, radius, innerRadius } = chartDimensions;
  
  // Memoize chart data to prevent recreation on each render
  const chartData = useMemo(() => [
    { label: 'score', value: clampedScore },
    { label: 'remaining', value: 100 - clampedScore },
  ], [clampedScore]);
  
  return (
    <>
      <GlassPanel className="h-full" spotlight={true} shimmer={false} data-testid="compliance-gauge">
        <div className="h-full flex flex-col overflow-hidden" style={{ minHeight: 0 }}>
      {/* Gauge Chart */}
      <div className="flex-shrink-0 flex items-center justify-center pt-4 pb-2 px-4">
        <div className="relative">
          <svg width={width} height={height} style={{ overflow: 'visible' }}>
            <LinearGradient id="gauge-gradient" from={gaugeColor} to={gaugeColor} />
            
            <Group top={centerY} left={centerX}>
              <Pie
                data={chartData}
                pieValue={(d) => d.value}
                outerRadius={radius}
                innerRadius={innerRadius}
                cornerRadius={3}
                padAngle={0.02}
              >
                {(pie) => {
                  return pie.arcs.map((arc, index) => {
                    const isScore = arc.data.label === 'score';
                    return (
                      <g key={`arc-${index}`}>
                        <path
                          d={pie.path(arc) || ''}
                          fill={isScore ? gaugeColor : 'rgba(255, 255, 255, 0.05)'}
                          stroke={isScore ? gaugeColor : 'rgba(255, 255, 255, 0.08)'}
                          strokeWidth={1}
                        />
                      </g>
                    );
                  });
                }}
              </Pie>
            </Group>
          </svg>
          
          {/* Score Value in Center */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              {auditUnavailable ? (
                <>
                  <div
                    className="text-lg font-bold tracking-tight"
                    style={{ color: gaugeColor }}
                  >
                    N/A
                  </div>
                  <div
                    className="text-[9px] font-medium mt-0.5"
                    style={{ color: luminousTokens.colors.text.muted }}
                  >
                    UNAVAILABLE
                  </div>
                </>
              ) : (
                <>
                  <div
                    className="text-2xl font-bold tracking-tight"
                    style={{ color: gaugeColor }}
                  >
                    {Math.round(clampedScore)}
                  </div>
                  <div
                    className="text-[9px] font-medium mt-0.5"
                    style={{ color: luminousTokens.colors.text.muted }}
                  >
                    SCORE
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Violation List */}
      <div className="flex-1 overflow-hidden flex flex-col border-t border-white/10" style={{ minHeight: 0 }}>
        <div className="flex-shrink-0" style={{ padding: '8px 16px 8px 24px' }}>
          <h3
            className="text-xs font-semibold tracking-wide uppercase"
            style={{ color: luminousTokens.colors.text.high }}
          >
            Violations
          </h3>
          {violations.length > 0 && (
            <p
              className="text-[10px] mt-0.5"
              style={{ color: luminousTokens.colors.text.muted }}
            >
              {groupedViolations.critical.length} Critical, {groupedViolations.warning.length} Warning, {groupedViolations.info.length} Info
            </p>
          )}
        </div>
        
        <div 
          ref={containerRef}
          className="flex-1 overflow-y-auto scrollbar-hide px-4 pb-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          style={{ minHeight: 0 }}
          tabIndex={0}
          role={violations.length > 0 ? "listbox" : "region"}
          aria-label={violations.length > 0 ? "Compliance violations" : "Violation status"}
        >
          {auditUnavailable ? (
            <div className="flex items-center justify-center h-full" role="status" aria-live="polite">
              <p
                className="text-center text-sm"
                style={{ color: luminousTokens.colors.text.muted }}
              >
                Audit Unavailable
              </p>
            </div>
          ) : violations.length === 0 ? (
            <div className="flex items-center justify-center h-full" role="status" aria-live="polite">
              <p
                className="text-center text-sm"
                style={{ color: luminousTokens.colors.text.muted }}
              >
                No violations detected
              </p>
            </div>
          ) : (
            <div className="space-y-1" role="presentation">
              {orderedViolations.map((violation, index) => (
                <ViolationItem
                  key={violation.id}
                  violation={violation}
                  onClick={createViolationClickHandler(violation.id)}
                  focused={index === focusedIndex}
                  keyboardIndex={index}
                />
              ))}
            </div>
          )}
        </div>
      </div>
      </div>
    </GlassPanel>
    
    {/* Confetti celebration for high scores */}
    <Confetti 
      trigger={showConfetti} 
      onComplete={() => setShowConfetti(false)} 
    />
    </>
  );
});

// Display name for debugging
ComplianceGauge.displayName = 'ComplianceGauge';
