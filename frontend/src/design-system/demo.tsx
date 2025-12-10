/**
 * Industrial Design System Demo Component
 * 
 * Demonstrates the foundation layer capabilities
 */

import React from 'react';
import { industrial } from './index';

export const DesignSystemDemo: React.FC = () => {
  const [isPressed, setIsPressed] = React.useState(false);

  return (
    <div className="p-8 bg-surface-primary min-h-screen">
      <h1 className="text-2xl font-bold text-ink mb-8">Industrial Design System - Foundation Layer</h1>
      
      {/* Neumorphic Shadow Examples */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="p-6 rounded-lg shadow-neumorphic-raised-subtle">
          <h3 className="font-semibold text-ink mb-2">Subtle Raised</h3>
          <p className="text-ink-muted">Gentle elevation effect</p>
        </div>
        
        <div className="p-6 rounded-lg shadow-neumorphic-raised-normal">
          <h3 className="font-semibold text-ink mb-2">Normal Raised</h3>
          <p className="text-ink-muted">Standard elevation effect</p>
        </div>
        
        <div className="p-6 rounded-lg shadow-neumorphic-raised-deep">
          <h3 className="font-semibold text-ink mb-2">Deep Raised</h3>
          <p className="text-ink-muted">Strong elevation effect</p>
        </div>
      </div>

      {/* Recessed Examples */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="p-6 rounded-lg shadow-neumorphic-recessed-subtle">
          <h3 className="font-semibold text-ink mb-2">Subtle Recessed</h3>
          <p className="text-ink-muted">Gentle inset effect</p>
        </div>
        
        <div className="p-6 rounded-lg shadow-neumorphic-recessed-normal">
          <h3 className="font-semibold text-ink mb-2">Normal Recessed</h3>
          <p className="text-ink-muted">Standard inset effect</p>
        </div>
        
        <div className="p-6 rounded-lg shadow-neumorphic-recessed-deep">
          <h3 className="font-semibold text-ink mb-2">Deep Recessed</h3>
          <p className="text-ink-muted">Strong inset effect</p>
        </div>
      </div>

      {/* Press Physics Demo */}
      <div className="mb-8">
        <h3 className="font-semibold text-ink mb-4">Press Physics Demo</h3>
        <button
          className={`px-6 py-3 rounded-lg font-medium text-ink transition-all duration-100 ease-mechanical ${
            isPressed 
              ? 'shadow-neumorphic-recessed-normal translate-y-[2px]' 
              : 'shadow-neumorphic-raised-normal'
          }`}
          onMouseDown={() => setIsPressed(true)}
          onMouseUp={() => setIsPressed(false)}
          onMouseLeave={() => setIsPressed(false)}
        >
          Press Me - Feel the Physics!
        </button>
      </div>

      {/* LED Indicators */}
      <div className="mb-8">
        <h3 className="font-semibold text-ink mb-4">LED Status Indicators</h3>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-led-off"></div>
            <span className="text-ink-muted">Off</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-led-on shadow-led-glow"></div>
            <span className="text-ink-muted">On</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-led-error shadow-led-glow"></div>
            <span className="text-ink-muted">Error</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-led-warning shadow-led-glow"></div>
            <span className="text-ink-muted">Warning</span>
          </div>
        </div>
      </div>

      {/* Manufacturing Details */}
      <div className="mb-8">
        <h3 className="font-semibold text-ink mb-4">Manufacturing Details</h3>
        <div className="relative p-6 rounded-lg shadow-neumorphic-raised-normal bg-surface-brushed">
          <div className="screw screw-tl"></div>
          <div className="screw screw-tr"></div>
          <div className="screw screw-bl"></div>
          <div className="screw screw-br"></div>
          
          <h4 className="font-medium text-ink mb-2">Bolted Panel</h4>
          <p className="text-ink-muted">Panel with corner screws and brushed surface texture</p>
          
          <div className="mt-4 h-8 bg-vent-horizontal opacity-30"></div>
        </div>
      </div>

      {/* Animation Examples */}
      <div className="mb-8">
        <h3 className="font-semibold text-ink mb-4">Mechanical Animations</h3>
        <div className="flex gap-4">
          <div className="w-4 h-4 rounded-full bg-led-on animate-led-pulse"></div>
          <div className="px-4 py-2 rounded shadow-neumorphic-raised-normal animate-mechanical-slide-in">
            Slide In
          </div>
          <div className="px-4 py-2 rounded shadow-neumorphic-raised-normal animate-mechanical-fade-in">
            Fade In
          </div>
        </div>
      </div>

      {/* Design Token Information */}
      <div className="p-6 rounded-lg shadow-neumorphic-recessed-normal bg-surface-secondary">
        <h3 className="font-semibold text-ink mb-4">Design System Info</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <strong>Version:</strong> {industrial.tokens.shadows ? '1.0.0' : 'Loading...'}
          </div>
          <div>
            <strong>Theme:</strong> Industrial Skeuomorphic
          </div>
          <div>
            <strong>Light Source:</strong> Top-Left (-1, -1)
          </div>
          <div>
            <strong>Easing:</strong> Mechanical Cubic Bezier
          </div>
        </div>
      </div>
    </div>
  );
};

export default DesignSystemDemo;