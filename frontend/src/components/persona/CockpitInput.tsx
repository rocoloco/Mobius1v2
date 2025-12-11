import React, { useState } from 'react';
import { Cpu, Send } from 'lucide-react';
import { MigratedPhysicalButton as PhysicalButton } from '../physical';

interface CockpitInputProps {
  onGenerate: (prompt: string) => void;
  isGenerating: boolean;
  initialValue?: string;
}

/**
 * The "Cockpit Control Deck" - FOR THE EFFICIENCY OPERATOR
 * Floating prompt bar that feels like a command line.
 * Minimal controls, maximum focus.
 */
export const CockpitInput: React.FC<CockpitInputProps> = ({
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
    <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-xl px-4 z-40">
      <form onSubmit={handleSubmit}>
        <div className="bg-surface/90 backdrop-blur-xl shadow-soft rounded-2xl p-2 pl-5 flex items-center gap-4 border border-white/50 ring-1 ring-white/50">
          {/* CPU Icon */}
          <div className="text-ink-muted">
            <Cpu size={18} />
          </div>

          {/* Input */}
          <div className="flex-1 relative">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe asset..."
              disabled={isGenerating}
              className="
                w-full bg-transparent border-none
                focus:ring-0 text-sm font-medium text-ink
                placeholder:text-ink-muted/50 h-10 outline-none
                disabled:opacity-50
              "
            />
          </div>

          {/* Divider */}
          <div className="w-px h-8 bg-ink/10 shadow-[1px_0_0_white]" />

          {/* The "Go" Button */}
          <PhysicalButton
            type="submit"
            variant="primary"
            disabled={isGenerating || !prompt.trim()}
          >
            <span className="flex items-center gap-2">
              {isGenerating ? 'GENERATING...' : 'GENERATE'}
              <Send size={14} strokeWidth={3} />
            </span>
          </PhysicalButton>
        </div>
      </form>
    </div>
  );
};

export default CockpitInput;
