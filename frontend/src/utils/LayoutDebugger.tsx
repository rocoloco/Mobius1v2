/**
 * Layout Debugger - Visual alignment and spacing analysis tool
 * 
 * Press 'D' to toggle debug mode and see alignment guides
 */

import React, { useState, useEffect } from 'react';

export const LayoutDebugger: React.FC = () => {
  const [debugMode, setDebugMode] = useState(false);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'd' || e.key === 'D') {
        setDebugMode(!debugMode);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [debugMode]);

  if (!debugMode) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-[9999]">
      {/* Center vertical line */}
      <div className="absolute left-1/2 top-0 w-0.5 h-full bg-red-500/50 -translate-x-0.5" />
      
      {/* Horizontal thirds */}
      <div className="absolute left-0 top-1/3 w-full h-0.5 bg-blue-500/30" />
      <div className="absolute left-0 top-2/3 w-full h-0.5 bg-blue-500/30" />
      
      {/* Vertical thirds */}
      <div className="absolute left-1/3 top-0 w-0.5 h-full bg-blue-500/30" />
      <div className="absolute left-2/3 top-0 w-0.5 h-full bg-blue-500/30" />
      
      {/* 8px grid */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0,255,0,0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,255,0,0.3) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px'
        }}
      />
      
      {/* Debug info panel */}
      <div className="absolute top-4 left-4 bg-black/80 text-white p-4 rounded text-xs font-mono pointer-events-auto">
        <div className="mb-2 font-bold">Layout Debugger (Press 'D' to toggle)</div>
        <div>Red line: Center vertical</div>
        <div>Blue lines: Rule of thirds</div>
        <div>Green grid: 32px spacing</div>
        <div className="mt-2">
          <div>Screen: {window.innerWidth}x{window.innerHeight}</div>
          <div>Viewport center: {window.innerWidth / 2}px</div>
        </div>
      </div>
    </div>
  );
};

export default LayoutDebugger;