/**
 * Responsive Grid Component
 * 
 * Addresses mobile responsiveness issues with adaptive layouts
 */

import React from 'react';
import { industrialTokens, NeumorphicUtils } from '../index';

interface ResponsiveGridProps {
  children: React.ReactNode;
  columns?: {
    mobile: number;
    tablet: number;
    desktop: number;
  };
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  columns = { mobile: 1, tablet: 2, desktop: 3 },
  gap = 'md',
  className = ''
}) => {
  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8'
  };

  const gridClasses = `
    grid 
    grid-cols-${columns.mobile} 
    sm:grid-cols-${columns.tablet} 
    lg:grid-cols-${columns.desktop} 
    ${gapClasses[gap]}
    ${className}
  `;

  return (
    <div className={gridClasses}>
      {children}
    </div>
  );
};

interface MobileOptimizedCardProps {
  title: string;
  children: React.ReactNode;
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export const MobileOptimizedCard: React.FC<MobileOptimizedCardProps> = ({
  title,
  children,
  collapsible = false,
  defaultExpanded = true
}) => {
  const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);

  return (
    <div 
      className="rounded-xl overflow-hidden"
      style={{
        backgroundColor: industrialTokens.colors.surface.secondary,
        ...NeumorphicUtils.getShadowStyle('normal', 'raised')
      }}
    >
      <div 
        className={`p-4 ${collapsible ? 'cursor-pointer' : ''}`}
        onClick={collapsible ? () => setIsExpanded(!isExpanded) : undefined}
        role={collapsible ? 'button' : undefined}
        aria-expanded={collapsible ? isExpanded : undefined}
        tabIndex={collapsible ? 0 : undefined}
        onKeyDown={collapsible ? (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setIsExpanded(!isExpanded);
          }
        } : undefined}
      >
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
            {title}
          </h3>
          {collapsible && (
            <span 
              className={`transform transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
              aria-hidden="true"
            >
              ▼
            </span>
          )}
        </div>
      </div>
      
      {(!collapsible || isExpanded) && (
        <div className="px-4 pb-4">
          {children}
        </div>
      )}
    </div>
  );
};

interface TouchFriendlyButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  disabled?: boolean;
}

export const TouchFriendlyButton: React.FC<TouchFriendlyButtonProps> = ({
  children,
  onClick,
  type = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false
}) => {
  const typeStyles = {
    primary: {
      backgroundColor: '#3b82f6',
      color: '#ffffff'
    },
    secondary: {
      backgroundColor: industrialTokens.colors.surface.secondary,
      color: industrialTokens.colors.text.primary
    },
    danger: {
      backgroundColor: '#ef4444',
      color: '#ffffff'
    }
  };

  const sizeStyles = {
    sm: 'px-4 py-3 text-sm min-h-[44px]', // 44px minimum touch target
    md: 'px-6 py-4 text-base min-h-[48px]', // 48px recommended touch target
    lg: 'px-8 py-5 text-lg min-h-[52px]'   // 52px large touch target
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${sizeStyles[size]}
        ${fullWidth ? 'w-full' : ''}
        rounded-xl font-medium transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
        active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed
        touch-manipulation
      `}
      style={{
        ...typeStyles[type],
        ...NeumorphicUtils.getShadowStyle('normal', 'raised')
      }}
    >
      {children}
    </button>
  );
};

interface SwipeableTabsProps {
  tabs: Array<{ id: string; label: string; icon: string }>;
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export const SwipeableTabs: React.FC<SwipeableTabsProps> = ({
  tabs,
  activeTab,
  onTabChange
}) => {
  const [touchStart, setTouchStart] = React.useState<number | null>(null);
  const [touchEnd, setTouchEnd] = React.useState<number | null>(null);

  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    const currentIndex = tabs.findIndex(tab => tab.id === activeTab);
    
    if (isLeftSwipe && currentIndex < tabs.length - 1) {
      onTabChange(tabs[currentIndex + 1].id);
    }
    
    if (isRightSwipe && currentIndex > 0) {
      onTabChange(tabs[currentIndex - 1].id);
    }
  };

  return (
    <div 
      className="overflow-x-auto scrollbar-hide"
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      <div className="flex gap-2 p-2 min-w-max">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              flex items-center gap-2 px-4 py-3 rounded-lg font-medium 
              transition-all duration-200 whitespace-nowrap min-h-[48px]
              focus:outline-none focus:ring-2 focus:ring-blue-500
              ${activeTab === tab.id ? 'text-blue-600' : 'text-gray-600'}
            `}
            style={{
              backgroundColor: activeTab === tab.id 
                ? industrialTokens.colors.surface.primary 
                : 'transparent',
              ...(activeTab === tab.id 
                ? NeumorphicUtils.getShadowStyle('normal', 'raised')
                : {}
              )
            }}
          >
            <span className="text-lg">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};