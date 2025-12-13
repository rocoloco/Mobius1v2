import React from 'react';
import { Settings, User } from 'lucide-react';
import { ConnectionPulse } from '../atoms/ConnectionPulse';

interface AppShellProps {
  children: React.ReactNode;
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
  onSettingsClick?: () => void;
  userAvatar?: string;
}

/**
 * AppShell - Universal app shell with fixed header
 * 
 * Provides the top-level layout wrapper for the entire dashboard.
 * Features a fixed header with glassmorphism styling containing:
 * - Left: Mobius logo and "Brand Governance Engine" branding
 * - Right: Connection status, settings icon, and user avatar
 * 
 * @param children - Main content to render below the header
 * @param connectionStatus - WebSocket connection status
 * @param onSettingsClick - Callback when settings icon is clicked
 * @param userAvatar - Optional URL for user avatar image
 */
export function AppShell({
  children,
  connectionStatus,
  onSettingsClick,
  userAvatar,
}: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#101012] relative overflow-hidden">
      {/* Ambient Background Orbs - The Stage */}
      <div 
        className="absolute pointer-events-none"
        style={{
          top: '-10%',
          left: '-10%',
          width: '500px',
          height: '500px',
          background: 'rgba(124, 58, 237, 0.15)',
          borderRadius: '50%',
          filter: 'blur(128px)',
        }}
        aria-hidden="true"
      />
      <div 
        className="absolute pointer-events-none"
        style={{
          bottom: '-10%',
          right: '-10%',
          width: '600px',
          height: '600px',
          background: 'rgba(59, 130, 246, 0.08)',
          borderRadius: '50%',
          filter: 'blur(128px)',
        }}
        aria-hidden="true"
      />
      
      {/* Fixed Header */}
      <header
        className="fixed top-0 left-0 right-0 h-16 bg-white/5 backdrop-blur-md border-b border-white/10 z-50"
        data-testid="app-shell-header"
      >
        <div className="h-full px-6 flex items-center justify-between">
          {/* Left: Logo and Branding */}
          <div className="flex items-center gap-3">
            {/* Mobius Logo */}
            <img
              src="/mobius-icon-dark.svg"
              alt=""
              style={{ width: '40px', height: '40px' }}
              aria-hidden="true"
            />
            
            {/* Brand Text - h1 for proper heading structure */}
            <h1 className="text-[#F1F5F9] font-semibold text-base tracking-tight m-0">
              Brand Governance Engine
            </h1>
          </div>

          {/* Right: Utilities */}
          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              <ConnectionPulse status={connectionStatus} />
            </div>

            {/* Settings Icon */}
            <button
              onClick={onSettingsClick}
              className="w-11 h-11 rounded-lg hover:bg-white/5 flex items-center justify-center transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 hover-scale"
              aria-label="Settings"
              data-testid="settings-button"
              style={{ minWidth: '44px', minHeight: '44px' }}
            >
              <Settings className="w-5 h-5 text-[#94A3B8]" />
            </button>

            {/* User Avatar */}
            <button
              className="w-11 h-11 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center overflow-hidden focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300 hover-scale"
              data-testid="user-avatar"
              aria-label="User profile"
              style={{ minWidth: '44px', minHeight: '44px' }}
            >
              {userAvatar ? (
                <img
                  src={userAvatar}
                  alt="User avatar"
                  className="w-full h-full object-cover"
                />
              ) : (
                <User className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content with offset for fixed header */}
      <main className="relative z-10" style={{ marginTop: '64px', height: 'calc(100vh - 64px)', overflow: 'hidden' }}>
        {children}
      </main>
    </div>
  );
}
