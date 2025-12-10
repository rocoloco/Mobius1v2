/**
 * Industrial Design System Demo
 * 
 * Clean, organized showcase of all industrial components
 */

import React, { useState } from 'react';
import { 
  industrialTokens, 
  NeumorphicUtils,
  IndustrialCard,
  IndustrialButton,
  IndustrialInput,
  IndustrialIndicator,
  IndustrialIndicatorGroup
} from './index';
import { PhillipsHeadBolt, FlatheadBolt, TorxHeadBolt, HexHeadBolt } from './components/IndustrialBolts';
import { EnhancedIndustrialButton } from './components/EnhancedIndustrialButton';
import { VentGrille, ConnectorPort, SurfaceTexture, WarningLabel, SerialPlate } from './components/IndustrialManufacturing';

export const IndustrialDemo: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [cardStatus, setCardStatus] = useState<'active' | 'inactive' | 'error' | 'warning'>('active');

  return (
    <div 
      className="min-h-screen p-8"
      style={{ backgroundColor: industrialTokens.colors.surface.primary }}
    >
      <div className="max-w-7xl mx-auto space-y-16">
        {/* Header */}
        <div className="text-center">
          <h1 
            className="text-5xl font-bold mb-4"
            style={{ color: industrialTokens.colors.text.primary }}
          >
            Industrial Design System
          </h1>
          <p 
            className="text-xl mb-8"
            style={{ color: industrialTokens.colors.text.secondary }}
          >
            Professional skeuomorphic components for industrial interfaces
          </p>
          <div className="flex justify-center gap-4">
            <WarningLabel type="notice" text="DEMO MODE" />
            <SerialPlate model="Design System v1.0" serialNumber="Build: 2024.12.09" />
          </div>
        </div>

        {/* 1. Industrial Cards */}
        <section className="space-y-6">
          <h2 className="text-3xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
            Industrial Control Panels
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
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
          </div>
        </section>

        {/* 2. Enhanced Buttons */}
        <section className="space-y-6">
          <h2 className="text-3xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
            Industrial Control Buttons
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Enhanced Buttons */}
            <div className="space-y-4">
              <h3 className="text-xl font-medium">Enhanced with Physics</h3>
              <div className="p-6 rounded-lg space-y-4" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getShadowStyle('subtle', 'recessed') }}>
                <div className="flex flex-wrap gap-4">
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
              </div>
            </div>

            {/* Standard Buttons */}
            <div className="space-y-4">
              <h3 className="text-xl font-medium">Standard Industrial</h3>
              <div className="p-6 rounded-lg space-y-4" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getShadowStyle('subtle', 'recessed') }}>
                <div className="flex flex-wrap gap-4">
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
              </div>
            </div>
          </div>
        </section>

        {/* 3. Form Controls */}
        <section className="space-y-6">
          <h2 className="text-3xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
            Industrial Form Controls
          </h2>
          
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
        </section>

        {/* 4. Status Indicators */}
        <section className="space-y-6">
          <h2 className="text-3xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
            Industrial Status Indicators
          </h2>
          
          <div className="space-y-8">
            {/* Individual Indicators */}
            <div className="space-y-4">
              <h3 className="text-xl font-medium">Individual Status LEDs</h3>
              <div className="p-6 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getShadowStyle('subtle', 'recessed') }}>
                <div className="flex flex-wrap gap-8">
                  <IndustrialIndicator status="off" size="lg" label="System Offline" />
                  <IndustrialIndicator status="on" size="lg" label="System Online" glow={true} />
                  <IndustrialIndicator status="error" size="lg" label="Critical Error" pulse={true} />
                  <IndustrialIndicator status="warning" size="lg" label="Warning State" />
                  <IndustrialIndicator status="success" size="lg" label="All Systems Go" />
                </div>
              </div>
            </div>

            {/* Indicator Groups */}
            <div className="space-y-4">
              <h3 className="text-xl font-medium">Production Line Status</h3>
              <div className="p-6 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getShadowStyle('subtle', 'recessed') }}>
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
              </div>
            </div>
          </div>
        </section>

        {/* 5. Manufacturing Hardware */}
        <section className="space-y-6">
          <h2 className="text-3xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
            Manufacturing Hardware Details
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Industrial Bolts */}
            <div className="space-y-4">
              <h3 className="text-xl font-medium">Industrial Fasteners</h3>
              <div className="p-6 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getShadowStyle('subtle', 'recessed') }}>
                <div className="grid grid-cols-4 gap-6 text-center">
                  <div>
                    <PhillipsHeadBolt size={32} />
                    <p className="text-sm mt-2 font-medium">Phillips</p>
                  </div>
                  <div>
                    <FlatheadBolt size={32} />
                    <p className="text-sm mt-2 font-medium">Flathead</p>
                  </div>
                  <div>
                    <TorxHeadBolt size={32} />
                    <p className="text-sm mt-2 font-medium">Torx</p>
                  </div>
                  <div>
                    <HexHeadBolt size={32} />
                    <p className="text-sm mt-2 font-medium">Hex</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Connector Ports */}
            <div className="space-y-4">
              <h3 className="text-xl font-medium">Connector Ports</h3>
              <div className="p-6 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.secondary, ...NeumorphicUtils.getShadowStyle('subtle', 'recessed') }}>
                <div className="grid grid-cols-4 gap-6 text-center">
                  <div>
                    <ConnectorPort type="ethernet" size="lg" />
                    <p className="text-sm mt-2 font-medium">Ethernet</p>
                  </div>
                  <div>
                    <ConnectorPort type="usb" size="lg" />
                    <p className="text-sm mt-2 font-medium">USB</p>
                  </div>
                  <div>
                    <ConnectorPort type="power" size="lg" />
                    <p className="text-sm mt-2 font-medium">Power</p>
                  </div>
                  <div>
                    <ConnectorPort type="data" size="lg" />
                    <p className="text-sm mt-2 font-medium">Data</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 6. Surface Textures */}
        <section className="space-y-6">
          <h2 className="text-3xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
            Industrial Surface Textures
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="relative h-32 rounded-lg overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getShadowStyle('normal', 'raised') }}>
              <SurfaceTexture pattern="brushed" intensity={0.4} />
              <div className="absolute bottom-3 left-3 text-sm font-medium">Brushed Metal</div>
            </div>
            
            <div className="relative h-32 rounded-lg overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getShadowStyle('normal', 'raised') }}>
              <SurfaceTexture pattern="diamond-plate" intensity={0.5} />
              <div className="absolute bottom-3 left-3 text-sm font-medium">Diamond Plate</div>
            </div>
            
            <div className="relative h-32 rounded-lg overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getShadowStyle('normal', 'raised') }}>
              <SurfaceTexture pattern="perforated" intensity={0.6} />
              <div className="absolute bottom-3 left-3 text-sm font-medium">Perforated</div>
            </div>
            
            <div className="relative h-32 rounded-lg overflow-hidden" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getShadowStyle('normal', 'raised') }}>
              <SurfaceTexture pattern="carbon-fiber" intensity={0.8} />
              <div className="absolute bottom-3 left-3 text-sm font-medium text-white">Carbon Fiber</div>
            </div>
          </div>
        </section>

        {/* 7. Ventilation Systems */}
        <section className="space-y-6">
          <h2 className="text-3xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
            Ventilation & Cooling
          </h2>
          
          <div className="space-y-4">
            <div className="p-6 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getShadowStyle('normal', 'raised') }}>
              <div className="mb-3 text-lg font-medium">Standard Density Vent Grille</div>
              <VentGrille density="normal" style={{ height: '24px' }} />
            </div>
            
            <div className="p-6 rounded-lg" style={{ backgroundColor: industrialTokens.colors.surface.primary, ...NeumorphicUtils.getShadowStyle('normal', 'raised') }}>
              <div className="mb-3 text-lg font-medium">High Density Vent Grille</div>
              <VentGrille density="dense" style={{ height: '24px' }} />
            </div>
          </div>
        </section>

        {/* 8. Design Foundation */}
        <section className="space-y-6">
          <h2 className="text-3xl font-semibold" style={{ color: industrialTokens.colors.text.primary }}>
            Design Foundation
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Color Palette */}
            <div className="space-y-4">
              <h3 className="text-xl font-medium">Color Palette</h3>
              <div className="grid grid-cols-3 gap-4">
                {Object.entries(industrialTokens.colors.surface).map(([name, color]) => (
                  <div key={name} className="text-center">
                    <div 
                      className="w-16 h-16 rounded-lg mx-auto mb-2"
                      style={{ 
                        backgroundColor: color,
                        ...NeumorphicUtils.getShadowStyle('normal', 'raised')
                      }}
                    />
                    <p className="text-sm font-medium capitalize">{name}</p>
                    <p className="text-xs text-gray-500">{color}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Shadow Variants */}
            <div className="space-y-4">
              <h3 className="text-xl font-medium">Neumorphic Shadows</h3>
              <div className="grid grid-cols-3 gap-4">
                {(['subtle', 'normal', 'deep'] as const).map((variant) => (
                  <div key={variant} className="text-center space-y-3">
                    <h4 className="text-sm font-medium capitalize">{variant}</h4>
                    
                    <div 
                      className="w-16 h-16 rounded-lg mx-auto flex items-center justify-center text-xs"
                      style={{
                        backgroundColor: industrialTokens.colors.surface.primary,
                        ...NeumorphicUtils.getShadowStyle(variant, 'raised')
                      }}
                    >
                      Raised
                    </div>
                    
                    <div 
                      className="w-16 h-16 rounded-lg mx-auto flex items-center justify-center text-xs"
                      style={{
                        backgroundColor: industrialTokens.colors.surface.primary,
                        ...NeumorphicUtils.getShadowStyle(variant, 'recessed')
                      }}
                    >
                      Recessed
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="text-center py-8 border-t" style={{ borderColor: industrialTokens.colors.shadows.dark + '20' }}>
          <p style={{ color: industrialTokens.colors.text.muted }}>
            Industrial Design System • Professional Skeuomorphic Components • Built with React & TypeScript
          </p>
        </footer>
      </div>
    </div>
  );
};

export default IndustrialDemo;