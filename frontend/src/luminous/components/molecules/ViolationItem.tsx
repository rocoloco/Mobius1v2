import { AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { luminousTokens } from '../../tokens';

interface Violation {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
}

interface ViolationItemProps {
  violation: Violation;
  onClick: () => void;
  focused?: boolean;
  keyboardIndex?: number;
}

/**
 * ViolationItem - Clickable violation list item component
 * 
 * Displays a single violation with severity icon and message.
 * Used in the ComplianceGauge violation list. Clicking triggers
 * focus effect on corresponding Canvas bounding box.
 * 
 * @param violation - Violation object with id, severity, and message
 * @param onClick - Callback triggered when violation is clicked
 */
export function ViolationItem({ 
  violation, 
  onClick, 
  focused = false, 
  keyboardIndex 
}: ViolationItemProps) {
  const { severity, message } = violation;
  
  // Map severity to icon and color
  const getSeverityIcon = () => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-4 h-4" style={{ color: luminousTokens.colors.compliance.critical }} />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4" style={{ color: luminousTokens.colors.compliance.review }} />;
      case 'info':
        return <Info className="w-4 h-4" style={{ color: luminousTokens.colors.text.muted }} />;
    }
  };
  
  return (
    <button
      onClick={onClick}
      data-testid="violation-item"
      data-severity={severity}
      data-keyboard-index={keyboardIndex}
      className={`w-full flex items-start gap-3 px-3 py-3 rounded-lg transition-all duration-300 hover:bg-white/5 hover:scale-[1.02] text-left focus:outline-none ${
        focused ? 'bg-white/10 scale-[1.02]' : ''
      }`}
      style={{
        cursor: 'pointer',
        boxShadow: focused ? `0 0 0 2px ${luminousTokens.colors.accent.blue}` : 'none',
        minHeight: '44px',
      }}
      aria-label={`${severity} violation: ${message}`}
      role="option"
      aria-selected={focused}
    >
      <div className="flex-shrink-0 mt-0.5">
        {getSeverityIcon()}
      </div>
      <p
        className="text-sm leading-relaxed flex-1"
        style={{ color: luminousTokens.colors.text.body }}
      >
        {message}
      </p>
    </button>
  );
}
