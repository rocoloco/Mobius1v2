
import {
  GlassPanel,
  GradientText,
  ConnectionPulse,
  MonoText,
} from './atoms';
import {
  ChatMessage,
  ViolationItem,
  ConstraintCard,
  ColorSwatch,
  VersionThumbnail,
} from './molecules';
import { Linkedin, EyeOff, Mic } from 'lucide-react';

/**
 * Component Showcase - Visual demo page for atomic and molecular components
 * This page displays all Luminous design system components in isolation
 * for visual review and testing.
 */
export function ComponentShowcase() {
  return (
    <div className="min-h-screen bg-[#101012] p-8 space-y-12">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-[#F1F5F9] mb-2">
            Luminous Design System
          </h1>
          <p className="text-[#94A3B8] mb-4">
            Component Showcase - Atomic & Molecular Components
          </p>
          <GlassPanel>
            <div className="p-6">
              <h2 className="text-lg font-semibold text-[#F1F5F9] mb-2">
                ✨ Enhanced Glassmorphism (2025)
              </h2>
              <p className="text-sm text-[#94A3B8] leading-relaxed">
                Modern glassmorphism with multi-layer depth, sophisticated glow effects, 
                gradient borders, subtle noise texture, and simulated light sources. 
                Each component features enhanced visual richness while maintaining the 
                neutral, precision-engineered aesthetic.
              </p>
            </div>
          </GlassPanel>
        </div>

        {/* Visual Enhancement Demo */}
        <section className="space-y-6 mb-16">
          <h2 className="text-2xl font-semibold text-[#F1F5F9] mb-4">
            Enhanced Glassmorphism Demo
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Enhanced Version */}
            <div>
              <p className="text-sm text-[#10B981] mb-3 font-semibold">✨ Enhanced (2025)</p>
              <GlassPanel glow>
                <div className="p-8">
                  <h3 className="text-xl font-bold text-[#F1F5F9] mb-3">
                    Multi-Layer Depth
                  </h3>
                  <ul className="space-y-2 text-sm text-[#94A3B8]">
                    <li>✓ Multi-layer shadows (4 layers)</li>
                    <li>✓ Gradient background with directional lighting</li>
                    <li>✓ Top highlight + bottom shadow</li>
                    <li>✓ Subtle noise texture overlay</li>
                    <li>✓ Enhanced glow with inner highlight</li>
                    <li>✓ Organic, tactile quality</li>
                  </ul>
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <p className="text-xs text-[#64748B]">
                      Notice the depth, richness, and dimensional quality
                    </p>
                  </div>
                </div>
              </GlassPanel>
            </div>
            
            {/* Comparison: Simulated "Before" */}
            <div>
              <p className="text-sm text-[#64748B] mb-3 font-semibold">Before (Flat)</p>
              <div 
                className="p-8 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl"
                style={{ boxShadow: '0 0 20px rgba(37, 99, 235, 0.15)' }}
              >
                <h3 className="text-xl font-bold text-[#F1F5F9] mb-3">
                  Single-Layer Flat
                </h3>
                <ul className="space-y-2 text-sm text-[#94A3B8]">
                  <li>• Single shadow layer</li>
                  <li>• Flat background color</li>
                  <li>• Simple border</li>
                  <li>• No texture</li>
                  <li>• Basic glow effect</li>
                  <li>• Minimal depth perception</li>
                </ul>
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-xs text-[#64748B]">
                    Functional but lacks visual richness
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Atomic Components Section */}
        <section className="space-y-8">
          <h2 className="text-2xl font-semibold text-[#F1F5F9] mb-4">
            Atomic Components
          </h2>

          {/* GlassPanel */}
          <div className="space-y-4">
            <h3 className="text-xl font-medium text-[#F1F5F9]">GlassPanel</h3>
            <p className="text-sm text-[#64748B] mb-4">
              Enhanced glassmorphism with multi-layer depth, subtle noise texture, and light simulation
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-[#94A3B8] mb-2">Default (with noise)</p>
                <GlassPanel>
                  <div className="p-6">
                    <p className="text-[#F1F5F9] mb-2 font-semibold">
                      Enhanced Depth
                    </p>
                    <p className="text-[#94A3B8] text-sm">
                      Multi-layer shadows, gradient borders, and subtle noise texture
                    </p>
                  </div>
                </GlassPanel>
              </div>
              <div>
                <p className="text-sm text-[#94A3B8] mb-2">With Glow</p>
                <GlassPanel glow>
                  <div className="p-6">
                    <p className="text-[#F1F5F9] mb-2 font-semibold">
                      Active State
                    </p>
                    <p className="text-[#94A3B8] text-sm">
                      Multi-layer glow with inner highlight and outer diffusion
                    </p>
                  </div>
                </GlassPanel>
              </div>
              <div>
                <p className="text-sm text-[#94A3B8] mb-2">Without Noise</p>
                <GlassPanel noise={false}>
                  <div className="p-6">
                    <p className="text-[#F1F5F9] mb-2 font-semibold">
                      Clean Glass
                    </p>
                    <p className="text-[#94A3B8] text-sm">
                      Pure glassmorphism without texture overlay
                    </p>
                  </div>
                </GlassPanel>
              </div>
            </div>
          </div>

          {/* GradientText */}
          <div className="space-y-4">
            <h3 className="text-xl font-medium text-[#F1F5F9]">GradientText</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <GlassPanel>
                <div className="p-6">
                  <p className="text-sm text-[#94A3B8] mb-3">Static</p>
                  <GradientText>Gemini 3 Pro - Ready</GradientText>
                </div>
              </GlassPanel>
              <GlassPanel>
                <div className="p-6">
                  <p className="text-sm text-[#94A3B8] mb-3">Animated</p>
                  <GradientText animate>Gemini 3 Pro - Thinking...</GradientText>
                </div>
              </GlassPanel>
            </div>
          </div>

          {/* ConnectionPulse */}
          <div className="space-y-4">
            <h3 className="text-xl font-medium text-[#F1F5F9]">
              ConnectionPulse
            </h3>
            <GlassPanel>
              <div className="p-6 flex gap-8 items-center flex-wrap">
                <div className="flex items-center gap-2">
                  <ConnectionPulse status="connected" />
                  <span className="text-[#94A3B8] text-sm">Connected</span>
                </div>
                <div className="flex items-center gap-2">
                  <ConnectionPulse status="connecting" />
                  <span className="text-[#94A3B8] text-sm">Connecting</span>
                </div>
                <div className="flex items-center gap-2">
                  <ConnectionPulse status="disconnected" />
                  <span className="text-[#94A3B8] text-sm">Disconnected</span>
                </div>
              </div>
            </GlassPanel>
          </div>

          {/* MonoText */}
          <div className="space-y-4">
            <h3 className="text-xl font-medium text-[#F1F5F9]">MonoText</h3>
            <GlassPanel>
              <div className="p-6 space-y-2">
                <div>
                  <span className="text-[#94A3B8]">Hex Code: </span>
                  <MonoText>#2563EB</MonoText>
                </div>
                <div>
                  <span className="text-[#94A3B8]">Font Family: </span>
                  <MonoText>Inter-Bold</MonoText>
                </div>
                <div>
                  <span className="text-[#94A3B8]">Distance: </span>
                  <MonoText>1.2</MonoText>
                </div>
              </div>
            </GlassPanel>
          </div>
        </section>

        {/* Molecular Components Section */}
        <section className="space-y-8 mt-16">
          <h2 className="text-2xl font-semibold text-[#F1F5F9] mb-4">
            Molecular Components
          </h2>

          {/* ChatMessage */}
          <div className="space-y-4">
            <h3 className="text-xl font-medium text-[#F1F5F9]">ChatMessage</h3>
            <div className="space-y-4">
              <ChatMessage
                role="user"
                content="Create a LinkedIn post image for our new product launch"
                timestamp={new Date('2024-01-15T10:30:00')}
              />
              <ChatMessage
                role="system"
                content="I'll create a LinkedIn post image following your brand guidelines. Generating now..."
                timestamp={new Date('2024-01-15T10:30:05')}
              />
            </div>
          </div>

          {/* ViolationItem */}
          <div className="space-y-4">
            <h3 className="text-xl font-medium text-[#F1F5F9]">ViolationItem</h3>
            <GlassPanel>
              <div className="p-6 space-y-2">
                <ViolationItem
                  violation={{
                    id: '1',
                    severity: 'critical',
                    message: 'Logo margin too small (8px, required: 16px)',
                  }}
                  onClick={() => console.log('Violation clicked')}
                />
                <ViolationItem
                  violation={{
                    id: '2',
                    severity: 'warning',
                    message: 'Font weight should be 600 (currently 400)',
                  }}
                  onClick={() => console.log('Violation clicked')}
                />
                <ViolationItem
                  violation={{
                    id: '3',
                    severity: 'info',
                    message: 'Consider using primary brand color',
                  }}
                  onClick={() => console.log('Violation clicked')}
                />
              </div>
            </GlassPanel>
          </div>

          {/* ConstraintCard */}
          <div className="space-y-4">
            <h3 className="text-xl font-medium text-[#F1F5F9]">
              ConstraintCard
            </h3>
            <div className="space-y-3">
              <ConstraintCard
                type="channel"
                label="LinkedIn"
                icon={<Linkedin className="w-4 h-4" />}
                active={false}
              />
              <ConstraintCard
                type="negative"
                label="No Comic Sans"
                icon={<EyeOff className="w-4 h-4" />}
                active={true}
              />
              <ConstraintCard
                type="voice"
                label="Professional Tone"
                icon={<Mic className="w-4 h-4" />}
                active={false}
                metadata={{
                  voiceVectors: {
                    formal: 0.8,
                    witty: 0.2,
                    technical: 0.6,
                    urgent: 0.3,
                  },
                }}
              />
            </div>
          </div>

          {/* ColorSwatch */}
          <div className="space-y-4">
            <h3 className="text-xl font-medium text-[#F1F5F9]">ColorSwatch</h3>
            <GlassPanel>
              <div className="p-6 space-y-3">
                <ColorSwatch
                  detected="#2664EC"
                  brand="#2563EB"
                  distance={1.2}
                  pass={true}
                />
                <ColorSwatch
                  detected="#FF5733"
                  brand="#EF4444"
                  distance={8.5}
                  pass={false}
                />
                <ColorSwatch
                  detected="#10B981"
                  brand="#10B981"
                  distance={0}
                  pass={true}
                />
              </div>
            </GlassPanel>
          </div>

          {/* VersionThumbnail */}
          <div className="space-y-4">
            <h3 className="text-xl font-medium text-[#F1F5F9]">
              VersionThumbnail
            </h3>
            <div className="flex gap-4">
              <VersionThumbnail
                imageUrl="https://via.placeholder.com/150"
                score={88}
                timestamp={new Date('2024-01-15T10:30:00')}
                active={false}
                onClick={() => console.log('Version 1 clicked')}
              />
              <VersionThumbnail
                imageUrl="https://via.placeholder.com/150"
                score={95}
                timestamp={new Date('2024-01-15T10:35:00')}
                active={true}
                onClick={() => console.log('Version 2 clicked')}
              />
              <VersionThumbnail
                imageUrl="https://via.placeholder.com/150"
                score={72}
                timestamp={new Date('2024-01-15T10:40:00')}
                active={false}
                onClick={() => console.log('Version 3 clicked')}
              />
            </div>
          </div>
        </section>

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-white/10">
          <p className="text-center text-[#64748B]">
            Luminous Structuralism Design System - Component Showcase
          </p>
        </div>
      </div>
    </div>
  );
}
