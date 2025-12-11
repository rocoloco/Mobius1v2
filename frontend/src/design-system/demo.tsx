/**
 * Industrial Design System Demo
 * 
 * Clean, organized showcase of all industrial components with tabbed navigation
 */

import React, { useState } from 'react';
import { 
  industrialTokens, 
  NeumorphicUtils,
  IndustrialCard,
  IndustrialButton,
  IndustrialInput,
  IndustrialIndicator,
  IndustrialIndicatorGroup,
  PolishedIndustrialButton
} from './index';
import { PhillipsHeadBolt, FlatheadBolt, TorxHeadBolt, HexHeadBolt } from './components/IndustrialBolts';
import { EnhancedIndustrialButton } from './components/EnhancedIndustrialButton';
import { VentGrille, ConnectorPort, SurfaceTexture, WarningLabel, SerialPlate } from './components/IndustrialManufacturing';
import { 
  HighContrastToggle, 
  SkipLinks, 
  AccessibleStatusIndicator, 
  KeyboardNavigationInfo 
} from './components/AccessibilityEnhancements';
import { 
  ResponsiveGrid, 
  TouchFriendlyButton,
  SwipeableTabs 
} from './components/ResponsiveGrid';

// Tab configuration for organized navigation
const tabs = [
  { id: 'overview', label: 'Overview', icon: '🏭', description: 'System overview and introduction' },
  { id: 'controls', label: 'Control Panels', icon: '⚙️', description: 'Industrial control panels and cards' },
  { id: 'buttons', label: 'Buttons & Actions', icon: '🔘', description: 'Interactive buttons and controls' },
  { id: 'forms', label: 'Form Controls', icon: '📝', description: 'Input fields and form elements' },
  { id: 'indicators', label: 'Status & Feedback', icon: '💡', description: 'Status indicators and feedback' },
  { id: 'hardware', label: 'Hardware Details', icon: '🔧', description: 'Manufacturing hardware components' },
  { id: 'foundation', label: 'Design Tokens', icon: '🎨', description: 'Colors, shadows, and design foundation' }
];

