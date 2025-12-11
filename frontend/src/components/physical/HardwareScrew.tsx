import React from 'react';
import { TorxHeadBolt } from '../../design-system/components/IndustrialBolts';

interface HardwareScrewProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  type?: 'phillips' | 'hex' | 'torx';
}

export const HardwareScrew: React.FC<HardwareScrewProps> = ({
  className = '',
  size = 'lg',
  type = 'torx'
}) => {
  const sizeMap = {
    sm: 16,
    md: 18,
    lg: 20
  };

  return (
    <div
      className={`
        w-5 h-5
        rounded-full
        flex items-center justify-center
        ${className}
      `}
      style={{
        backgroundColor: '#e0e5ec', // Same as industrialTokens.colors.surface.primary
        boxShadow: `
          inset 2px 2px 4px rgba(163, 177, 198, 0.6),
          inset -2px -2px 4px rgba(255, 255, 255, 0.8),
          0 1px 2px rgba(0, 0, 0, 0.1)
        `
      }}
      aria-hidden="true"
    >
      <TorxHeadBolt size={sizeMap[size]} />
    </div>
  );
};

export default HardwareScrew;
