import React from 'react';

interface RecessedScreenProps {
  children: React.ReactNode;
  className?: string;
}

export const RecessedScreen: React.FC<RecessedScreenProps> = ({
  children,
  className = ''
}) => {
  return (
    <div
      className={`
        bg-[#dbe0e8]
        rounded-2xl
        shadow-recessed
        overflow-hidden
        relative
        border border-white/20
        ${className}
      `}
    >
      {children}

      {/* Scanline Texture Overlay */}
      <div
        className="
          absolute inset-0
          bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.05)_50%)]
          bg-[length:100%_4px]
          pointer-events-none
          opacity-20
        "
        aria-hidden="true"
      />
    </div>
  );
};

export default RecessedScreen;