export const IndustrialDemo: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [inputValue, setInputValue] = useState('');
  const [cardStatus, setCardStatus] = useState<'active' | 'inactive' | 'error' | 'warning'>('active');

  // Tab navigation component with mobile optimization
  const TabNavigation = () => (
    <div className="mb-8">
      {/* Desktop/Tablet Navigation */}
      <div className="hidden sm:block">
        <div 
          className="flex flex-wrap gap-2 p-2 rounded-xl"
          style={{ 
            backgroundColor: industrialTokens.colors.surface.secondary,
            ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed')
          }}
        >
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all duration-200
                hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
                ${activeTab === tab.id ? 'text-blue-600' : 'text-gray-600 hover:text-gray-800'}
              `}
              style={{
                backgroundColor: activeTab === tab.id 
                  ? industrialTokens.colors.surface.primary 
                  : 'transparent',
                ...(activeTab === tab.id 
                  ? NeumorphicUtils.getPremiumShadowStyle('normal', 'raised')
                  : {}
                )
              }}
              aria-pressed={activeTab === tab.id}
              title={tab.description}
            >
              <span className="text-lg" role="img" aria-label={tab.label}>
                {tab.icon}
              </span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Mobile Navigation with Swipe Support */}
      <div className="sm:hidden">
        <div 
          className="rounded-xl p-2"
          style={{ 
            backgroundColor: industrialTokens.colors.surface.secondary,
            ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed')
          }}
        >
          <SwipeableTabs 
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
        </div>
        <div className="mt-2 text-center">
          <p className="text-sm text-gray-500">
            Swipe left/right to navigate tabs
          </p>
        </div>
      </div>
      
      {/* Active tab description */}
      <div className="mt-4 text-center">
        <p 
          className="text-base sm:text-lg"
          style={{ color: industrialTokens.colors.text.secondary }}
        >
          {tabs.find(tab => tab.id === activeTab)?.description}
        </p>
      </div>
    </div>
  );

  return (
    <div 
      className="min-h-screen p-4 sm:p-8"
      style={{ backgroundColor: industrialTokens.colors.surface.primary }}
    >
      {/* Skip Links for Accessibility */}
      <SkipLinks />
      
      <div className="max-w-7xl mx-auto">
        {/* Accessibility Controls */}
        <div className="flex justify-end gap-4 mb-6">
          <HighContrastToggle />
          <KeyboardNavigationInfo />
        </div>

        {/* Header */}
        <div className="text-center mb-8" id="main-content">
          <h1 
            className="text-3xl sm:text-5xl font-bold mb-4"
            style={{ color: industrialTokens.colors.text.primary }}
          >
            Industrial Design System
          </h1>
          <p 
            className="text-lg sm:text-xl mb-6"
            style={{ color: industrialTokens.colors.text.secondary }}
          >
            Professional skeuomorphic components for industrial interfaces
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <WarningLabel type="notice" text="DEMO MODE" />
            <SerialPlate model="Design System v1.0" serialNumber="Build: 2024.12.09" />
          </div>
        </div>

        {/* Tab Navigation */}
        <nav id="navigation" aria-label="Component categories">
          <TabNavigation />
        </nav>

        {/* Tab Content */}
        <div className="space-y-8">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <section className="space-y-8">
              <div className="text-center space-y-6">
                <h2 className="text-3xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
                  Welcome to the Industrial Design System
                </h2>
                <p className="text-lg max-w-3xl mx-auto leading-relaxed" style={{ color: industrialTokens.colors.text.secondary }}>
                  A comprehensive collection of skeuomorphic components designed for industrial and manufacturing interfaces. 
                  Each component is crafted with attention to physical realism, accessibility, and professional aesthetics.
                </p>
              </div>

              {/* Quick Preview Grid */}
              <ResponsiveGrid 
                columns={{ mobile: 1, tablet: 2, desktop: 3 }}
                gap="md"
              >
                {tabs.slice(1).map((tab) => (
                  <TouchFriendlyButton
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    type="secondary"
                    size="lg"
                    fullWidth
                  >
                    <div className="flex items-center gap-3 text-left">
                      <span className="text-2xl" role="img" aria-label={tab.label}>
                        {tab.icon}
                      </span>
                      <div>
                        <h3 className="text-lg font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
                          {tab.label}
                        </h3>
                        <p className="text-sm" style={{ color: industrialTokens.colors.text.secondary }}>
                          {tab.description}
                        </p>
                      </div>
                    </div>
                  </TouchFriendlyButton>
                ))}
              </ResponsiveGrid>

              {/* Key Features */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
                <div className="space-y-4">
                  <h3 className="text-2xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
                    Key Features
                  </h3>
                  <ul className="space-y-3" style={{ color: industrialTokens.colors.text.secondary }}>
                    <li className="flex items-center gap-3">
                      <span className="text-green-500">✓</span>
                      Realistic neumorphic shadows and depth
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-green-500">✓</span>
                      WCAG 2.1 AA accessibility compliance
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-green-500">✓</span>
                      Responsive design for all screen sizes
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-green-500">✓</span>
                      TypeScript support with full type safety
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-green-500">✓</span>
                      Consistent 8px grid system
                    </li>
                  </ul>
                </div>
                
                <div className="space-y-4">
                  <h3 className="text-2xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
                    Use Cases
                  </h3>
                  <ul className="space-y-3" style={{ color: industrialTokens.colors.text.secondary }}>
                    <li className="flex items-center gap-3">
                      <span className="text-blue-500">•</span>
                      Manufacturing control systems
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-blue-500">•</span>
                      Industrial monitoring dashboards
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-blue-500">•</span>
                      Equipment configuration interfaces
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-blue-500">•</span>
                      Process automation tools
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-blue-500">•</span>
                      Quality control applications
                    </li>
                  </ul>
                </div>
              </div>
            </section>
          )}

          {/* Control Panels Tab */}
          {activeTab === 'controls' && (
            <section className="space-y-8">
              <div className="text-center">
                <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                  Industrial Control Panels
                </h2>
                <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                  Robust control panels with realistic hardware details and interactive feedback
                </p>
              </div>
              
              <ResponsiveGrid 
                columns={{ mobile: 1, tablet: 2, desktop: 3 }}
                gap="lg"
              >
                <IndustrialCard
                  title="System Status"
                  subtitle="Main control panel"
                  status={cardStatus}
                  bolted={true}
                  size="md"
                  onClick={() => {
                    const statuses: Array<'active' | 'inactive' | 'error' | 'warning'> = ['active', 'inactive', 'error', 'warning'];
                    const currentIndex = statuses.indexOf(cardStatus);
                    const nextIndex = (currentIndex + 1) % statuses.length;
                    setCardStatus(statuses[nextIndex]);
                  }}
                >
                  <p className="mb-4">Click to cycle through status states</p>
                  <div className="flex gap-3">
                    <IndustrialIndicator status="on" size="sm" label="Power" />
                    <IndustrialIndicator status="warning" size="sm" label="Temp" />
                  </div>
                </IndustrialCard>

                <IndustrialCard
                  title="Manufacturing Unit"
                  subtitle="Production line A"
                  status="active"
                  bolted={true}
                  ventilated={true}
                  manufacturing={{ texture: 'brushed' }}
                  size="md"
                >
                  <p className="mb-4">Ventilated panel with brushed texture</p>
                  <IndustrialIndicatorGroup
                    indicators={[
                      { id: '1', status: 'on', label: 'Line 1' },
                      { id: '2', status: 'on', label: 'Line 2' },
                      { id: '3', status: 'error', label: 'Line 3' },
                    ]}
                    size="sm"
                    orientation="vertical"
                  />
                </IndustrialCard>

                <IndustrialCard
                  title="Data Terminal"
                  subtitle="I/O Interface"
                  status="inactive"
                  bolted={false}
                  manufacturing={{ connectors: true }}
                  size="md"
                >
                  <p className="mb-4">Terminal with connector ports</p>
                  <IndustrialInput
                    placeholder="Enter command..."
                    size="sm"
                    ledIndicator={true}
                  />
                </IndustrialCard>
              </ResponsiveGrid>

              {/* Interactive Features */}
              <div className="mt-12 p-6 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                <h3 className="text-xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                  Interactive Features
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium mb-2">Click Interactions</h4>
                    <p className="text-sm" style={{ color: industrialTokens.colors.text.secondary }}>
                      Cards respond to clicks with visual feedback and state changes
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Status Indicators</h4>
                    <p className="text-sm" style={{ color: industrialTokens.colors.text.secondary }}>
                      Real-time status updates with color-coded LED indicators
                    </p>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Buttons Tab */}
          {activeTab === 'buttons' && (
            <section className="space-y-8">
              <div className="text-center">
                <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                  Industrial Control Buttons
                </h2>
                <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                  Tactile buttons with enhanced physics and visual feedback for critical operations
                </p>
              </div>
              
              <div className="space-y-8">
                {/* Enhanced Buttons */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Enhanced with Physics
                  </h3>
                  <div className="p-8 rounded-xl space-y-6" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                    <div className="flex flex-wrap gap-6 justify-center">
                      <EnhancedIndustrialButton
                        type="primary"
                        size="md"
                        glowOnHover={true}
                      >
                        Primary Control
                      </EnhancedIndustrialButton>

                      <EnhancedIndustrialButton
                        type="success"
                        size="md"
                        glowOnHover={true}
                      >
                        Start Process
                      </EnhancedIndustrialButton>

                      <EnhancedIndustrialButton
                        type="emergency"
                        size="lg"
                        glowOnHover={true}
                        manufacturing={{ screws: true }}
                      >
                        EMERGENCY STOP
                      </EnhancedIndustrialButton>
                    </div>
                    
                    <div className="text-center">
                      <p className="text-sm" style={{ color: industrialTokens.colors.text.muted }}>
                        Enhanced buttons feature realistic physics, glow effects, and tactile feedback
                      </p>
                    </div>
                  </div>
                </div>

                {/* Translucent Resin Keycap Buttons */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Translucent Resin Keycaps
                  </h3>
                  <p className="text-gray-600">
                    Buttons that simulate translucent resin keycaps with internal LEDs. When active, they bloom with internal light diffusion.
                  </p>
                  <div className="p-8 rounded-xl space-y-8" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div className="text-center space-y-4">
                        <h4 className="text-lg font-medium">Inactive State</h4>
                        <div className="flex flex-col gap-4 items-center">
                          <PolishedIndustrialButton variant="resin" size="lg">
                            Generate Report
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="resin" size="md" glowColor="#10b981">
                            Start Process
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="resin" size="sm" glowColor="#f59e0b">
                            Quick Action
                          </PolishedIndustrialButton>
                        </div>
                        <p className="text-sm text-gray-600">Translucent resin material</p>
                      </div>
                      
                      <div className="text-center space-y-4">
                        <h4 className="text-lg font-medium">Active/Blooming State</h4>
                        <div className="flex flex-col gap-4 items-center">
                          <PolishedIndustrialButton variant="resin" size="lg" active={true}>
                            Generate Report
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="resin" size="md" active={true} glowColor="#10b981">
                            Start Process
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="resin" size="sm" active={true} glowColor="#f59e0b">
                            Quick Action
                          </PolishedIndustrialButton>
                        </div>
                        <p className="text-sm text-gray-600">Internal LED bloom with light diffusion</p>
                      </div>
                    </div>

                    <div className="p-6 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                      <h4 className="text-lg font-medium mb-3">Loading State Demo</h4>
                      <div className="flex justify-center">
                        <PolishedIndustrialButton variant="resin" size="lg" loading={true} glowColor="#3b82f6">
                          Processing...
                        </PolishedIndustrialButton>
                      </div>
                      <p className="text-sm text-gray-600 text-center mt-3">
                        Loading state automatically activates the internal LED bloom
                      </p>
                    </div>
                  </div>
                </div>

                {/* Standard Buttons */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Standard Industrial
                  </h3>
                  <div className="p-8 rounded-xl space-y-6" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                    <div className="flex flex-wrap gap-6 justify-center">
                      <IndustrialButton type="primary" size="md">
                        Primary Action
                      </IndustrialButton>

                      <IndustrialButton type="secondary" size="md">
                        Secondary Action
                      </IndustrialButton>

                      <IndustrialButton 
                        type="primary" 
                        size="lg"
                        manufacturing={{ screws: true }}
                      >
                        Bolted Control
                      </IndustrialButton>
                    </div>
                    
                    <div className="text-center">
                      <p className="text-sm" style={{ color: industrialTokens.colors.text.muted }}>
                        Standard buttons with consistent styling and optional hardware details
                      </p>
                    </div>
                  </div>
                </div>

                {/* Button Variants Grid */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Button Variants & Sizes
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Size Variants */}
                    <div className="p-6 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                      <h4 className="text-lg font-medium mb-4">Size Variants</h4>
                      <div className="space-y-4">
                        <IndustrialButton type="primary" size="sm">Small</IndustrialButton>
                        <IndustrialButton type="primary" size="md">Medium</IndustrialButton>
                        <IndustrialButton type="primary" size="lg">Large</IndustrialButton>
                      </div>
                    </div>

                    {/* Type Variants */}
                    <div className="p-6 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                      <h4 className="text-lg font-medium mb-4">Type Variants</h4>
                      <div className="space-y-4">
                        <IndustrialButton type="primary" size="md">Primary</IndustrialButton>
                        <IndustrialButton type="secondary" size="md">Secondary</IndustrialButton>
                        <IndustrialButton type="danger" size="md">Danger</IndustrialButton>
                      </div>
                    </div>

                    {/* State Variants */}
                    <div className="p-6 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                      <h4 className="text-lg font-medium mb-4">State Variants</h4>
                      <div className="space-y-4">
                        <IndustrialButton type="primary" size="md">Normal</IndustrialButton>
                        <IndustrialButton type="primary" size="md" disabled>Disabled</IndustrialButton>
                        <IndustrialButton type="primary" size="md" manufacturing={{ screws: true }}>With Hardware</IndustrialButton>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Forms Tab */}
          {activeTab === 'forms' && (
            <section className="space-y-8">
              <div className="text-center">
                <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                  Industrial Form Controls
                </h2>
                <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                  Robust input fields with clear status indication and accessibility features
                </p>
              </div>
              
              <div className="space-y-8">
                {/* Input States */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Input States & Validation
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <IndustrialInput
                      label="System Parameter"
                      placeholder="Enter value..."
                      value={inputValue}
                      onChange={setInputValue}
                      status="normal"
                      helperText="Enter a numeric value between 0-100"
                      required
                    />

                    <IndustrialInput
                      label="Error Condition"
                      placeholder="Error detected..."
                      status="error"
                      helperText="This field has an error"
                      disabled
                    />

                    <IndustrialInput
                      label="Success State"
                      placeholder="Operation complete"
                      status="success"
                      helperText="Operation completed successfully"
                    />

                    <IndustrialInput
                      label="Warning State"
                      placeholder="Check parameters..."
                      status="warning"
                      helperText="Please verify the input parameters"
                    />
                  </div>
                </div>

                {/* Input Variants */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Input Variants & Features
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-6">
                      <IndustrialInput
                        label="With LED Indicator"
                        placeholder="Status monitoring..."
                        ledIndicator={true}
                        helperText="LED indicates active monitoring"
                      />
                      
                      <IndustrialInput
                        label="Large Size Input"
                        placeholder="Large input field..."
                        size="lg"
                        helperText="Larger input for better visibility"
                      />
                    </div>
                    
                    <div className="space-y-6">
                      <IndustrialInput
                        label="Small Size Input"
                        placeholder="Compact input..."
                        size="sm"
                        helperText="Compact size for dense layouts"
                      />
                      
                      <IndustrialInput
                        label="Disabled Input"
                        placeholder="Cannot edit..."
                        disabled
                        helperText="Input is disabled"
                      />
                    </div>
                  </div>
                </div>

                {/* Form Example */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Complete Form Example
                  </h3>
                  <div className="p-8 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <IndustrialInput
                          label="Machine ID"
                          placeholder="Enter machine identifier..."
                          required
                          helperText="Unique identifier for the machine"
                        />
                        
                        <IndustrialInput
                          label="Operating Temperature"
                          placeholder="Temperature in °C..."
                          status="warning"
                          helperText="Current: 85°C (Warning threshold: 80°C)"
                        />
                      </div>
                      
                      <IndustrialInput
                        label="Process Description"
                        placeholder="Describe the manufacturing process..."
                        helperText="Detailed description of the current process"
                      />
                      
                      <div className="flex gap-4 pt-4">
                        <IndustrialButton type="primary" size="md">
                          Save Configuration
                        </IndustrialButton>
                        <IndustrialButton type="secondary" size="md">
                          Reset Form
                        </IndustrialButton>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Indicators Tab */}
          {activeTab === 'indicators' && (
            <section className="space-y-8">
              <div className="text-center">
                <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                  Industrial Status Indicators
                </h2>
                <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                  Clear visual feedback with LED indicators, animations, and accessibility features
                </p>
              </div>
              
              <div className="space-y-8">
                {/* Individual Indicators */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Individual Status LEDs
                  </h3>
                  <div className="p-8 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8">
                      <div className="text-center">
                        <IndustrialIndicator status="off" size="lg" label="System Offline" />
                        <p className="mt-2 text-sm font-medium">Offline</p>
                      </div>
                      <div className="text-center">
                        <IndustrialIndicator status="on" size="lg" label="System Online" glow={true} />
                        <p className="mt-2 text-sm font-medium">Online</p>
                      </div>
                      <div className="text-center">
                        <IndustrialIndicator status="error" size="lg" label="Critical Error" pulse={true} />
                        <p className="mt-2 text-sm font-medium">Error</p>
                      </div>
                      <div className="text-center">
                        <IndustrialIndicator status="warning" size="lg" label="Warning State" />
                        <p className="mt-2 text-sm font-medium">Warning</p>
                      </div>
                      <div className="text-center">
                        <IndustrialIndicator status="success" size="lg" label="All Systems Go" />
                        <p className="mt-2 text-sm font-medium">Success</p>
                      </div>
                    </div>
                    
                    <div className="mt-12 space-y-6">
                      <h4 className="text-lg font-medium text-center">Soft Plastic vs. Sharp LED Comparison</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="text-center p-6 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                          <h5 className="text-md font-medium mb-4">Diffused (Soft Plastic)</h5>
                          <div className="flex justify-center gap-4 mb-2">
                            <IndustrialIndicator status="on" size="lg" diffused={true} />
                            <IndustrialIndicator status="error" size="lg" diffused={true} />
                            <IndustrialIndicator status="warning" size="lg" diffused={true} />
                          </div>
                          <p className="text-xs text-gray-600">LEDs buried under translucent plastic</p>
                        </div>
                        <div className="text-center p-6 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                          <h5 className="text-md font-medium mb-4">Sharp (Traditional)</h5>
                          <div className="flex justify-center gap-4 mb-2">
                            <IndustrialIndicator status="on" size="lg" diffused={false} />
                            <IndustrialIndicator status="error" size="lg" diffused={false} />
                            <IndustrialIndicator status="warning" size="lg" diffused={false} />
                          </div>
                          <p className="text-xs text-gray-600">Traditional sharp LED indicators</p>
                        </div>
                      </div>
                    </div>

                    <div className="mt-8 space-y-4">
                      <h4 className="text-lg font-medium text-center">Accessible Status Indicators</h4>
                      <div className="flex flex-wrap justify-center gap-4">
                        <AccessibleStatusIndicator status="on" label="System Power" size="md" />
                        <AccessibleStatusIndicator status="error" label="Critical Alert" size="md" />
                        <AccessibleStatusIndicator status="warning" label="Temperature" size="md" />
                        <AccessibleStatusIndicator status="success" label="All Systems" size="md" />
                      </div>
                      <p className="text-sm text-center" style={{ color: industrialTokens.colors.text.muted }}>
                        Enhanced indicators with text alternatives for screen readers and colorblind users
                      </p>
                    </div>
                  </div>
                </div>

                {/* Indicator Groups */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Production Line Status
                  </h3>
                  <div className="p-8 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                    <IndustrialIndicatorGroup
                      indicators={[
                        { id: 'power', status: 'on', label: 'Power' },
                        { id: 'network', status: 'on', label: 'Network' },
                        { id: 'temp', status: 'warning', label: 'Temperature' },
                        { id: 'pressure', status: 'error', label: 'Pressure' },
                        { id: 'flow', status: 'on', label: 'Flow Rate' },
                      ]}
                      size="md"
                      glow={true}
                      orientation="horizontal"
                    />
                    
                    <div className="mt-6 text-center">
                      <p className="text-sm" style={{ color: industrialTokens.colors.text.muted }}>
                        Grouped indicators for monitoring multiple system parameters
                      </p>
                    </div>
                  </div>
                </div>

                {/* Vertical Indicator Group */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Vertical Status Panel
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="p-8 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                      <IndustrialIndicatorGroup
                        indicators={[
                          { id: 'line1', status: 'on', label: 'Production Line 1' },
                          { id: 'line2', status: 'on', label: 'Production Line 2' },
                          { id: 'line3', status: 'error', label: 'Production Line 3' },
                          { id: 'line4', status: 'warning', label: 'Production Line 4' },
                          { id: 'line5', status: 'off', label: 'Production Line 5' },
                        ]}
                        size="md"
                        glow={true}
                        orientation="vertical"
                      />
                    </div>
                    
                    <div className="space-y-6">
                      <h4 className="text-xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                        Size Variants
                      </h4>
                      <div className="space-y-4">
                        <div className="p-4 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                          <p className="text-sm font-medium mb-2">Small Size</p>
                          <IndustrialIndicatorGroup
                            indicators={[
                              { id: 's1', status: 'on', label: 'S1' },
                              { id: 's2', status: 'warning', label: 'S2' },
                              { id: 's3', status: 'error', label: 'S3' },
                            ]}
                            size="sm"
                            orientation="horizontal"
                          />
                        </div>
                        
                        <div className="p-4 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                          <p className="text-sm font-medium mb-2">Large Size</p>
                          <IndustrialIndicatorGroup
                            indicators={[
                              { id: 'l1', status: 'on', label: 'L1' },
                              { id: 'l2', status: 'success', label: 'L2' },
                            ]}
                            size="lg"
                            orientation="horizontal"
                            glow={true}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Hardware Tab */}
          {activeTab === 'hardware' && (
            <section className="space-y-8">
              <div className="text-center">
                <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                  Manufacturing Hardware Details
                </h2>
                <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                  Realistic hardware components including fasteners, connectors, textures, and ventilation
                </p>
              </div>
              
              <div className="space-y-8">
                {/* Industrial Bolts */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Industrial Fasteners
                  </h3>
                  <div className="p-8 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
                      <div>
                        <PhillipsHeadBolt size={48} />
                        <p className="text-sm mt-3 font-medium">Phillips Head</p>
                        <p className="text-xs text-gray-500">Cross-head screw</p>
                      </div>
                      <div>
                        <FlatheadBolt size={48} />
                        <p className="text-sm mt-3 font-medium">Flathead</p>
                        <p className="text-xs text-gray-500">Slotted screw</p>
                      </div>
                      <div>
                        <TorxHeadBolt size={48} />
                        <p className="text-sm mt-3 font-medium">Torx Head</p>
                        <p className="text-xs text-gray-500">Star-shaped drive</p>
                      </div>
                      <div>
                        <HexHeadBolt size={48} />
                        <p className="text-sm mt-3 font-medium">Hex Head</p>
                        <p className="text-xs text-gray-500">Allen key drive</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Connector Ports */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Connector Ports
                  </h3>
                  <div className="p-8 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
                      <div>
                        <ConnectorPort type="ethernet" size="lg" />
                        <p className="text-sm mt-3 font-medium">Ethernet</p>
                        <p className="text-xs text-gray-500">RJ45 Network</p>
                      </div>
                      <div>
                        <ConnectorPort type="usb" size="lg" />
                        <p className="text-sm mt-3 font-medium">USB</p>
                        <p className="text-xs text-gray-500">Universal Serial Bus</p>
                      </div>
                      <div>
                        <ConnectorPort type="power" size="lg" />
                        <p className="text-sm mt-3 font-medium">Power</p>
                        <p className="text-xs text-gray-500">DC Power Input</p>
                      </div>
                      <div>
                        <ConnectorPort type="data" size="lg" />
                        <p className="text-sm mt-3 font-medium">Data</p>
                        <p className="text-xs text-gray-500">Serial Data Port</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Surface Textures */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Industrial Surface Textures
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="relative h-40 rounded-xl overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised') }}>
                      <SurfaceTexture pattern="brushed" intensity={0.4} />
                      <div className="absolute bottom-4 left-4">
                        <p className="text-sm font-medium">Brushed Metal</p>
                        <p className="text-xs text-gray-500">Directional finish</p>
                      </div>
                    </div>
                    
                    <div className="relative h-40 rounded-xl overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised') }}>
                      <SurfaceTexture pattern="diamond-plate" intensity={0.5} />
                      <div className="absolute bottom-4 left-4">
                        <p className="text-sm font-medium">Diamond Plate</p>
                        <p className="text-xs text-gray-500">Anti-slip surface</p>
                      </div>
                    </div>
                    
                    <div className="relative h-40 rounded-xl overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised') }}>
                      <SurfaceTexture pattern="perforated" intensity={0.6} />
                      <div className="absolute bottom-4 left-4">
                        <p className="text-sm font-medium">Perforated</p>
                        <p className="text-xs text-gray-500">Ventilation holes</p>
                      </div>
                    </div>
                    
                    <div className="relative h-40 rounded-xl overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised') }}>
                      <SurfaceTexture pattern="carbon-fiber" intensity={0.8} />
                      <div className="absolute bottom-4 left-4">
                        <p className="text-sm font-medium text-white">Carbon Fiber</p>
                        <p className="text-xs text-gray-300">Lightweight composite</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Micro-Texture Finish */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Premium Micro-Texture Finish
                  </h3>
                  <p className="text-gray-600">
                    Subtle noise patterns that simulate the pebble finish found on high-end electronics like Google Home or Apple power cables.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <div className="relative h-32 rounded-xl overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised'), ...NeumorphicUtils.getMicroTexture('subtle') }}>
                      <div className="absolute bottom-4 left-4">
                        <p className="text-sm font-medium">Subtle</p>
                        <p className="text-xs text-gray-600">Minimal texture</p>
                      </div>
                    </div>
                    
                    <div className="relative h-32 rounded-xl overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised'), ...NeumorphicUtils.getMicroTexture('normal') }}>
                      <div className="absolute bottom-4 left-4">
                        <p className="text-sm font-medium">Normal</p>
                        <p className="text-xs text-gray-600">Standard pebble finish</p>
                      </div>
                    </div>
                    
                    <div className="relative h-32 rounded-xl overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised'), ...NeumorphicUtils.getMicroTexture('fine') }}>
                      <div className="absolute bottom-4 left-4">
                        <p className="text-sm font-medium">Fine</p>
                        <p className="text-xs text-gray-600">High-detail texture</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-6 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                    <h4 className="text-lg font-medium mb-3">Implementation</h4>
                    <p className="text-sm text-gray-600 mb-3">
                      The micro-texture is applied using SVG noise filters at very low opacity (1.5-2.5%) to create tactile friction without visual distraction.
                    </p>
                    <div className="bg-gray-100 p-3 rounded text-xs font-mono">
                      <code>NeumorphicUtils.getMicroTexture('normal')</code>
                    </div>
                  </div>
                </div>

                {/* Ventilation Systems */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Ventilation & Cooling
                  </h3>
                  <div className="space-y-6">
                    <div className="p-8 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised') }}>
                      <div className="mb-4">
                        <h4 className="text-lg font-medium mb-2">Standard Density Vent Grille</h4>
                        <p className="text-sm text-gray-600">Optimal airflow for standard cooling requirements</p>
                      </div>
                      <VentGrille density="normal" style={{ height: '32px' }} />
                    </div>
                    
                    <div className="p-8 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised') }}>
                      <div className="mb-4">
                        <h4 className="text-lg font-medium mb-2">High Density Vent Grille</h4>
                        <p className="text-sm text-gray-600">Enhanced airflow for high-performance cooling</p>
                      </div>
                      <VentGrille density="dense" style={{ height: '32px' }} />
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Foundation Tab */}
          {activeTab === 'foundation' && (
            <section className="space-y-8">
              <div className="text-center">
                <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                  Design Foundation
                </h2>
                <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                  Core design tokens, color palette, shadows, and typography system
                </p>
              </div>
              
              <div className="space-y-8">
                {/* Color Palette */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Color Palette
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-6">
                    {Object.entries(industrialTokens.colors.surface).map(([name, color]) => (
                      <div key={name} className="text-center">
                        <div 
                          className="w-20 h-20 rounded-xl mx-auto mb-3"
                          style={{ 
                            backgroundColor: color,
                            ...NeumorphicUtils.getPremiumShadowStyle('normal', 'raised')
                          }}
                        />
                        <p className="text-sm font-medium capitalize">{name}</p>
                        <p className="text-xs text-gray-500 font-mono">{color}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Shadow Variants */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Neumorphic Shadow System
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {(['subtle', 'normal', 'deep'] as const).map((variant) => (
                      <div key={variant} className="space-y-6">
                        <h4 className="text-xl font-medium capitalize text-center">{variant} Shadows</h4>
                        
                        <div className="space-y-4">
                          <div className="text-center">
                            <div 
                              className="w-24 h-24 rounded-xl mx-auto flex items-center justify-center text-sm font-medium"
                              style={{
                                backgroundColor: industrialTokens.colors.surface.primary,
                                ...NeumorphicUtils.getPremiumShadowStyle(variant, 'raised')
                              }}
                            >
                              Raised
                            </div>
                            <p className="text-xs text-gray-500 mt-2">Elevated surface</p>
                          </div>
                          
                          <div className="text-center">
                            <div 
                              className="w-24 h-24 rounded-xl mx-auto flex items-center justify-center text-sm font-medium"
                              style={{
                                backgroundColor: industrialTokens.colors.surface.primary,
                                ...NeumorphicUtils.getPremiumShadowStyle(variant, 'recessed')
                              }}
                            >
                              Recessed
                            </div>
                            <p className="text-xs text-gray-500 mt-2">Inset surface</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Design Principles */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-medium" style={{ color: industrialTokens.colors.text.primary }}>
                    Design Principles
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="p-6 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                      <h4 className="text-lg font-semibold mb-4">Spacing System</h4>
                      <div className="space-y-3">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-blue-500 rounded"></div>
                          <span className="text-sm">8px base unit (0.5rem)</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-4 h-4 bg-blue-500 rounded"></div>
                          <span className="text-sm">16px standard spacing (1rem)</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-6 h-6 bg-blue-500 rounded"></div>
                          <span className="text-sm">24px section spacing (1.5rem)</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-blue-500 rounded"></div>
                          <span className="text-sm">32px large spacing (2rem)</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-6 rounded-xl" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getPremiumShadowStyle('subtle', 'recessed') }}>
                      <h4 className="text-lg font-semibold mb-4">Accessibility</h4>
                      <div className="space-y-3">
                        <div className="flex items-center gap-3">
                          <span className="text-green-500">✓</span>
                          <span className="text-sm">WCAG 2.1 AA compliant</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-green-500">✓</span>
                          <span className="text-sm">Keyboard navigation support</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-green-500">✓</span>
                          <span className="text-sm">Screen reader friendly</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-green-500">✓</span>
                          <span className="text-sm">High contrast ratios</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center py-8 border-t" style={{ borderColor: industrialTokens.colors.shadows.dark + '20' }}>
          <div className="space-y-4">
            <p style={{ color: industrialTokens.colors.text.muted }}>
              Industrial Design System • Professional Skeuomorphic Components • Built with React & TypeScript
            </p>
            <div className="flex justify-center gap-4 text-sm" style={{ color: industrialTokens.colors.text.muted }}>
              <span>Version 1.0</span>
              <span>•</span>
              <span>{tabs.length} Component Categories</span>
              <span>•</span>
              <span>WCAG 2.1 AA Compliant</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default IndustrialDemo;
