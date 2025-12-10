import React from 'react';

type ButtonVariant = 'default' | 'icon' | 'primary' | 'ghost';

interface PhysicalButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: React.ReactNode;
}

export const PhysicalButton: React.FC<PhysicalButtonProps> = ({
  children,
  onClick,
  variant = 'default',
  className = '',
  disabled = false,
  ...props
}) => {
  const baseStyles = `
    relative flex items-center justify-center
    transition-all duration-150
    font-bold tracking-wide uppercase text-[11px]
    select-none
    disabled:opacity-50 disabled:pointer-events-none
  `;

  const activeState = 'active:scale-[0.98] active:shadow-pressed';

  const variantStyles: Record<ButtonVariant, string> = {
    default: 'bg-surface text-ink shadow-soft hover:text-accent rounded-xl h-10 px-5',
    icon: 'bg-surface text-ink shadow-soft hover:text-accent rounded-xl w-10 h-10',
    primary: 'bg-accent text-white shadow-soft hover:brightness-110 rounded-xl h-10 px-6 active:bg-accent/90',
    ghost: 'bg-transparent text-ink-muted hover:text-ink border border-ink/10 rounded-lg h-8 px-3',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${!disabled ? activeState : ''} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default PhysicalButton;
