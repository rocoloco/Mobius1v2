import React from 'react';
import { ViolationItem } from '../ViolationItem';
import { ConstraintCard } from '../ConstraintCard';
import { Linkedin, EyeOff, Mic } from 'lucide-react';
import { GlassPanel } from '../../atoms/GlassPanel';

/**
 * Demo page for ViolationItem and ConstraintCard components
 * 
 * This file demonstrates the visual appearance and behavior of the
 * ViolationItem and ConstraintCard molecular components in isolation.
 */
export function ViolationAndConstraintDemo() {
  const [selectedViolation, setSelectedViolation] = React.useState<string | null>(null);
  
  const violations = [
    {
      id: '1',
      severity: 'critical' as const,
      message: 'Logo margin too small - minimum 20px clearance required',
    },
    {
      id: '2',
      severity: 'warning' as const,
      message: 'Font weight should be 600 or 700 for headings',
    },
    {
      id: '3',
      severity: 'info' as const,
      message: 'Consider using brand accent color for call-to-action',
    },
  ];
  
  return (
    <div className="min-h-screen bg-[#101012] p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-white mb-2">
            ViolationItem & ConstraintCard Demo
          </h1>
          <p className="text-slate-400">
            Molecular components for violations and constraints
          </p>
        </div>
        
        {/* ViolationItem Section */}
        <section>
          <h2 className="text-xl font-semibold text-white mb-4">ViolationItem Component</h2>
          <GlassPanel className="p-6">
            <div className="space-y-2">
              {violations.map(violation => (
                <ViolationItem
                  key={violation.id}
                  violation={violation}
                  onClick={() => {
                    setSelectedViolation(violation.id);
                    console.log('Clicked violation:', violation.id);
                  }}
                />
              ))}
            </div>
            {selectedViolation && (
              <p className="mt-4 text-sm text-slate-400">
                Selected violation: {selectedViolation}
              </p>
            )}
          </GlassPanel>
        </section>
        
        {/* ConstraintCard Section */}
        <section>
          <h2 className="text-xl font-semibold text-white mb-4">ConstraintCard Component</h2>
          <GlassPanel className="p-6">
            <div className="space-y-3">
              {/* Channel Constraint */}
              <ConstraintCard
                type="channel"
                label="LinkedIn Professional"
                icon={<Linkedin className="w-5 h-5" />}
                active={false}
              />
              
              {/* Negative Constraint (Active) */}
              <ConstraintCard
                type="negative"
                label="No Comic Sans"
                icon={<EyeOff className="w-5 h-5" />}
                active={true}
              />
              
              {/* Voice Constraint with Radar Chart */}
              <ConstraintCard
                type="voice"
                label="Brand Voice"
                icon={<Mic className="w-5 h-5" />}
                active={false}
                metadata={{
                  voiceVectors: {
                    formal: 0.8,
                    witty: 0.3,
                    technical: 0.6,
                    urgent: 0.2,
                  },
                }}
              />
              
              {/* Voice Constraint Active */}
              <ConstraintCard
                type="voice"
                label="Active Voice Profile"
                icon={<Mic className="w-5 h-5" />}
                active={true}
                metadata={{
                  voiceVectors: {
                    formal: 0.4,
                    witty: 0.9,
                    technical: 0.5,
                    urgent: 0.7,
                  },
                }}
              />
            </div>
          </GlassPanel>
        </section>
        
        {/* Combined Example */}
        <section>
          <h2 className="text-xl font-semibold text-white mb-4">Combined Layout Example</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Violations Panel */}
            <GlassPanel className="p-4">
              <h3 className="text-sm font-semibold text-white mb-3">Violations</h3>
              <div className="space-y-2">
                {violations.map(violation => (
                  <ViolationItem
                    key={violation.id}
                    violation={violation}
                    onClick={() => setSelectedViolation(violation.id)}
                  />
                ))}
              </div>
            </GlassPanel>
            
            {/* Constraints Panel */}
            <GlassPanel className="p-4">
              <h3 className="text-sm font-semibold text-white mb-3">Active Constraints</h3>
              <div className="space-y-3">
                <ConstraintCard
                  type="channel"
                  label="LinkedIn"
                  icon={<Linkedin className="w-5 h-5" />}
                />
                <ConstraintCard
                  type="voice"
                  label="Professional Tone"
                  icon={<Mic className="w-5 h-5" />}
                  active={true}
                  metadata={{
                    voiceVectors: {
                      formal: 0.9,
                      witty: 0.2,
                      technical: 0.7,
                      urgent: 0.3,
                    },
                  }}
                />
              </div>
            </GlassPanel>
          </div>
        </section>
      </div>
    </div>
  );
}
