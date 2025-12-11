/**
 * Polished Industrial Design System Demo
 * 
 * Professional showcase using polished components built on Radix UI
 */

import React, { useState } from 'react';
import { industrialTokens } from './tokens';
import { PolishedIndustrialButton } from './components/PolishedIndustrialButton';
import { PolishedIndustrialCard } from './components/PolishedIndustrialCard';
import { PolishedIndustrialInput } from './components/PolishedIndustrialInput';
import {
  PolishedIndustrialTabs,
  PolishedIndustrialTabsList,
  PolishedIndustrialTabsTrigger,
  PolishedIndustrialTabsContent,
} from './components/PolishedIndustrialTabs';
import { 
  HighContrastToggle, 
  SkipLinks, 
  AccessibleStatusIndicator, 
  KeyboardNavigationInfo 
} from './components/AccessibilityEnhancements';
import { 
  PhillipsHeadBolt, 
  FlatheadBolt, 
  TorxHeadBolt, 
  HexHeadBolt 
} from './components/IndustrialBolts';

// Tab configuration
const tabs = [
  { id: 'overview', label: 'Overview', icon: '🏭', description: 'System overview and introduction' },
  { id: 'buttons', label: 'Buttons', icon: '🔘', description: 'Interactive buttons and controls' },
  { id: 'cards', label: 'Cards', icon: '📋', description: 'Information cards and panels' },
  { id: 'forms', label: 'Forms', icon: '📝', description: 'Input fields and form elements' },
  { id: 'components', label: 'Components', icon: '🔧', description: 'Advanced component showcase' }
];

