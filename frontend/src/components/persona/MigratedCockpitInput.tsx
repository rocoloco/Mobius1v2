/**
 * Migrated Cockpit Input - Uses Polished Industrial Design System
 * 
 * This component replaces the original CockpitInput with the polished industrial design system
 * while maintaining backward compatibility with the existing API.
 */

import React, { useState } from 'react';
import { Cpu, Send } from 'lucide-react';
import { PolishedIndustrialCard } from '../../design-system/components/PolishedIndustrialCard';
import { PolishedIndustrialInput } from '../../design-system/components/PolishedIndustrialInput';
import { PolishedIndustrialButton } from '../../design-system/components/PolishedIndustrialButton';

interface MigratedCockpitInputProps {
  onGenerate: (prompt: string) => void;
  isGenerating: boolean;
  initialValue?: string;
}

/**
 * The "Cockpit Control Deck" - FOR THE EFFICIENCY OPERATOR
 * Floating prompt bar that feels like a command line.
 * Minimal controls, maximum focus.
 */
export const MigratedCockpitInput: React.FC<MigratedCockpitInputProps> = ({
  onGenerate,
  isGenerating,
  initialValue = '',
}) => {
  const [prompt, setPrompt] = useState(initialValue);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !isGenerating) {
      onGenerate(prompt.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto px-4">
      <PolishedIndustrialCard
        variant="elevated"
        size="sm"
        neumorphic={true}
        manufacturing={{
          bolts: false,
          texture: 'smooth'
        }}
        className="backdrop-blur-xl"
        style={{
          background: 'linear-gradient(135deg, rgba(240, 243, 247, 0.98) 0%, rgba(224, 229, 236, 0.95) 100%)',
          borderRadius: '1rem',
          border: '1px solid rgba(59, 130, 246, 0.12)',
          boxShadow: `
            0 4px 20px rgba(0, 0, 0, 0.08),
            0 0 0 1px rgba(255, 255, 255, 0.8) inset,
            0 0 40px rgba(59, 130, 246, 0.05)
          `
        }}
      >
        <form onSubmit={handleSubmit} className="flex items-center gap-4">
          {/* CPU Icon with accent glow */}
          <div className="text-blue-500/70 flex-shrink-0 transition-colors duration-300 group-hover:text-blue-600">
            <Cpu size={18} />
          </div>

          {/* Input */}
          <div className="flex-1">
            <PolishedIndustrialInput
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe asset..."
              disabled={isGenerating}
              variant="recessed"
              size="md"
              neumorphic={true}
              className=""
              style={{
                paddingTop: '8px',
                paddingBottom: '8px'
              }}
            />
          </div>

          {/* The "Go" Button */}
          <div className="flex-shrink-0">
            <PolishedIndustrialButton
              type="submit"
              variant="primary"
              size="md"
              disabled={isGenerating || !prompt.trim()}
              loading={isGenerating}
              rightIcon={<Send size={14} strokeWidth={3} />}
              neumorphic={true}
              industrial={true}
            >
              {isGenerating ? 'GENERATING' : 'GENERATE'}
            </PolishedIndustrialButton>
          </div>
        </form>
      </PolishedIndustrialCard>
    </div>
  );
};

export default MigratedCockpitInput;