/**
 * Visual Demo: AppShell Component
 * 
 * This demo file showcases the AppShell component in different states
 * for visual verification during development.
 * 
 * To view this demo:
 * 1. Import this component in your main App.tsx or create a demo route
 * 2. Run the dev server: npm run dev
 */

import { useState } from 'react';
import { AppShell } from '../AppShell';

export function AppShellDemo() {
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connected');
  const [showSettings, setShowSettings] = useState(false);

  const handleSettingsClick = () => {
    setShowSettings(!showSettings);
    console.log('Settings clicked');
  };

  const cycleConnectionStatus = () => {
    setConnectionStatus(prev => {
      if (prev === 'connected') return 'disconnected';
      if (prev === 'disconnected') return 'connecting';
      return 'connected';
    });
  };

  return (
    <div className="min-h-screen">
      <AppShell
        connectionStatus={connectionStatus}
        onSettingsClick={handleSettingsClick}
        userAvatar="https://api.dicebear.com/7.x/avataaars/svg?seed=demo"
      >
        <div className="p-8 space-y-6">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold text-[#F1F5F9] mb-4">
              AppShell Component Demo
            </h1>
            
            <p className="text-[#94A3B8] mb-8">
              This demo showcases the AppShell organism component with interactive controls.
            </p>

            {/* Demo Controls */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-4">
              <h2 className="text-xl font-semibold text-[#F1F5F9] mb-4">
                Interactive Controls
              </h2>

              <div className="space-y-3">
                <div>
                  <label className="text-[#94A3B8] block mb-2">
                    Connection Status: <span className="text-[#F1F5F9] font-semibold">{connectionStatus}</span>
                  </label>
                  <button
                    onClick={cycleConnectionStatus}
                    className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition-opacity"
                  >
                    Cycle Connection Status
                  </button>
                </div>

                <div>
                  <label className="text-[#94A3B8] block mb-2">
                    Settings Panel: <span className="text-[#F1F5F9] font-semibold">{showSettings ? 'Open' : 'Closed'}</span>
                  </label>
                  <p className="text-[#64748B] text-sm">
                    Click the settings icon in the header to toggle
                  </p>
                </div>
              </div>
            </div>

            {/* Feature Checklist */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 mt-6">
              <h2 className="text-xl font-semibold text-[#F1F5F9] mb-4">
                Component Features
              </h2>
              
              <ul className="space-y-2 text-[#94A3B8]">
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Fixed header with 64px height
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Glassmorphism styling (bg-white/5, backdrop-blur-md)
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Mobius logo and "Brand Governance Engine" branding
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Connection status indicator (changes color)
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Settings icon button
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  User avatar (with fallback icon)
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Content area with pt-16 offset
                </li>
              </ul>
            </div>

            {/* Sample Content */}
            <div className="mt-6 space-y-4">
              <h2 className="text-2xl font-semibold text-[#F1F5F9]">
                Sample Content Area
              </h2>
              <p className="text-[#94A3B8]">
                This area demonstrates how content is rendered below the fixed header
                with the correct pt-16 offset. The header remains fixed at the top
                while this content scrolls.
              </p>
              
              {/* Add some filler content to demonstrate scrolling */}
              {Array.from({ length: 10 }).map((_, i) => (
                <div
                  key={i}
                  className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-4"
                >
                  <h3 className="text-lg font-semibold text-[#F1F5F9] mb-2">
                    Content Block {i + 1}
                  </h3>
                  <p className="text-[#94A3B8]">
                    This is sample content to demonstrate scrolling behavior.
                    The header should remain fixed at the top as you scroll down.
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </AppShell>
    </div>
  );
}
