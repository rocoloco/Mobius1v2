/**
 * Migrated Recessed Screen - Uses Polished Industrial Design System
 * 
 * This component replaces the original RecessedScreen with the polished industrial design system
 * while maintaining backward compatibility with the existing API.
 */

import React from 'react';
import { PolishedIndustrialCard } from '../../design-system/components/PolishedIndustrialCard';

interface MigratedRecessedScreenProps {
  children: React.ReactNode;
  className?: string;
  showTechnicalGrid?: boolean;
  gridColor?: string;
  glassEffect?: boolean;
}

export const MigratedRecessedScreen: React.FC<MigratedRecessedScreenProps> = ({
  children,
  className = '',
  showTechnicalGrid = true,
  gridColor = '#3b82f6',
  glassEffect = true
}) => {
  return (
    <div
      className={`relative ${className}`}
      data-testid="recessed-screen"
      style={{
        borderRadius: '1rem', // Match original rounded-2xl
        backgroundColor: '#dbe0e8', // Match original background
        boxShadow: 'inset 4px 4px 8px rgba(163, 177, 198, 0.6), inset -4px -4px 8px rgba(255, 255, 255, 0.8)', // Recessed effect
        padding: '2rem' // Increased padding to show corner hardware screws
      }}
    >
      {/* Viewfinder Reticle Markings */}
      {showTechnicalGrid && (
        <>
          {/* Corner Reticles - positioned relative to viewport edges */}
          <div className="absolute top-8 left-8 pointer-events-none z-25" aria-hidden="true">
            <div className="w-6 h-0.5" style={{ backgroundColor: gridColor, opacity: 0.8 }}></div>
            <div className="w-0.5 h-6" style={{ backgroundColor: gridColor, opacity: 0.8 }}></div>
          </div>
          
          <div className="absolute top-8 right-8 pointer-events-none z-25 flex flex-col items-end" aria-hidden="true">
            <div className="w-6 h-0.5" style={{ backgroundColor: gridColor, opacity: 0.8 }}></div>
            <div className="w-0.5 h-6 self-end" style={{ backgroundColor: gridColor, opacity: 0.8 }}></div>
          </div>
          
          <div className="absolute bottom-8 left-8 pointer-events-none z-25" aria-hidden="true">
            <div className="w-0.5 h-6" style={{ backgroundColor: gridColor, opacity: 0.8 }}></div>
            <div className="w-6 h-0.5" style={{ backgroundColor: gridColor, opacity: 0.8 }}></div>
          </div>
          
          <div className="absolute bottom-8 right-8 pointer-events-none z-25 flex flex-col items-end" aria-hidden="true">
            <div className="w-0.5 h-6 self-end" style={{ backgroundColor: gridColor, opacity: 0.8 }}></div>
            <div className="w-6 h-0.5" style={{ backgroundColor: gridColor, opacity: 0.8 }}></div>
          </div>
          
          {/* Center Crosshair */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none z-25" aria-hidden="true">
            <div className="relative w-8 h-8">
              <div className="absolute top-1/2 left-0 w-2.5 h-0.5 -translate-y-1/2" style={{ backgroundColor: gridColor, opacity: 0.7 }}></div>
              <div className="absolute top-1/2 right-0 w-2.5 h-0.5 -translate-y-1/2" style={{ backgroundColor: gridColor, opacity: 0.7 }}></div>
              <div className="absolute left-1/2 top-0 h-2.5 w-0.5 -translate-x-1/2" style={{ backgroundColor: gridColor, opacity: 0.7 }}></div>
              <div className="absolute left-1/2 bottom-0 h-2.5 w-0.5 -translate-x-1/2" style={{ backgroundColor: gridColor, opacity: 0.7 }}></div>
              <div className="absolute top-1/2 left-1/2 w-1.5 h-1.5 rounded-full -translate-x-1/2 -translate-y-1/2" style={{ border: `1.5px solid ${gridColor}`, backgroundColor: 'transparent', opacity: 0.6 }}></div>
            </div>
          </div>

          {/* Edge Midpoint Markers */}
          <div className="absolute top-8 left-1/2 -translate-x-1/2 pointer-events-none z-25" aria-hidden="true">
            <div className="w-0.5 h-4" style={{ backgroundColor: gridColor, opacity: 0.6 }}></div>
          </div>
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 pointer-events-none z-25" aria-hidden="true">
            <div className="w-0.5 h-4" style={{ backgroundColor: gridColor, opacity: 0.6 }}></div>
          </div>
          <div className="absolute left-8 top-1/2 -translate-y-1/2 pointer-events-none z-25" aria-hidden="true">
            <div className="w-4 h-0.5" style={{ backgroundColor: gridColor, opacity: 0.6 }}></div>
          </div>
          <div className="absolute right-8 top-1/2 -translate-y-1/2 pointer-events-none z-25" aria-hidden="true">
            <div className="w-4 h-0.5" style={{ backgroundColor: gridColor, opacity: 0.6 }}></div>
          </div>
        </>
      )}

      {/* Glass Cover Simulation - Enhanced */}
      {glassEffect && (
        <>
          <div className="absolute inset-0 pointer-events-none glass-viewport z-15" aria-hidden="true" />
          <div className="absolute inset-0 pointer-events-none glass-reflection z-15" aria-hidden="true" />
        </>
      )}

      {/* Content Layer */}
      <div className="relative z-10 h-full">
        {children}
      </div>

      {/* Scanline Texture Overlay - preserved from original */}
      <div
        className="
          absolute inset-0
          bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.05)_50%)]
          bg-[length:100%_4px]
          pointer-events-none
          opacity-20
          z-20
        "
        aria-hidden="true"
      />
    </div>
  );
};

export default MigratedRecessedScreen;