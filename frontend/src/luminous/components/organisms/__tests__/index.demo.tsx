import { useState } from 'react';
import { DirectorDemo } from './Director.demo';
import { CanvasDemo } from './Canvas.demo';
import { ComplianceGaugeDemo } from './ComplianceGauge.demo';
import { ContextDeckDemo } from './ContextDeck.demo';
import { TwinDataDemo } from './TwinData.demo';
import { AppShell } from '../AppShell';

type DemoPage = 'index' | 'director' | 'canvas' | 'gauge' | 'context' | 'twin';

/**
 * Organism Components Demo Index
 * 
 * Master demo page providing access to all organism component demos.
 * This page serves as the visual checkpoint for reviewing organism
 * components before integration into the full dashboard.
 */
export function OrganismDemoIndex() {
  const [currentPage, setCurrentPage] = useState<DemoPage>('index');
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connected');

  const demos = [
    {
      id: 'director' as const,
      name: 'Director',
      description: 'Multi-turn chat interface for AI prompt interaction',
      color: 'from-purple-600 to-blue-600',
      requirements: '4.1-4.11',
    },
    {
      id: 'canvas' as const,
      name: 'Canvas',
      description: 'Image viewport with bounding boxes and version scrubber',
      color: 'from-blue-600 to-cyan-600',
      requirements: '5.1-5.13',
    },
    {
      id: 'gauge' as const,
      name: 'Compliance Gauge',
      description: 'Radial donut chart with violation list',
      color: 'from-green-600 to-emerald-600',
      requirements: '6.1-6.10',
    },
    {
      id: 'context' as const,
      name: 'Context Deck',
      description: 'Constraint visualization panel',
      color: 'from-yellow-600 to-orange-600',
      requirements: '7.1-7.8',
    },
    {
      id: 'twin' as const,
      name: 'Twin Data',
      description: 'Visual token inspector (colors & fonts)',
      color: 'from-pink-600 to-rose-600',
      requirements: '8.1-8.9',
    },
  ];

  const renderDemo = () => {
    switch (currentPage) {
      case 'director':
        return <DirectorDemo />;
      case 'canvas':
        return <CanvasDemo />;
      case 'gauge':
        return <ComplianceGaugeDemo />;
      case 'context':
        return <ContextDeckDemo />;
      case 'twin':
        return <TwinDataDemo />;
      default:
        return null;
    }
  };

  if (currentPage !== 'index') {
    return (
      <div className="min-h-screen bg-[#101012]">
        {/* Navigation Bar */}
        <div className="fixed top-0 left-0 right-0 z-50 bg-white/5 backdrop-blur-md border-b border-white/10">
          <div className="px-6 py-4 flex items-center justify-between">
            <button
              onClick={() => setCurrentPage('index')}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Index
            </button>
            
            <div className="text-white font-semibold">
              {demos.find(d => d.id === currentPage)?.name} Demo
            </div>
            
            <div className="w-32"></div>
          </div>
        </div>
        
        {/* Demo Content */}
        <div className="pt-16">
          {renderDemo()}
        </div>
      </div>
    );
  }

  return (
    <AppShell
      connectionStatus={connectionStatus}
      onSettingsClick={() => alert('Settings clicked (demo)')}
    >
      <div className="min-h-[calc(100vh-64px)] p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold text-white">
              Organism Components Demo
            </h1>
            <p className="text-xl text-slate-400">
              Visual Checkpoint - Review organism components before integration
            </p>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600/20 border border-purple-500/50 rounded-lg">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
              <span className="text-purple-300 text-sm font-medium">
                Task 16: Visual Checkpoint
              </span>
            </div>
          </div>

          {/* Connection Status Demo */}
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Connection Status Demo</h2>
            <p className="text-sm text-slate-400 mb-4">
              Test the connection status indicator in the header above
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => setConnectionStatus('connected')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  connectionStatus === 'connected'
                    ? 'bg-green-600 text-white'
                    : 'bg-white/5 text-slate-400 hover:bg-white/10'
                }`}
              >
                Connected
              </button>
              <button
                onClick={() => setConnectionStatus('connecting')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  connectionStatus === 'connecting'
                    ? 'bg-yellow-600 text-white'
                    : 'bg-white/5 text-slate-400 hover:bg-white/10'
                }`}
              >
                Connecting
              </button>
              <button
                onClick={() => setConnectionStatus('disconnected')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  connectionStatus === 'disconnected'
                    ? 'bg-red-600 text-white'
                    : 'bg-white/5 text-slate-400 hover:bg-white/10'
                }`}
              >
                Disconnected
              </button>
            </div>
          </div>

          {/* Demo Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {demos.map((demo) => (
              <button
                key={demo.id}
                onClick={() => setCurrentPage(demo.id)}
                className="group relative bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300 text-left overflow-hidden"
              >
                {/* Gradient Background */}
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${demo.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
                ></div>

                {/* Content */}
                <div className="relative z-10 space-y-3">
                  <div className="flex items-start justify-between">
                    <h3 className="text-xl font-bold text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-purple-400 group-hover:to-blue-400 transition-all">
                      {demo.name}
                    </h3>
                    <svg
                      className="w-5 h-5 text-slate-400 group-hover:text-white group-hover:translate-x-1 transition-all"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>

                  <p className="text-sm text-slate-400 leading-relaxed">
                    {demo.description}
                  </p>

                  <div className="flex items-center gap-2 text-xs">
                    <span className="px-2 py-1 bg-white/5 rounded text-slate-400 font-mono">
                      Requirements {demo.requirements}
                    </span>
                  </div>
                </div>

                {/* Hover Glow Effect */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-blue-500/10 blur-xl"></div>
                </div>
              </button>
            ))}
          </div>

          {/* Instructions */}
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-semibold text-white">Review Instructions</h2>
            
            <div className="space-y-3 text-sm text-slate-400">
              <p>
                This is a visual checkpoint before integrating organism components into the full dashboard.
                Please review each component demo to ensure:
              </p>
              
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Glassmorphism effects render correctly</li>
                <li>Component interactions work as expected</li>
                <li>Color schemes match the Luminous design system</li>
                <li>Typography and spacing are consistent</li>
                <li>Animations and transitions are smooth</li>
                <li>Components handle different data states properly</li>
              </ul>

              <div className="bg-purple-600/20 border border-purple-500/50 rounded-lg p-4 mt-4">
                <p className="text-purple-300 font-medium">
                  ⚠️ PAUSE FOR USER FEEDBACK
                </p>
                <p className="text-purple-400 text-xs mt-2">
                  After reviewing all demos, provide feedback before proceeding to dashboard integration (Task 17).
                </p>
              </div>
            </div>
          </div>

          {/* Component Status */}
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Component Status</h2>
            
            <div className="space-y-2">
              {demos.map((demo) => (
                <div
                  key={demo.id}
                  className="flex items-center justify-between py-2 border-b border-white/5 last:border-0"
                >
                  <span className="text-slate-300">{demo.name}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-xs text-green-400">Implemented</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

export default OrganismDemoIndex;
