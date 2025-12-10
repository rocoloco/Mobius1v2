import React from 'react';

interface HardwareScrewProps {
  className?: string;
  size?: 'sm' | 'md';
}

export const HardwareScrew: React.FC<HardwareScrewProps> = ({
  className = '',
  size = 'md'
}) => {
  const sizeStyles = {
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5',
  };

  return (
    <div
      className={`
        ${sizeStyles[size]}
        rounded-full
        bg-ink/10
        shadow-[inset_1px_1px_2px_rgba(0,0,0,0.2)]
        ${className}
      `}
      aria-hidden="true"
    />
  );
};

export default HardwareScrew;
