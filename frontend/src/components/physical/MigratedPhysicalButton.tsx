/**
 * Migrated Physical Button - Uses Polished Industrial Design System
 * 
 * This component replaces the original PhysicalButton with the polished industrial design system
 * while maintaining backward compatibility with the existing API.
 */

import React from 'react';
import { PolishedIndustrialButton } from '../../design-system/components/PolishedIndustrialButton';

type ButtonVariant = 'default' | 'icon' | 'primary' | 'ghost';

interface MigratedPhysicalButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: React.ReactNode;
}

// Map old variants to new polished variants
const variantMapping: Record<ButtonVariant, any> = {
  default: { variant: 'secondary', size: 'md' },
  icon: { variant: 'secondary', size: 'md' },
  primary: { variant: 'primary', size: 'md' },
  ghost: { variant: 'ghost', size: 'sm' }
};

export const MigratedPhysicalButton: React.FC<MigratedPhysicalButtonProps> = ({
  children,
  variant = 'default',
  className = '',
  ...props
}) => {
  const mappedProps = variantMapping[variant];
  
  // For icon variant, ensure square aspect ratio
  const iconStyles = variant === 'icon' ? 'min-w-[2.75rem] aspect-square' : '';
  
  return (
    <PolishedIndustrialButton
      {...mappedProps}
      className={`${iconStyles} ${className}`}
      neumorphic={true}
      industrial={true}
      {...props}
    >
      {children}
    </PolishedIndustrialButton>
  );
};

export default MigratedPhysicalButton;