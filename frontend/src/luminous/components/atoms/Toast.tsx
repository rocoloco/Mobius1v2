import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, X } from 'lucide-react';
import { luminousTokens } from '../../tokens';

export type ToastType = 'success' | 'warning' | 'error';

interface ToastProps {
  type: ToastType;
  message: string;
  duration?: number;
  onClose: () => void;
}

/**
 * Toast - Notification component for temporary messages
 * 
 * Displays temporary notification messages with appropriate styling
 * based on type (success, warning, error). Auto-dismisses after
 * specified duration.
 * 
 * @param type - Toast type determining color and icon
 * @param message - Message text to display
 * @param duration - Auto-dismiss duration in ms (default: 5000)
 * @param onClose - Callback when toast is closed
 */
export function Toast({ type, message, duration = 5000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300); // Wait for fade out animation
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const getToastStyles = () => {
    switch (type) {
      case 'success':
        return {
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: luminousTokens.colors.compliance.pass,
        };
      case 'warning':
        return {
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          color: luminousTokens.colors.compliance.review,
        };
      case 'error':
        return {
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          color: luminousTokens.colors.compliance.critical,
        };
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'warning':
      case 'error':
        return <AlertTriangle className="w-5 h-5" />;
    }
  };

  const styles = getToastStyles();

  return (
    <div
      className={`fixed top-20 right-4 z-50 max-w-sm p-4 rounded-xl transition-all duration-300 ${
        isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'
      }`}
      style={{
        ...styles,
        backdropFilter: luminousTokens.effects.backdropBlur,
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
      }}
      data-testid="toast"
      data-type={type}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0" style={{ color: styles.color }}>
          {getIcon()}
        </div>
        <div className="flex-1">
          <p
            className="text-sm font-medium"
            style={{ color: luminousTokens.colors.text.high }}
          >
            {message}
          </p>
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            setTimeout(onClose, 300);
          }}
          className="flex-shrink-0 p-1 rounded-lg hover:bg-white/10 transition-colors duration-200"
          aria-label="Close notification"
        >
          <X className="w-4 h-4" style={{ color: luminousTokens.colors.text.muted }} />
        </button>
      </div>
    </div>
  );
}