/**
 * Measurement Tool - Click elements to see their exact dimensions and positions
 * 
 * Press 'M' to toggle measurement mode
 */

import React, { useState, useEffect } from 'react';

interface Measurement {
  element: string;
  x: number;
  y: number;
  width: number;
  height: number;
  centerX: number;
  centerY: number;
}

export const MeasurementTool: React.FC = () => {
  const [measureMode, setMeasureMode] = useState(false);
  const [measurements, setMeasurements] = useState<Measurement[]>([]);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'm' || e.key === 'M') {
        setMeasureMode(!measureMode);
        if (!measureMode) {
          setMeasurements([]);
        }
      }
    };

    const handleClick = (e: MouseEvent) => {
      if (!measureMode) return;
      
      e.preventDefault();
      e.stopPropagation();
      
      const target = e.target as HTMLElement;
      const rect = target.getBoundingClientRect();
      
      const measurement: Measurement = {
        element: target.className || target.tagName,
        x: rect.x,
        y: rect.y,
        width: rect.width,
        height: rect.height,
        centerX: rect.x + rect.width / 2,
        centerY: rect.y + rect.height / 2
      };
      
      setMeasurements(prev => [...prev, measurement]);
    };

    window.addEventListener('keydown', handleKeyPress);
    if (measureMode) {
      window.addEventListener('click', handleClick, true);
    }

    return () => {
      window.removeEventListener('keydown', handleKeyPress);
      window.removeEventListener('click', handleClick, true);
    };
  }, [measureMode]);

  if (!measureMode) return null;

  return (
    <>
      {/* Measurement overlay */}
      <div className="fixed inset-0 pointer-events-none z-[9998]">
        {measurements.map((m, i) => (
          <div
            key={i}
            className="absolute border-2 border-yellow-400 bg-yellow-400/10"
            style={{
              left: m.x,
              top: m.y,
              width: m.width,
              height: m.height
            }}
          >
            <div className="absolute -top-6 left-0 bg-yellow-400 text-black px-1 text-xs">
              {Math.round(m.width)}×{Math.round(m.height)}
            </div>
          </div>
        ))}
      </div>

      {/* Measurements panel */}
      <div className="fixed top-4 right-4 bg-black/90 text-white p-4 rounded text-xs font-mono max-w-sm pointer-events-auto z-[9999]">
        <div className="mb-2 font-bold">Measurements (Press 'M' to toggle)</div>
        <div className="mb-2 text-yellow-400">Click elements to measure</div>
        
        <div className="max-h-64 overflow-y-auto space-y-2">
          {measurements.map((m, i) => (
            <div key={i} className="border-l-2 border-yellow-400 pl-2">
              <div className="font-semibold truncate">{m.element}</div>
              <div>Position: {Math.round(m.x)}, {Math.round(m.y)}</div>
              <div>Size: {Math.round(m.width)} × {Math.round(m.height)}</div>
              <div>Center: {Math.round(m.centerX)}, {Math.round(m.centerY)}</div>
            </div>
          ))}
        </div>
        
        {measurements.length > 0 && (
          <button 
            onClick={() => setMeasurements([])}
            className="mt-2 bg-red-600 px-2 py-1 rounded text-xs"
          >
            Clear
          </button>
        )}
      </div>
    </>
  );
};

export default MeasurementTool;