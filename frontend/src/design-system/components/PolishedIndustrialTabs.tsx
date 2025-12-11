/**
 * Polished Industrial Tabs Component
 * 
 * Professional tabs built on Radix UI with industrial design tokens
 */

import React from 'react';
import * as TabsPrimitive from '@radix-ui/react-tabs';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx } from 'clsx';
import { industrialTokens, NeumorphicUtils } from '../index';

const tabsListVariants = cva(
  [
    'inline-flex items-center justify-center rounded-xl p-1',
    'text-gray-500 transition-all duration-200'
  ],
  {
    variants: {
      variant: {
        default: 'bg-gray-100/80 border border-gray-200/50',
        industrial: 'border border-gray-300/50',
        pills: 'bg-transparent gap-2'
      },
      size: {
        sm: 'h-9 text-sm',
        md: 'h-11 text-base',
        lg: 'h-13 text-lg'
      }
    },
    defaultVariants: {
      variant: 'industrial',
      size: 'md'
    }
  }
);

const tabsTriggerVariants = cva(
  [
    'inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-1.5',
    'text-sm font-medium ring-offset-white transition-all duration-200',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:pointer-events-none disabled:opacity-50 relative overflow-hidden',
    'select-none touch-manipulation'
  ],
  {
    variants: {
      variant: {
        default: [
          'data-[state=active]:bg-white data-[state=active]:text-gray-900 data-[state=active]:shadow-sm',
          'hover:bg-white/60 hover:text-gray-900 focus-visible:ring-gray-500'
        ],
        industrial: [
          'data-[state=active]:text-blue-600 hover:text-gray-900',
          'focus-visible:ring-blue-500 font-semibold tracking-wide'
        ],
        pills: [
          'data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg',
          'hover:bg-gray-100 hover:text-gray-900 focus-visible:ring-blue-500',
          'border border-gray-200/50'
        ]
      },
      size: {
        sm: 'h-7 px-2 text-xs',
        md: 'h-9 px-3 text-sm',
        lg: 'h-11 px-4 text-base'
      }
    },
    defaultVariants: {
      variant: 'industrial',
      size: 'md'
    }
  }
);

const tabsContentVariants = cva(
  [
    'mt-6 ring-offset-white focus-visible:outline-none focus-visible:ring-2',
    'focus-visible:ring-offset-2 focus-visible:ring-gray-500'
  ]
);

export interface PolishedIndustrialTabsProps
  extends React.ComponentPropsWithoutRef<typeof TabsPrimitive.Root>,
    VariantProps<typeof tabsListVariants> {
  neumorphic?: boolean;
}

export interface TabsListProps
  extends React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>,
    VariantProps<typeof tabsListVariants> {
  neumorphic?: boolean;
}

export interface TabsTriggerProps
  extends React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>,
    VariantProps<typeof tabsTriggerVariants> {
  icon?: React.ReactNode;
  badge?: string | number;
}

const PolishedIndustrialTabs = TabsPrimitive.Root;

const PolishedIndustrialTabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  TabsListProps
>(({ className, variant, size, neumorphic = true, style, ...props }, ref) => {
  // Apply neumorphic styling
  const neumorphicStyle = neumorphic ? {
    backgroundColor: industrialTokens.colors.surface.secondary,
    ...NeumorphicUtils.getShadowStyle('subtle', 'recessed'),
  } : {};

  const combinedStyle: React.CSSProperties = {
    ...neumorphicStyle,
    ...style
  };

  return (
    <TabsPrimitive.List
      ref={ref}
      className={clsx(tabsListVariants({ variant, size }), className)}
      style={combinedStyle}
      {...props}
    />
  );
});
PolishedIndustrialTabsList.displayName = TabsPrimitive.List.displayName;

const PolishedIndustrialTabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  TabsTriggerProps
>(({ className, variant, size, icon, badge, children, style, ...props }, ref) => {
  // Use a ref to access the DOM element and check data-state
  const [isActive, setIsActive] = React.useState(false);
  const triggerRef = React.useRef<HTMLButtonElement>(null);

  React.useEffect(() => {
    const element = triggerRef.current;
    if (!element) return;

    const checkActiveState = () => {
      const dataState = element.getAttribute('data-state');
      setIsActive(dataState === 'active');
    };

    // Check initial state
    checkActiveState();

    // Create a MutationObserver to watch for data-state changes
    const observer = new MutationObserver(checkActiveState);
    observer.observe(element, {
      attributes: true,
      attributeFilter: ['data-state']
    });

    return () => observer.disconnect();
  }, []);

  // Apply neumorphic styling for active state
  const neumorphicStyle = isActive ? {
    backgroundColor: industrialTokens.colors.surface.primary,
    ...NeumorphicUtils.getShadowStyle('normal', 'raised'),
  } : {};

  const combinedStyle: React.CSSProperties = {
    ...neumorphicStyle,
    ...style
  };

  // Combine refs
  const combinedRef = React.useCallback((node: HTMLButtonElement) => {
    triggerRef.current = node;
    if (typeof ref === 'function') {
      ref(node);
    } else if (ref) {
      ref.current = node;
    }
  }, [ref]);

  return (
    <TabsPrimitive.Trigger
      ref={combinedRef}
      className={clsx(tabsTriggerVariants({ variant, size }), className)}
      style={combinedStyle}
      {...props}
    >
      <div className="flex items-center gap-2">
        {icon && <span className="flex-shrink-0">{icon}</span>}
        <span>{children}</span>
        {badge && (
          <span className="ml-1 px-1.5 py-0.5 text-xs bg-gray-200 text-gray-700 rounded-full min-w-[1.25rem] text-center">
            {badge}
          </span>
        )}
      </div>
    </TabsPrimitive.Trigger>
  );
});
PolishedIndustrialTabsTrigger.displayName = TabsPrimitive.Trigger.displayName;

const PolishedIndustrialTabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={clsx(tabsContentVariants(), className)}
    {...props}
  />
));
PolishedIndustrialTabsContent.displayName = TabsPrimitive.Content.displayName;

export {
  PolishedIndustrialTabs,
  PolishedIndustrialTabsList,
  PolishedIndustrialTabsTrigger,
  PolishedIndustrialTabsContent,
  tabsListVariants,
  tabsTriggerVariants
};