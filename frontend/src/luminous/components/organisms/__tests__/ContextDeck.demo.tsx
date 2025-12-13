import { useState } from 'react';
import { Linkedin, Twitter, EyeOff, Mic } from 'lucide-react';
import { ConstraintCard } from '../../molecules/ConstraintCard';
import { GlassPanel } from '../../atoms/GlassPanel';

/**
 * ContextDeck Demo Page
 * 
 * Interactive demo showcasing the ContextDeck with:
 * - Channel constraints (platform-specific rules)
 * - Negative constraints (forbidden elements)
 * - Voice constraints (brand voice vectors with radar chart)
 */
export function ContextDeckDemo() {
  const [activeConstraints, setActiveConstraints] = useState<string[]>([]);

  const mockConstraints = [
    {
      id: 'channel-linkedin',
      type: 'channel' as const,
      label: 'LinkedIn Professional',
      icon: <Linkedin size={20} />,
      active: activeConstraints.includes('channel-linkedin'),
    },
    {
      id: 'channel-twitter',
      type: 'channel' as const,
      label: 'Twitter/X Casual',
      icon: <Twitter size={20} />,
      active: activeConstraints.includes('channel-twitter'),
    },
    {
      id: 'negative-1',
      type: 'negative' as const,
      label: 'No stock photography',
      icon: <EyeOff size={20} />,
      active: activeConstraints.includes('negative-1'),
    },
    {
      id: 'negative-2',
      type: 'negative' as const,
      label: 'Avoid aggressive language',
      icon: <EyeOff size={20} />,
      active: activeConstraints.includes('negative-2'),
    },
    {
      id: 'negative-3',
      type: 'negative' as const,
      label: 'No competitor mentions',
      icon: <EyeOff size={20} />,
      active: activeConstraints.includes('negative-3'),
    },
    {
      id: 'voice-vectors',
      type: 'voice' as const,
      label: 'Brand Voice',
      icon: <Mic size={20} />,
      active: activeConstraints.includes('voice-vectors'),
      metadata: {
        voiceVectors: {
          formal: 0.7,
          witty: 0.4,
          technical: 0.8,
          urgent: 0.2,
        },
      },
    },
  ];

  const toggleConstraint = (id: string) => {
    setActiveConstraints(prev =>
      prev.includes(id)
        ? prev.filter(c => c !== id)
        : [...prev, id]
    );
  };

  return (
    <div className="min-h-screen bg-[#101012] p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-white">ContextDeck Component Demo</h1>
          <p className="text-slate-400">Constraint visualization panel</p>
        </div>

        {/* Demo Controls */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white">Demo Controls</h2>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm text-slate-400 mb-3">
                Click constraint cards below to toggle their active state (highlighted)
              </p>
              
              <div className="flex flex-wrap gap-2">
                {mockConstraints.map(constraint => (
                  <button
                    key={constraint.id}
                    onClick={() => toggleConstraint(constraint.id)}
                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                      activeConstraints.includes(constraint.id)
                        ? 'bg-purple-600 text-white'
                        : 'bg-white/5 text-slate-400 hover:bg-white/10'
                    }`}
                  >
                    {constraint.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setActiveConstraints(mockConstraints.map(c => c.id))}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors"
              >
                Activate All
              </button>
              
              <button
                onClick={() => setActiveConstraints([])}
                className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-lg transition-colors"
              >
                Deactivate All
              </button>
            </div>
          </div>

          <div className="text-sm text-slate-400 bg-white/5 rounded-lg p-4">
            <p><strong>Active Constraints:</strong> {activeConstraints.length} / {mockConstraints.length}</p>
            <p className="mt-2 text-xs">
              In the real dashboard, constraints are highlighted when their corresponding rules appear in violations
            </p>
          </div>
        </div>

        {/* Demo Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Demo */}
          <div className="md:col-span-2">
            <div className="h-[700px]">
              <GlassPanel className="h-full p-6">
                <div className="flex flex-col gap-4 h-full">
                  {/* Header */}
                  <div className="flex-shrink-0">
                    <h2 className="text-lg font-semibold text-slate-100">Context Deck</h2>
                    <p className="text-sm text-slate-400 mt-1">Active brand constraints</p>
                  </div>
                  
                  {/* Constraints list */}
                  <div className="flex-1 overflow-y-auto" style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                    {mockConstraints.map((constraint) => (
                      <ConstraintCard
                        key={constraint.id}
                        type={constraint.type}
                        label={constraint.label}
                        icon={constraint.icon}
                        active={constraint.active}
                        metadata={constraint.metadata}
                      />
                    ))}
                  </div>
                </div>
              </GlassPanel>
            </div>
          </div>

          {/* Side Info */}
          <div className="space-y-6">
            {/* Constraint Types */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Constraint Types</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <div className="flex items-center gap-2 text-blue-400 mb-1">
                    <Linkedin size={16} />
                    <span className="font-semibold">Channel</span>
                  </div>
                  <p className="text-slate-400 text-xs">
                    Platform-specific rules (LinkedIn, Twitter, etc.)
                  </p>
                </div>
                
                <div>
                  <div className="flex items-center gap-2 text-red-400 mb-1">
                    <EyeOff size={16} />
                    <span className="font-semibold">Negative</span>
                  </div>
                  <p className="text-slate-400 text-xs">
                    Forbidden elements or patterns
                  </p>
                </div>
                
                <div>
                  <div className="flex items-center gap-2 text-purple-400 mb-1">
                    <Mic size={16} />
                    <span className="font-semibold">Voice</span>
                  </div>
                  <p className="text-slate-400 text-xs">
                    Brand voice vectors with radar chart visualization
                  </p>
                </div>
              </div>
            </div>

            {/* Voice Vectors Explanation */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Voice Vectors</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Formal</span>
                  <span className="text-white font-mono">0.7</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Witty</span>
                  <span className="text-white font-mono">0.4</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Technical</span>
                  <span className="text-white font-mono">0.8</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Urgent</span>
                  <span className="text-white font-mono">0.2</span>
                </div>
              </div>
              <p className="text-xs text-slate-400 mt-3">
                Values range from 0.0 to 1.0, visualized in the radar chart
              </p>
            </div>

            {/* Features */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Features to Test</h3>
              <ul className="list-disc list-inside text-slate-400 space-y-2 text-sm">
                <li>Toggle constraints to see highlight effect</li>
                <li>Scroll through constraint list</li>
                <li>Observe different constraint types</li>
                <li>View radar chart on voice constraint</li>
                <li>Notice pill-shaped card design</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
