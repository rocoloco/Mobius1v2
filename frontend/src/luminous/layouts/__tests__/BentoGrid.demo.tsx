/**
 * BentoGrid Demo
 * 
 * Visual demonstration of the BentoGrid layout with placeholder content
 * for each zone.
 */

import { BentoGrid } from '../BentoGrid';
import { GlassPanel } from '../../components/atoms/GlassPanel';

export function BentoGridDemo() {
  return (
    <div className="min-h-screen bg-[#101012]">
      {/* Mock Header */}
      <div className="h-16 bg-white/5 backdrop-blur-md border-b border-white/10 flex items-center px-6">
        <span className="text-white/90 font-semibold">Mobius Brand Governance Engine</span>
      </div>

      {/* BentoGrid Layout */}
      <BentoGrid
        director={
          <GlassPanel className="h-full flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-white/90 mb-2">Director</h2>
              <p className="text-white/60 text-sm">Multi-turn chat interface</p>
              <p className="text-white/40 text-xs mt-1">Spans 2 rows</p>
            </div>
          </GlassPanel>
        }
        canvas={
          <GlassPanel className="h-full flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-white/90 mb-2">Canvas</h2>
              <p className="text-white/60 text-sm">Image viewport with bounding boxes</p>
              <p className="text-white/40 text-xs mt-1">Spans 3 rows (full height)</p>
            </div>
          </GlassPanel>
        }
        gauge={
          <GlassPanel className="h-full flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-white/90 mb-2">Compliance Gauge</h2>
              <p className="text-white/60 text-sm">Radial donut chart</p>
              <p className="text-white/40 text-xs mt-1">Spans 1 row</p>
            </div>
          </GlassPanel>
        }
        context={
          <GlassPanel className="h-full flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-white/90 mb-2">Context Deck</h2>
              <p className="text-white/60 text-sm">Constraint visualization</p>
              <p className="text-white/40 text-xs mt-1">Spans 1 row</p>
            </div>
          </GlassPanel>
        }
        twin={
          <GlassPanel className="h-full flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-white/90 mb-2">Twin Data</h2>
              <p className="text-white/60 text-sm">Visual token inspector</p>
              <p className="text-white/40 text-xs mt-1">Spans 2 rows</p>
            </div>
          </GlassPanel>
        }
      />
    </div>
  );
}

export default BentoGridDemo;
