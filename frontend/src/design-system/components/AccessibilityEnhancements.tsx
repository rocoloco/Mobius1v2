/**
 * Accessibility Enhancement Components
 * 
 * Components to improve accessibility and address WCAG compliance issues
 */

import React, { useState, useEffect } from 'react';
import { industrialTokens, NeumorphicUtils } from '../index';

// High Contrast Mode Toggle
export const HighContrastToggle: React.FC = () => {
  const [highContrast, setHighContrast] = useState(false);

  useEffect(() => {
    if (highContrast) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }
  }, [highContrast]);

  return (
    <button
      onClick={() => setHighContrast(!highContrast)}
      className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
      style={{
        backgroundColor: highContrast 
          ? industrialTokens.colors.surface.primary 
          : industrialTokens.colors.surface.secondary,
        color: highContrast ? '#000' : industrialTokens.colors.text.primary,
        ...NeumorphicUtils.getShadowStyle('normal', 'raised')
      }}
      aria-pressed={highContrast}
      title="Toggle high contrast mode for better visibility"
    >
      <span role="img" aria-label="Contrast">🔆</span>
      <span>High Contrast</span>
    </button>
  );
};

// Screen Reader Skip Links
export const SkipLinks: React.FC = () => {
  return (
    <div className="sr-only focus-within:not-sr-only">
      <a
        href="#main-content"
        className="absolute top-4 left-4 px-4 py-2 bg-blue-600 text-white rounded-lg z-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        Skip to main content
      </a>
      <a
        href="#navigation"
        className="absolute top-4 left-32 px-4 py-2 bg-blue-600 text-white rounded-lg z-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        Skip to navigation
      </a>
    </div>
  );
};

// Accessible Status Indicator with Text Alternative
interface AccessibleStatusIndicatorProps {
  status: 'on' | 'off' | 'error' | 'warning' | 'success';
  label: string;
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

export const AccessibleStatusIndicator: React.FC<AccessibleStatusIndicatorProps> = ({
  status,
  label,
  size = 'md',
  showText = true
}) => {
  const statusConfig = {
    on: { color: '#22c55e', text: 'Active', bgColor: '#dcfce7' },
    off: { color: '#6b7280', text: 'Inactive', bgColor: '#f3f4f6' },
    error: { color: '#ef4444', text: 'Error', bgColor: '#fef2f2' },
    warning: { color: '#f59e0b', text: 'Warning', bgColor: '#fefbeb' },
    success: { color: '#10b981', text: 'Success', bgColor: '#ecfdf5' }
  };

  const sizeConfig = {
    sm: { indicator: 12, text: 'text-xs', padding: 'px-2 py-1' },
    md: { indicator: 16, text: 'text-sm', padding: 'px-3 py-1' },
    lg: { indicator: 20, text: 'text-base', padding: 'px-4 py-2' }
  };

  const config = statusConfig[status];
  const sizing = sizeConfig[size];

  return (
    <div 
      className={`inline-flex items-center gap-2 rounded-full ${sizing.padding}`}
      style={{ backgroundColor: config.bgColor }}
      role="status"
      aria-label={`${label}: ${config.text}`}
    >
      <div
        className="rounded-full"
        style={{
          width: sizing.indicator,
          height: sizing.indicator,
          backgroundColor: config.color,
          ...NeumorphicUtils.getShadowStyle('subtle', 'raised')
        }}
        aria-hidden="true"
      />
      {showText && (
        <span className={`font-medium ${sizing.text}`} style={{ color: config.color }}>
          {label}: {config.text}
        </span>
      )}
      {/* Hidden text for screen readers */}
      <span className="sr-only">
        Status indicator for {label} is currently {config.text.toLowerCase()}
      </span>
    </div>
  );
};

// Keyboard Navigation Helper
export const KeyboardNavigationInfo: React.FC = () => {
  const [showHelp, setShowHelp] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setShowHelp(!showHelp)}
        onKeyDown={(e) => {
          if (e.key === 'Escape') setShowHelp(false);
        }}
        className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        style={{
          backgroundColor: industrialTokens.colors.surface.secondary,
          color: industrialTokens.colors.text.secondary,
          ...NeumorphicUtils.getShadowStyle('subtle', 'raised')
        }}
        aria-expanded={showHelp}
        aria-haspopup="true"
        title="Show keyboard navigation help"
      >
        <span role="img" aria-label="Keyboard">⌨️</span>
        <span>Keyboard Help</span>
      </button>

      {showHelp && (
        <div
          className="absolute top-full left-0 mt-2 p-4 rounded-lg shadow-lg z-50 w-80"
          style={{
            backgroundColor: industrialTokens.colors.surface.primary,
            ...NeumorphicUtils.getShadowStyle('deep', 'raised')
          }}
          role="dialog"
          aria-labelledby="keyboard-help-title"
        >
          <h3 id="keyboard-help-title" className="text-lg font-semibold mb-3">
            Keyboard Navigation
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <kbd className="px-2 py-1 bg-gray-200 rounded text-xs">Tab</kbd>
              <span>Navigate forward</span>
            </div>
            <div className="flex justify-between">
              <kbd className="px-2 py-1 bg-gray-200 rounded text-xs">Shift + Tab</kbd>
              <span>Navigate backward</span>
            </div>
            <div className="flex justify-between">
              <kbd className="px-2 py-1 bg-gray-200 rounded text-xs">Enter</kbd>
              <span>Activate button/link</span>
            </div>
            <div className="flex justify-between">
              <kbd className="px-2 py-1 bg-gray-200 rounded text-xs">Space</kbd>
              <span>Activate button</span>
            </div>
            <div className="flex justify-between">
              <kbd className="px-2 py-1 bg-gray-200 rounded text-xs">Escape</kbd>
              <span>Close dialog/menu</span>
            </div>
          </div>
          <button
            onClick={() => setShowHelp(false)}
            className="mt-3 px-3 py-1 bg-blue-600 text-white rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
};

// Focus Trap for Modal/Dialog Components
export const FocusTrap: React.FC<{ children: React.ReactNode; active: boolean }> = ({
  children,
  active
}) => {
  const trapRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!active || !trapRef.current) return;

    const focusableElements = trapRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus();
          e.preventDefault();
        }
      }
    };

    document.addEventListener('keydown', handleTabKey);
    firstElement?.focus();

    return () => {
      document.removeEventListener('keydown', handleTabKey);
    };
  }, [active]);

  return (
    <div ref={trapRef} className={active ? '' : 'pointer-events-none'}>
      {children}
    </div>
  );
};