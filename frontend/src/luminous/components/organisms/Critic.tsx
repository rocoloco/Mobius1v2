/**
 * Critic - The "Glass Curtain" Analysis Panel
 * 
 * Combines ComplianceGauge and TwinData into a single panel that:
 * - "Sleeps" during drafting/generation (dimmed, placeholder)
 * - "Wakes up" after generation completes (full content)
 * 
 * The panel always occupies its space (no layout shift), but its
 * visual presence changes based on state.
 */

import { memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, Moon, Palette, Type, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { GlassPanel } from '../atoms/GlassPanel';
import { luminousTokens } from '../../tokens';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

interface Violation {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
}

interface DetectedFont {
  family: string;
  weight: string;
  allowed: boolean;
}

interface CriticProps {
  /** Whether the critic is awake (showing full content) */
  isAwake: boolean;
  /** Compliance score (0-100) */
  score: number;
  /** List of violations */
  violations: Violation[];
  /** Detected colors from the generated image */
  detectedColors: string[];
  /** Brand colors for comparison */
  brandColors: string[];
  /** Detected fonts from the generated image */
  detectedFonts: DetectedFont[];
  /** Callback when a violation is clicked */
  onViolationClick?: (violationId: string) => void;
}

export const Critic = memo(function Critic({
  isAwake,
  score,
  violations,
  detectedColors,
  brandColors,
  detectedFonts,
  onViolationClick,
}: CriticProps) {
  const prefersReducedMotion = useReducedMotion();
  
  const transition = {
    duration: prefersReducedMotion ? 0 : 0.5,
    ease: 'easeOut' as const,
  };

  // Score color based on value
  const scoreColor = score >= 90 
    ? luminousTokens.colors.compliance.pass 
    : score >= 70 
      ? luminousTokens.colors.compliance.review 
      : luminousTokens.colors.compliance.critical;

  return (
    <GlassPanel
      className="h-full relative overflow-hidden"
      spotlight={true}
      shimmer={isAwake}
      glow={isAwake}
      data-testid="critic"
    >
      {/* Sleeping/Awake state wrapper */}
      <motion.div
        className="h-full flex flex-col"
        animate={{
          opacity: isAwake ? 1 : 0.4,
          filter: isAwake ? 'grayscale(0%)' : 'grayscale(50%)',
        }}
        transition={transition}
      >
        {/* Awake Content */}
        <AnimatePresence mode="wait">
          {isAwake ? (
            <motion.div
              key="awake"
              className="h-full flex flex-col overflow-hidden"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={transition}
            >
              {/* Score Header */}
              <div 
                className="flex-shrink-0 border-b"
                style={{ 
                  padding: '24px',
                  borderColor: 'rgba(255, 255, 255, 0.08)',
                }}
              >
                <div className="flex items-center justify-between mb-3">
                  <span 
                    className="text-xs font-medium uppercase tracking-wider"
                    style={{ color: luminousTokens.colors.text.muted }}
                  >
                    Governance Score
                  </span>
                  <motion.div
                    animate={{ 
                      scale: [1, 1.1, 1],
                      opacity: [0.5, 1, 0.5],
                    }}
                    transition={{ 
                      duration: 2, 
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  >
                    <Eye size={16} style={{ color: luminousTokens.colors.accent.purple }} />
                  </motion.div>
                </div>
                <motion.div 
                  className="text-5xl font-bold"
                  style={{ 
                    color: scoreColor,
                    textShadow: `0 0 30px ${scoreColor}60`,
                  }}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ 
                    duration: prefersReducedMotion ? 0 : 0.5,
                    ease: 'easeOut',
                    delay: 0.2,
                  }}
                >
                  {Math.round(score)}%
                </motion.div>
              </div>

              {/* Scrollable Content */}
              <div 
                className="flex-1 overflow-y-auto"
                style={{ padding: '20px 24px' }}
              >
                {/* Violations Section */}
                {violations.length > 0 && (
                  <Section title="Violations" count={violations.length}>
                    <div className="space-y-2">
                      {violations.map((violation) => (
                        <ViolationItem
                          key={violation.id}
                          violation={violation}
                          onClick={() => onViolationClick?.(violation.id)}
                        />
                      ))}
                    </div>
                  </Section>
                )}

                {/* Detected Colors */}
                {detectedColors.length > 0 && (
                  <Section title="Detected Colors" icon={<Palette size={14} />}>
                    <div className="flex flex-wrap gap-2">
                      {detectedColors.map((color, idx) => (
                        <ColorSwatch 
                          key={idx} 
                          color={color} 
                          isAllowed={brandColors.includes(color)}
                        />
                      ))}
                    </div>
                  </Section>
                )}

                {/* Detected Fonts */}
                {detectedFonts.length > 0 && (
                  <Section title="Detected Fonts" icon={<Type size={14} />}>
                    <div className="space-y-2">
                      {detectedFonts.map((font, idx) => (
                        <FontItem key={idx} font={font} />
                      ))}
                    </div>
                  </Section>
                )}

                {/* All Clear State */}
                {violations.length === 0 && (
                  <motion.div 
                    className="flex flex-col items-center justify-center py-8"
                    style={{ color: luminousTokens.colors.compliance.pass }}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                  >
                    <motion.div
                      animate={{ 
                        boxShadow: [
                          `0 0 20px ${luminousTokens.colors.compliance.pass}40`,
                          `0 0 40px ${luminousTokens.colors.compliance.pass}60`,
                          `0 0 20px ${luminousTokens.colors.compliance.pass}40`,
                        ],
                      }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                      className="rounded-full p-3 mb-3"
                      style={{ backgroundColor: `${luminousTokens.colors.compliance.pass}20` }}
                    >
                      <CheckCircle size={32} />
                    </motion.div>
                    <span className="text-sm font-medium">All checks passed</span>
                  </motion.div>
                )}
              </div>
            </motion.div>
          ) : (
            /* Sleeping Placeholder */
            <motion.div
              key="sleeping"
              className="h-full flex flex-col items-center justify-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={transition}
            >
              <motion.div
                animate={{ 
                  opacity: [0.3, 0.5, 0.3],
                  scale: [1, 1.05, 1],
                  rotate: [0, 5, 0, -5, 0],
                }}
                transition={{ 
                  duration: 4, 
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              >
                <Moon 
                  size={36} 
                  className="mb-4"
                  style={{ color: luminousTokens.colors.accent.purple }} 
                />
              </motion.div>
              <motion.span 
                className="text-sm tracking-wide font-medium"
                style={{ color: 'rgba(255, 255, 255, 0.4)' }}
                animate={{ opacity: [0.4, 0.6, 0.4] }}
                transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              >
                The Critic Sleeps
              </motion.span>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </GlassPanel>
  );
});

// Section component
function Section({ 
  title, 
  count, 
  icon,
  children 
}: { 
  title: string; 
  count?: number;
  icon?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        {icon && <span style={{ color: luminousTokens.colors.accent.purple }}>{icon}</span>}
        <span 
          className="text-xs font-medium uppercase tracking-wider"
          style={{ color: luminousTokens.colors.text.muted }}
        >
          {title}
        </span>
        {count !== undefined && (
          <span 
            className="text-xs px-2 py-0.5 rounded-full"
            style={{ 
              backgroundColor: 'rgba(239, 68, 68, 0.2)',
              color: luminousTokens.colors.compliance.critical,
            }}
          >
            {count}
          </span>
        )}
      </div>
      {children}
    </div>
  );
}

// Violation item
function ViolationItem({ 
  violation, 
  onClick 
}: { 
  violation: Violation; 
  onClick?: () => void;
}) {
  const severityConfig = {
    critical: {
      icon: AlertCircle,
      color: luminousTokens.colors.compliance.critical,
      bg: 'rgba(239, 68, 68, 0.1)',
      border: 'rgba(239, 68, 68, 0.2)',
    },
    warning: {
      icon: AlertCircle,
      color: luminousTokens.colors.compliance.review,
      bg: 'rgba(245, 158, 11, 0.1)',
      border: 'rgba(245, 158, 11, 0.2)',
    },
    info: {
      icon: Info,
      color: luminousTokens.colors.accent.blue,
      bg: 'rgba(59, 130, 246, 0.1)',
      border: 'rgba(59, 130, 246, 0.2)',
    },
  };

  const config = severityConfig[violation.severity];
  const Icon = config.icon;

  return (
    <button
      onClick={onClick}
      className="w-full text-left p-3 rounded-xl flex items-start gap-3 transition-all duration-200 hover:scale-[1.02]"
      style={{ 
        backgroundColor: config.bg,
        border: `1px solid ${config.border}`,
      }}
    >
      <Icon size={16} className="flex-shrink-0 mt-0.5" style={{ color: config.color }} />
      <span className="text-xs" style={{ color: luminousTokens.colors.text.body }}>
        {violation.message}
      </span>
    </button>
  );
}

// Color swatch
function ColorSwatch({ color, isAllowed }: { color: string; isAllowed: boolean }) {
  return (
    <div className="relative group">
      <div
        className="w-8 h-8 rounded-lg"
        style={{ 
          backgroundColor: color,
          border: isAllowed 
            ? `2px solid ${luminousTokens.colors.compliance.pass}` 
            : '2px solid rgba(255, 255, 255, 0.1)',
        }}
      />
      {!isAllowed && (
        <div 
          className="absolute -top-1 -right-1 w-3 h-3 rounded-full flex items-center justify-center"
          style={{ backgroundColor: luminousTokens.colors.compliance.review }}
        >
          <span className="text-[8px] text-black font-bold">!</span>
        </div>
      )}
    </div>
  );
}

// Font item
function FontItem({ font }: { font: DetectedFont }) {
  return (
    <div 
      className="flex items-center justify-between p-2 rounded-lg"
      style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)' }}
    >
      <span className="text-xs" style={{ color: luminousTokens.colors.text.body }}>
        {font.family} ({font.weight})
      </span>
      {font.allowed ? (
        <CheckCircle size={14} style={{ color: luminousTokens.colors.compliance.pass }} />
      ) : (
        <AlertCircle size={14} style={{ color: luminousTokens.colors.compliance.review }} />
      )}
    </div>
  );
}

Critic.displayName = 'Critic';