export const PolishedIndustrialDemo: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAsyncAction = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setLoading(false);
  };

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
            className="text-display text-3xl sm:text-5xl mb-4"
            style={{ 
              color: industrialTokens.colors.text.primary,
              fontFamily: industrialTokens.typography.fontFamily.primary,
              fontWeight: industrialTokens.typography.scale.display.fontWeight,
              letterSpacing: industrialTokens.typography.scale.display.letterSpacing
            }}
          >
            Polished Industrial Design System
          </h1>
          <p 
            className="text-body text-lg sm:text-xl mb-6 max-w-3xl mx-auto"
            style={{ 
              color: industrialTokens.colors.text.secondary,
              fontFamily: industrialTokens.typography.fontFamily.secondary,
              lineHeight: industrialTokens.typography.scale.body.lineHeight
            }}
          >
            Professional-grade components built on Radix UI primitives with industrial design tokens. 
            Combining the reliability of proven UI libraries with custom industrial aesthetics.
          </p>
          
          {/* Quick Stats */}
          <div className="flex flex-wrap justify-center gap-6 mb-8">
            <div className="text-center">
              <div 
                className="text-2xl font-bold text-blue-600"
                style={{ fontFamily: industrialTokens.typography.fontFamily.primary }}
              >
                50+
              </div>
              <div 
                className="text-caption text-sm text-gray-600"
                style={{ fontFamily: industrialTokens.typography.fontFamily.secondary }}
              >
                Components
              </div>
            </div>
            <div className="text-center">
              <div 
                className="text-2xl font-bold text-green-600"
                style={{ fontFamily: industrialTokens.typography.fontFamily.primary }}
              >
                WCAG 2.1
              </div>
              <div 
                className="text-caption text-sm text-gray-600"
                style={{ fontFamily: industrialTokens.typography.fontFamily.secondary }}
              >
                AA Compliant
              </div>
            </div>
            <div className="text-center">
              <div 
                className="text-2xl font-bold text-purple-600"
                style={{ fontFamily: industrialTokens.typography.fontFamily.primary }}
              >
                TypeScript
              </div>
              <div 
                className="text-caption text-sm text-gray-600"
                style={{ fontFamily: industrialTokens.typography.fontFamily.secondary }}
              >
                Full Support
              </div>
            </div>
            <div className="text-center">
              <div 
                className="text-2xl font-bold text-orange-600"
                style={{ fontFamily: industrialTokens.typography.fontFamily.primary }}
              >
                Radix UI
              </div>
              <div 
                className="text-caption text-sm text-gray-600"
                style={{ fontFamily: industrialTokens.typography.fontFamily.secondary }}
              >
                Foundation
              </div>
            </div>
          </div>
        </div>

        {/* Main Tabs Navigation */}
        <nav id="navigation" aria-label="Component categories">
          <PolishedIndustrialTabs value={activeTab} onValueChange={setActiveTab}>
            <PolishedIndustrialTabsList className="grid w-full grid-cols-2 lg:grid-cols-5 mb-8">
              {tabs.map((tab) => (
                <PolishedIndustrialTabsTrigger
                  key={tab.id}
                  value={tab.id}
                  icon={<span role="img" aria-label={tab.label}>{tab.icon}</span>}
                >
                  <span className="hidden sm:inline">{tab.label}</span>
                </PolishedIndustrialTabsTrigger>
              ))}
            </PolishedIndustrialTabsList>

            {/* Tab Content */}
            <div className="space-y-8">
              {/* Overview Tab */}
              <PolishedIndustrialTabsContent value="overview">
                <div className="space-y-8">
                  <div className="text-center space-y-6">
                    <h2 
                      className="text-heading text-3xl"
                      style={{ 
                        color: industrialTokens.colors.text.primary,
                        fontFamily: industrialTokens.typography.fontFamily.primary,
                        fontWeight: industrialTokens.typography.scale.heading.fontWeight,
                        letterSpacing: industrialTokens.typography.scale.heading.letterSpacing
                      }}
                    >
                      Welcome to the Future of Industrial UI
                    </h2>
                    <p 
                      className="text-body text-lg max-w-4xl mx-auto leading-relaxed"
                      style={{ 
                        color: industrialTokens.colors.text.secondary,
                        fontFamily: industrialTokens.typography.fontFamily.secondary,
                        lineHeight: industrialTokens.typography.scale.body.lineHeight
                      }}
                    >
                      This design system combines the battle-tested reliability of Radix UI primitives with custom industrial 
                      design tokens. Every component is built for accessibility, performance, and professional aesthetics.
                    </p>
                  </div>

                  {/* Typography Showcase */}
                  <PolishedIndustrialCard title="Typography Hierarchy" subtitle="Space Grotesk + IBM Plex Sans" size="lg">
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-4">
                          <h4 className="text-label" style={{ fontFamily: industrialTokens.typography.fontFamily.secondary }}>
                            Primary Font: Space Grotesk
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <div 
                                className="text-display text-2xl"
                                style={{ fontFamily: industrialTokens.typography.fontFamily.primary }}
                              >
                                Display Text
                              </div>
                              <div className="text-caption text-gray-500">Headers, titles, emphasis</div>
                            </div>
                            <div>
                              <div 
                                className="text-heading text-xl"
                                style={{ fontFamily: industrialTokens.typography.fontFamily.primary }}
                              >
                                Heading Text
                              </div>
                              <div className="text-caption text-gray-500">Section headers, navigation</div>
                            </div>
                            <div>
                              <div 
                                className="text-subheading text-lg"
                                style={{ fontFamily: industrialTokens.typography.fontFamily.primary }}
                              >
                                Subheading Text
                              </div>
                              <div className="text-caption text-gray-500">Card titles, labels</div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="space-y-4">
                          <h4 className="text-label" style={{ fontFamily: industrialTokens.typography.fontFamily.secondary }}>
                            Secondary Font: IBM Plex Sans
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <div 
                                className="text-body"
                                style={{ fontFamily: industrialTokens.typography.fontFamily.secondary }}
                              >
                                Body text for descriptions, content, and general reading. Optimized for readability and extended reading sessions.
                              </div>
                              <div className="text-caption text-gray-500">Paragraphs, descriptions</div>
                            </div>
                            <div>
                              <div 
                                className="text-caption"
                                style={{ fontFamily: industrialTokens.typography.fontFamily.secondary }}
                              >
                                Caption text for metadata, timestamps, and secondary information.
                              </div>
                              <div className="text-caption text-gray-500">Metadata, fine print</div>
                            </div>
                            <div>
                              <div 
                                className="text-code text-sm bg-gray-100 px-2 py-1 rounded"
                                style={{ fontFamily: industrialTokens.typography.fontFamily.mono }}
                              >
                                const code = "JetBrains Mono";
                              </div>
                              <div className="text-caption text-gray-500">Code, data, technical content</div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="border-t border-gray-200 pt-4">
                        <p className="text-body text-sm text-gray-600" style={{ fontFamily: industrialTokens.typography.fontFamily.secondary }}>
                          <strong style={{ fontFamily: industrialTokens.typography.fontFamily.primary }}>Font Pairing Strategy:</strong> Space Grotesk provides geometric precision for UI elements and headers, 
                          while IBM Plex Sans offers superior readability for body text and extended reading. Both fonts share 
                          technical heritage and industrial aesthetics.
                        </p>
                      </div>
                    </div>
                  </PolishedIndustrialCard>

                  {/* Feature Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <PolishedIndustrialCard
                      variant="elevated"
                      title="Radix UI Foundation"
                      subtitle="Built on proven primitives"
                      manufacturing={{ bolts: true }}
                    >
                      <p className="text-sm text-gray-600 mb-4">
                        Leverages Radix UI's accessibility-first components as a foundation, 
                        ensuring keyboard navigation, screen reader support, and ARIA compliance.
                      </p>
                      <div className="flex gap-2">
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">Accessible</span>
                        <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Tested</span>
                      </div>
                    </PolishedIndustrialCard>

                    <PolishedIndustrialCard
                      variant="elevated"
                      title="Industrial Aesthetics"
                      subtitle="Neumorphic design language"
                      manufacturing={{ texture: 'brushed' }}
                      status="active"
                    >
                      <p className="text-sm text-gray-600 mb-4">
                        Custom design tokens create a cohesive industrial look with realistic 
                        shadows, textures, and manufacturing details.
                      </p>
                      <div className="flex gap-2">
                        <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">Neumorphic</span>
                        <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">Realistic</span>
                      </div>
                    </PolishedIndustrialCard>

                    <PolishedIndustrialCard
                      variant="elevated"
                      title="Developer Experience"
                      subtitle="TypeScript & modern tooling"
                      manufacturing={{ bolts: true, texture: 'diamond-plate' }}
                    >
                      <p className="text-sm text-gray-600 mb-4">
                        Full TypeScript support, comprehensive documentation, and modern 
                        development tools for the best developer experience.
                      </p>
                      <div className="flex gap-2">
                        <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs rounded-full">TypeScript</span>
                        <span className="px-2 py-1 bg-teal-100 text-teal-700 text-xs rounded-full">Modern</span>
                      </div>
                    </PolishedIndustrialCard>
                  </div>

                  {/* Quick Actions */}
                  <div className="text-center space-y-4">
                    <h3 className="text-xl font-semibold">Get Started</h3>
                    <div className="flex flex-wrap justify-center gap-4">
                      <PolishedIndustrialButton
                        variant="primary"
                        size="lg"
                        onClick={() => setActiveTab('buttons')}
                        leftIcon={<span>🚀</span>}
                      >
                        Explore Components
                      </PolishedIndustrialButton>
                      <PolishedIndustrialButton
                        variant="outline"
                        size="lg"
                        leftIcon={<span>📖</span>}
                      >
                        View Documentation
                      </PolishedIndustrialButton>
                    </div>
                  </div>
                </div>
              </PolishedIndustrialTabsContent>

              {/* Buttons Tab */}
              <PolishedIndustrialTabsContent value="buttons">
                <div className="space-y-8">
                  <div className="text-center">
                    <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                      Professional Button Components
                    </h2>
                    <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                      Polished buttons with loading states, icons, and industrial styling
                    </p>
                  </div>

                  {/* Button Variants */}
                  <PolishedIndustrialCard title="Button Variants" size="lg">
                    <div className="space-y-6">
                      {/* Primary Action Buttons */}
                      <div>
                        <h4 className="text-sm font-medium mb-3 text-gray-700">Primary Actions</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                          <PolishedIndustrialButton variant="primary" size="md">
                            Primary
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="secondary" size="md">
                            Secondary
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="industrial" size="md">
                            Industrial
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="emergency" size="md">
                            Emergency
                          </PolishedIndustrialButton>
                        </div>
                      </div>

                      {/* Status Buttons */}
                      <div>
                        <h4 className="text-sm font-medium mb-3 text-gray-700">Status Actions</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                          <PolishedIndustrialButton variant="success" size="md">
                            Success
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="danger" size="md">
                            Danger
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="outline" size="md">
                            Outline
                          </PolishedIndustrialButton>
                        </div>
                      </div>

                      {/* Subtle Buttons */}
                      <div>
                        <h4 className="text-sm font-medium mb-3 text-gray-700">Subtle Actions</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <PolishedIndustrialButton variant="ghost" size="md">
                            Ghost Button
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="ghost" size="md" disabled>
                            Disabled Ghost
                          </PolishedIndustrialButton>
                        </div>
                      </div>
                    </div>
                  </PolishedIndustrialCard>

                  {/* Button Sizes */}
                  <PolishedIndustrialCard title="Button Sizes" size="lg">
                    <div className="flex flex-wrap items-center gap-4">
                      <PolishedIndustrialButton variant="primary" size="sm">
                        Small
                      </PolishedIndustrialButton>
                      <PolishedIndustrialButton variant="primary" size="md">
                        Medium
                      </PolishedIndustrialButton>
                      <PolishedIndustrialButton variant="primary" size="lg">
                        Large
                      </PolishedIndustrialButton>
                      <PolishedIndustrialButton variant="primary" size="xl">
                        Extra Large
                      </PolishedIndustrialButton>
                    </div>
                  </PolishedIndustrialCard>

                  {/* Interactive Features */}
                  <PolishedIndustrialCard title="Interactive Features & Press Physics" size="lg">
                    <div className="space-y-6">
                      {/* Icons and Loading */}
                      <div>
                        <h4 className="text-sm font-medium mb-3 text-gray-700">Icons & Loading States</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                          <PolishedIndustrialButton
                            variant="industrial"
                            leftIcon={<span>⚡</span>}
                          >
                            Power On
                          </PolishedIndustrialButton>
                          
                          <PolishedIndustrialButton
                            variant="secondary"
                            rightIcon={<span>→</span>}
                          >
                            Next Step
                          </PolishedIndustrialButton>
                          
                          <PolishedIndustrialButton
                            variant="primary"
                            loading={loading}
                            onClick={handleAsyncAction}
                          >
                            {loading ? 'Processing...' : 'Start Process'}
                          </PolishedIndustrialButton>
                        </div>
                      </div>

                      {/* Press Physics Demo */}
                      <div>
                        <h4 className="text-sm font-medium mb-3 text-gray-700">Press Physics (Click and Hold)</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                          <PolishedIndustrialButton variant="industrial">
                            Press & Hold
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="emergency">
                            Emergency Stop
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="success">
                            Confirm Action
                          </PolishedIndustrialButton>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                          Notice the realistic press physics when you click and hold these buttons
                        </p>
                      </div>

                      {/* States */}
                      <div>
                        <h4 className="text-sm font-medium mb-3 text-gray-700">Button States</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <PolishedIndustrialButton variant="primary" disabled>
                            Disabled State
                          </PolishedIndustrialButton>
                          
                          <PolishedIndustrialButton
                            variant="danger"
                            leftIcon={<span>🚨</span>}
                            rightIcon={<span>⚠️</span>}
                          >
                            Emergency Stop
                          </PolishedIndustrialButton>
                        </div>
                      </div>
                    </div>
                  </PolishedIndustrialCard>
                </div>
              </PolishedIndustrialTabsContent>

              {/* Cards Tab */}
              <PolishedIndustrialTabsContent value="cards">
                <div className="space-y-8">
                  <div className="text-center">
                    <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                      Industrial Card Components
                    </h2>
                    <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                      Versatile cards with status indicators, manufacturing details, and interactive features
                    </p>
                  </div>

                  {/* Card Variants */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <PolishedIndustrialCard
                      variant="default"
                      title="Default Card"
                      subtitle="Flush with surface"
                    >
                      <p className="text-sm text-gray-600">
                        Minimal depth, sits flush with the background surface. 
                        Used for secondary content and supporting information.
                      </p>
                    </PolishedIndustrialCard>

                    <PolishedIndustrialCard
                      variant="elevated"
                      title="Elevated Card"
                      subtitle="Raised above surface"
                      manufacturing={{ bolts: true }}
                    >
                      <p className="text-sm text-gray-600">
                        Deeper shadows create clear hierarchy. 
                        Used for primary content and important information panels.
                      </p>
                    </PolishedIndustrialCard>

                    <PolishedIndustrialCard
                      variant="interactive"
                      title="Interactive Card"
                      subtitle="Responds to interaction"
                      onClick={() => alert('Interactive card clicked!')}
                    >
                      <p className="text-sm text-gray-600">
                        Subtle hover feedback and cursor changes. 
                        Used for clickable panels and navigation elements.
                      </p>
                    </PolishedIndustrialCard>
                  </div>

                  {/* Industrial Design Principles */}
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold">Industrial Design Principles</h3>
                    <PolishedIndustrialCard title="Depth Hierarchy Through Shadow" size="lg">
                      <div className="space-y-6">
                        <p className="text-sm text-gray-600">
                          Industrial design uses subtle depth variations to create visual hierarchy without decorative elements.
                        </p>
                        
                        {/* Visual Shadow Examples */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                          <div className="space-y-3">
                            <h4 className="font-medium text-center">Default (Subtle)</h4>
                            <PolishedIndustrialCard
                              variant="default"
                              title="Subtle Depth"
                              size="sm"
                            >
                              <p className="text-xs text-gray-600">
                                Minimal shadow depth for secondary content and supporting information.
                              </p>
                            </PolishedIndustrialCard>
                            <p className="text-xs text-gray-500 text-center">
                              Flush with surface, minimal visual weight
                            </p>
                          </div>
                          
                          <div className="space-y-3">
                            <h4 className="font-medium text-center">Elevated (Deep)</h4>
                            <PolishedIndustrialCard
                              variant="elevated"
                              title="Deep Shadows"
                              size="sm"
                              manufacturing={{ bolts: true }}
                            >
                              <p className="text-xs text-gray-600">
                                Pronounced depth for primary content and important panels.
                              </p>
                            </PolishedIndustrialCard>
                            <p className="text-xs text-gray-500 text-center">
                              Raised above surface, high visual priority
                            </p>
                          </div>
                          
                          <div className="space-y-3">
                            <h4 className="font-medium text-center">Interactive (Normal)</h4>
                            <PolishedIndustrialCard
                              variant="interactive"
                              title="Hover Effects"
                              size="sm"
                              onClick={() => {}}
                            >
                              <p className="text-xs text-gray-600">
                                Moderate depth with hover feedback for clickable elements.
                              </p>
                            </PolishedIndustrialCard>
                            <p className="text-xs text-gray-500 text-center">
                              Dynamic depth, responds to interaction
                            </p>
                          </div>
                        </div>
                        
                        {/* Shadow Comparison */}
                        <div className="border-t border-gray-200 pt-4">
                          <h5 className="font-medium mb-3">Shadow Depth Comparison</h5>
                          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
                            <div className="text-center">
                              <div 
                                className="w-16 h-16 mx-auto mb-2 rounded-lg"
                                style={{
                                  backgroundColor: industrialTokens.colors.surface.primary,
                                  boxShadow: industrialTokens.shadows.neumorphic.raised.subtle
                                }}
                              />
                              <p className="font-medium">Subtle</p>
                              <p className="text-gray-500">0.7x depth</p>
                            </div>
                            <div className="text-center">
                              <div 
                                className="w-16 h-16 mx-auto mb-2 rounded-lg"
                                style={{
                                  backgroundColor: industrialTokens.colors.surface.primary,
                                  boxShadow: industrialTokens.shadows.neumorphic.raised.normal
                                }}
                              />
                              <p className="font-medium">Normal</p>
                              <p className="text-gray-500">1.0x depth</p>
                            </div>
                            <div className="text-center">
                              <div 
                                className="w-16 h-16 mx-auto mb-2 rounded-lg"
                                style={{
                                  backgroundColor: industrialTokens.colors.surface.primary,
                                  boxShadow: industrialTokens.shadows.neumorphic.raised.deep
                                }}
                              />
                              <p className="font-medium">Deep</p>
                              <p className="text-gray-500">1.5x depth</p>
                            </div>
                            <div className="text-center">
                              <div 
                                className="w-16 h-16 mx-auto mb-2 rounded-lg"
                                style={{
                                  backgroundColor: industrialTokens.colors.surface.primary,
                                  boxShadow: industrialTokens.shadows.neumorphic.recessed.normal
                                }}
                              />
                              <p className="font-medium">Recessed</p>
                              <p className="text-gray-500">Inset shadows</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </PolishedIndustrialCard>
                  </div>

                  {/* Status Cards */}
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold">Status Display Cards</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <PolishedIndustrialCard
                        variant="status"
                        status="active"
                        title="Active System"
                        subtitle="All systems operational"
                      >
                        <AccessibleStatusIndicator status="on" label="System Status" size="sm" />
                      </PolishedIndustrialCard>

                      <PolishedIndustrialCard
                        variant="status"
                        status="warning"
                        title="Warning State"
                        subtitle="Attention required"
                      >
                        <AccessibleStatusIndicator status="warning" label="System Status" size="sm" />
                      </PolishedIndustrialCard>

                      <PolishedIndustrialCard
                        variant="status"
                        status="error"
                        title="Error State"
                        subtitle="Immediate action needed"
                      >
                        <AccessibleStatusIndicator status="error" label="System Status" size="sm" />
                      </PolishedIndustrialCard>

                      <PolishedIndustrialCard
                        variant="status"
                        status="inactive"
                        title="Inactive System"
                        subtitle="System offline"
                      >
                        <AccessibleStatusIndicator status="off" label="System Status" size="sm" />
                      </PolishedIndustrialCard>
                    </div>
                  </div>

                  {/* Advanced Cards */}
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold">Advanced Features</h3>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <PolishedIndustrialCard
                        variant="elevated"
                        title="Manufacturing Unit A"
                        subtitle="Production Line Control"
                        status="active"
                        manufacturing={{ bolts: true, texture: 'brushed' }}
                        headerAction={
                          <PolishedIndustrialButton variant="ghost" size="sm">
                            Configure
                          </PolishedIndustrialButton>
                        }
                        footer={
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">Last updated: 2 min ago</span>
                            <PolishedIndustrialButton variant="primary" size="sm">
                              View Details
                            </PolishedIndustrialButton>
                          </div>
                        }
                      >
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-sm">Temperature:</span>
                            <span className="text-sm font-medium">72°C</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">Pressure:</span>
                            <span className="text-sm font-medium">145 PSI</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">Output Rate:</span>
                            <span className="text-sm font-medium">98.5%</span>
                          </div>
                        </div>
                      </PolishedIndustrialCard>

                      <PolishedIndustrialCard
                        variant="interactive"
                        title="Quality Control Station"
                        subtitle="Inspection & Testing"
                        status="warning"
                        manufacturing={{ bolts: true }}
                        onClick={() => setActiveTab('forms')}
                      >
                        <div className="space-y-4">
                          <p className="text-sm text-gray-600">
                            Quality control parameters require attention. Click to access the inspection form.
                          </p>
                          <div className="grid grid-cols-2 gap-4 text-center">
                            <div>
                              <div className="text-lg font-bold text-green-600">94.2%</div>
                              <div className="text-xs text-gray-500">Pass Rate</div>
                            </div>
                            <div>
                              <div className="text-lg font-bold text-yellow-600">12</div>
                              <div className="text-xs text-gray-500">Pending</div>
                            </div>
                          </div>
                        </div>
                      </PolishedIndustrialCard>
                    </div>
                  </div>
                </div>
              </PolishedIndustrialTabsContent>

              {/* Forms Tab */}
              <PolishedIndustrialTabsContent value="forms">
                <div className="space-y-8">
                  <div className="text-center">
                    <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                      Industrial Form Controls
                    </h2>
                    <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                      Professional input fields with validation, icons, and accessibility features
                    </p>
                  </div>

                  {/* Input Variants */}
                  <PolishedIndustrialCard title="Input Field Variants" size="lg">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <PolishedIndustrialInput
                        label="Default Input"
                        placeholder="Enter text..."
                        helperText="This is a default input field"
                      />

                      <PolishedIndustrialInput
                        variant="filled"
                        label="Filled Input"
                        placeholder="Enter text..."
                        helperText="Filled variant with background"
                      />

                      <PolishedIndustrialInput
                        label="With Left Icon"
                        placeholder="Search..."
                        leftIcon={<span>🔍</span>}
                        helperText="Input with left icon"
                      />

                      <PolishedIndustrialInput
                        label="With Right Icon"
                        placeholder="Enter password..."
                        type="password"
                        rightIcon={<span>👁️</span>}
                        helperText="Input with right icon"
                      />
                    </div>
                  </PolishedIndustrialCard>

                  {/* Input States */}
                  <PolishedIndustrialCard title="Input States & Validation" size="lg">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <PolishedIndustrialInput
                        label="Success State"
                        placeholder="Valid input..."
                        status="success"
                        helperText="Input validation passed"
                        ledIndicator
                      />

                      <PolishedIndustrialInput
                        label="Warning State"
                        placeholder="Check input..."
                        status="warning"
                        helperText="Please verify this input"
                        ledIndicator
                      />

                      <PolishedIndustrialInput
                        label="Error State"
                        placeholder="Invalid input..."
                        status="error"
                        helperText="This field contains an error"
                        ledIndicator
                      />

                      <PolishedIndustrialInput
                        label="Disabled Input"
                        placeholder="Cannot edit..."
                        disabled
                        helperText="This field is disabled"
                      />
                    </div>
                  </PolishedIndustrialCard>

                  {/* Complete Form Example */}
                  <PolishedIndustrialCard title="Manufacturing Configuration Form" size="lg">
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <PolishedIndustrialInput
                          label="Machine ID"
                          placeholder="Enter machine identifier..."
                          value={inputValue}
                          onChange={(e) => setInputValue(e.target.value)}
                          required
                          leftIcon={<span>🏭</span>}
                          helperText="Unique identifier for the machine"
                        />

                        <PolishedIndustrialInput
                          label="Operating Temperature"
                          placeholder="Temperature in °C..."
                          type="number"
                          status="warning"
                          ledIndicator
                          rightIcon={<span>🌡️</span>}
                          helperText="Current: 85°C (Warning threshold: 80°C)"
                        />
                      </div>

                      <PolishedIndustrialInput
                        label="Process Description"
                        placeholder="Describe the manufacturing process..."
                        helperText="Detailed description of the current process"
                      />

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <PolishedIndustrialInput
                          label="Pressure (PSI)"
                          placeholder="145"
                          type="number"
                          size="sm"
                        />

                        <PolishedIndustrialInput
                          label="Flow Rate (L/min)"
                          placeholder="12.5"
                          type="number"
                          size="sm"
                        />

                        <PolishedIndustrialInput
                          label="Efficiency (%)"
                          placeholder="98.5"
                          type="number"
                          size="sm"
                          status="success"
                          ledIndicator
                        />
                      </div>

                      <div className="flex gap-4 pt-4">
                        <PolishedIndustrialButton 
                          variant="primary" 
                          size="md"
                          leftIcon={<span>💾</span>}
                        >
                          Save Configuration
                        </PolishedIndustrialButton>
                        <PolishedIndustrialButton 
                          variant="secondary" 
                          size="md"
                          leftIcon={<span>🔄</span>}
                        >
                          Reset Form
                        </PolishedIndustrialButton>
                        <PolishedIndustrialButton 
                          variant="outline" 
                          size="md"
                          leftIcon={<span>📋</span>}
                        >
                          Load Template
                        </PolishedIndustrialButton>
                      </div>
                    </div>
                  </PolishedIndustrialCard>
                </div>
              </PolishedIndustrialTabsContent>

              {/* Components Tab */}
              <PolishedIndustrialTabsContent value="components">
                <div className="space-y-8">
                  <div className="text-center">
                    <h2 className="text-3xl font-semibold mb-4" style={{ color: industrialTokens.colors.text.primary }}>
                      Advanced Component Showcase
                    </h2>
                    <p className="text-lg" style={{ color: industrialTokens.colors.text.secondary }}>
                      Complex components demonstrating the full capabilities of the design system
                    </p>
                  </div>

                  {/* Component Comparison */}
                  <PolishedIndustrialCard title="Design System Comparison" size="lg">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-3 px-4">Feature</th>
                            <th className="text-center py-3 px-4">Basic Components</th>
                            <th className="text-center py-3 px-4">Polished Components</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          <tr>
                            <td className="py-3 px-4 font-medium">Accessibility</td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-yellow-600">⚠️ Basic</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-green-600">✅ WCAG 2.1 AA</span>
                            </td>
                          </tr>
                          <tr>
                            <td className="py-3 px-4 font-medium">TypeScript Support</td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-yellow-600">⚠️ Partial</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-green-600">✅ Full</span>
                            </td>
                          </tr>
                          <tr>
                            <td className="py-3 px-4 font-medium">Component Variants</td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-red-600">❌ Limited</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-green-600">✅ Extensive</span>
                            </td>
                          </tr>
                          <tr>
                            <td className="py-3 px-4 font-medium">Loading States</td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-red-600">❌ None</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-green-600">✅ Built-in</span>
                            </td>
                          </tr>
                          <tr>
                            <td className="py-3 px-4 font-medium">Professional Polish</td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-red-600">❌ Basic</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-green-600">✅ Production Ready</span>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </PolishedIndustrialCard>

                  {/* Industrial Hardware Showcase */}
                  <PolishedIndustrialCard title="Industrial Hardware Components" size="lg">
                    <div className="space-y-6">
                      <div>
                        <h4 className="text-lg font-semibold mb-4">Available Bolt Types</h4>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
                          <div className="space-y-3">
                            <div className="flex justify-center">
                              <HexHeadBolt size={32} />
                            </div>
                            <div>
                              <p className="font-medium">Hex Head</p>
                              <p className="text-xs text-gray-500">Allen key drive</p>
                              <span className="inline-block mt-1 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                                Default
                              </span>
                            </div>
                          </div>
                          
                          <div className="space-y-3">
                            <div className="flex justify-center">
                              <PhillipsHeadBolt size={32} />
                            </div>
                            <div>
                              <p className="font-medium">Phillips Head</p>
                              <p className="text-xs text-gray-500">Cross-head screw</p>
                            </div>
                          </div>
                          
                          <div className="space-y-3">
                            <div className="flex justify-center">
                              <TorxHeadBolt size={32} />
                            </div>
                            <div>
                              <p className="font-medium">Torx Head</p>
                              <p className="text-xs text-gray-500">Star-shaped drive</p>
                            </div>
                          </div>
                          
                          <div className="space-y-3">
                            <div className="flex justify-center">
                              <FlatheadBolt size={32} />
                            </div>
                            <div>
                              <p className="font-medium">Flathead</p>
                              <p className="text-xs text-gray-500">Slotted screw</p>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="border-t border-gray-200 pt-6">
                        <h4 className="text-lg font-semibold mb-4">Card Examples with Different Bolt Types</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <PolishedIndustrialCard
                            variant="elevated"
                            title="Hex Bolted Panel"
                            subtitle="Professional grade"
                            manufacturing={{ bolts: true }}
                            size="sm"
                          >
                            <p className="text-sm text-gray-600">
                              Default hex head bolts for industrial applications.
                            </p>
                          </PolishedIndustrialCard>
                          
                          <PolishedIndustrialCard
                            variant="elevated"
                            title="Textured Housing"
                            subtitle="Surface treatment"
                            manufacturing={{ bolts: true, texture: 'perforated' }}
                            size="sm"
                          >
                            <p className="text-sm text-gray-600">
                              Bolts with perforated surface texture for industrial aesthetics.
                            </p>
                          </PolishedIndustrialCard>
                        </div>
                      </div>
                    </div>
                  </PolishedIndustrialCard>

                  {/* Integration Example */}
                  <PolishedIndustrialCard 
                    title="Real-world Integration Example" 
                    subtitle="Manufacturing Dashboard Panel"
                    size="lg"
                    status="active"
                    manufacturing={{ bolts: true, texture: 'brushed' }}
                  >
                    <div className="space-y-6">
                      {/* Dashboard Header */}
                      <div className="flex flex-wrap items-center justify-between gap-4">
                        <div>
                          <h4 className="text-lg font-semibold">Production Line Alpha</h4>
                          <p className="text-sm text-gray-600">Real-time monitoring and control</p>
                        </div>
                        <div className="flex gap-2">
                          <PolishedIndustrialButton variant="success" size="sm">
                            Start Production
                          </PolishedIndustrialButton>
                          <PolishedIndustrialButton variant="danger" size="sm">
                            Emergency Stop
                          </PolishedIndustrialButton>
                        </div>
                      </div>

                      {/* Status Grid */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                          <div className="flex items-center gap-2 mb-2">
                            <AccessibleStatusIndicator status="on" label="Power" size="sm" showText={false} />
                            <span className="font-medium">Power System</span>
                          </div>
                          <div className="text-2xl font-bold text-green-600">Online</div>
                        </div>

                        <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                          <div className="flex items-center gap-2 mb-2">
                            <AccessibleStatusIndicator status="warning" label="Temperature" size="sm" showText={false} />
                            <span className="font-medium">Temperature</span>
                          </div>
                          <div className="text-2xl font-bold text-yellow-600">85°C</div>
                        </div>

                        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                          <div className="flex items-center gap-2 mb-2">
                            <AccessibleStatusIndicator status="success" label="Pressure" size="sm" showText={false} />
                            <span className="font-medium">Pressure</span>
                          </div>
                          <div className="text-2xl font-bold text-blue-600">145 PSI</div>
                        </div>

                        <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                          <div className="flex items-center gap-2 mb-2">
                            <AccessibleStatusIndicator status="success" label="Output" size="sm" showText={false} />
                            <span className="font-medium">Output Rate</span>
                          </div>
                          <div className="text-2xl font-bold text-purple-600">98.5%</div>
                        </div>
                      </div>

                      {/* Control Panel */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="space-y-4">
                          <h5 className="font-semibold">Process Controls</h5>
                          <PolishedIndustrialInput
                            label="Target Temperature"
                            placeholder="80"
                            type="number"
                            rightIcon={<span>°C</span>}
                            size="sm"
                          />
                          <PolishedIndustrialInput
                            label="Flow Rate"
                            placeholder="12.5"
                            type="number"
                            rightIcon={<span>L/min</span>}
                            size="sm"
                          />
                        </div>

                        <div className="space-y-4">
                          <h5 className="font-semibold">Quick Actions</h5>
                          <div className="grid grid-cols-2 gap-2">
                            <PolishedIndustrialButton variant="outline" size="sm">
                              Calibrate
                            </PolishedIndustrialButton>
                            <PolishedIndustrialButton variant="outline" size="sm">
                              Reset
                            </PolishedIndustrialButton>
                            <PolishedIndustrialButton variant="outline" size="sm">
                              Export Data
                            </PolishedIndustrialButton>
                            <PolishedIndustrialButton variant="outline" size="sm">
                              Settings
                            </PolishedIndustrialButton>
                          </div>
                        </div>
                      </div>
                    </div>
                  </PolishedIndustrialCard>
                </div>
              </PolishedIndustrialTabsContent>
            </div>
          </PolishedIndustrialTabs>
        </nav>

        {/* Footer */}
        <footer className="mt-16 text-center py-8 border-t" style={{ borderColor: industrialTokens.colors.shadows.dark + '20' }}>
          <div className="space-y-4">
            <p style={{ color: industrialTokens.colors.text.muted }}>
              Polished Industrial Design System • Built on Radix UI • Professional Grade Components
            </p>
            <div className="flex justify-center gap-4 text-sm" style={{ color: industrialTokens.colors.text.muted }}>
              <span>Version 2.0</span>
              <span>•</span>
              <span>50+ Components</span>
              <span>•</span>
              <span>WCAG 2.1 AA Compliant</span>
              <span>•</span>
              <span>TypeScript Ready</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default PolishedIndustrialDemo;