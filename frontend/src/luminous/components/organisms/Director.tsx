import { useState, useRef, useEffect, useCallback, memo } from 'react';
import { Send, Zap, AlertCircle, RotateCcw, Plus } from 'lucide-react';
import { ChatMessage } from '../molecules/ChatMessage';
import { BrandSelectorButton } from '../molecules/BrandSelectorButton';
import { BrandSelectorModal } from './BrandSelectorModal';
import { GradientText } from '../atoms/GradientText';
import { GlassPanel } from '../atoms/GlassPanel';
import { luminousTokens } from '../../tokens';
import { useDebouncedCallback } from '../../../hooks/useDebounce';

interface BrandGraphSummary {
  name: string;
  ruleCount: number;
  colorCount: number;
  archetype?: string;
  logoUrl?: string;
}

interface DirectorProps {
  sessionId: string;
  onSubmit: (prompt: string) => void;
  isGenerating: boolean;
  messages?: Array<{
    role: 'user' | 'system' | 'error';
    content: string;
    timestamp: Date;
  }>;
  error?: Error | null;
  onRetry?: () => void;
  onClearError?: () => void;
  /** Brand Graph summary for context indicator */
  brandGraph?: BrandGraphSummary | null;
  /** Callback when Brand Graph indicator is clicked */
  onBrandGraphClick?: () => void;
  /** Whether there's an existing image (enables "new session" button) */
  hasExistingImage?: boolean;
  /** Callback to start a new session */
  onNewSession?: () => void;
  /** Whether brands are still loading */
  brandsLoading?: boolean;
  /** Brand selection props */
  availableBrands?: Array<{
    id: string;
    name: string;
    colorCount?: number;
    ruleCount?: number;
    archetype?: string;
  }>;
  selectedBrandId?: string | null;
  shouldShowBrandSelector?: boolean;
  onSelectBrand?: (brandId: string) => void;
}

interface QuickAction {
  id: string;
  label: string;
  prompt: string;
}

const QUICK_ACTIONS: QuickAction[] = [
  {
    id: 'fix-red',
    label: 'Fix Red Violations',
    prompt: 'Please fix all critical violations marked in red',
  },
  {
    id: 'make-witty',
    label: 'Make it Witty',
    prompt: 'Make the design more witty and playful while maintaining brand guidelines',
  },
];

const MAX_CHARACTERS = 1000;

/**
 * Director - Multi-turn chat interface for AI prompt interaction
 * 
 * Wrapped with React.memo for performance optimization.
 * 
 * Provides a conversational interface for iteratively refining generated
 * brand assets through natural language. Features:
 * - Scrollable chat history with threaded messages
 * - Quick Action chips for common prompts
 * - Floating input field with character counter
 * - Real-time generation status indicator
 * - Debounced input handling for performance
 * 
 * @param sessionId - Current session identifier
 * @param onSubmit - Callback when user submits a prompt
 * @param isGenerating - Whether AI is currently processing
 * @param messages - Chat message history (optional)
 * @param brandGraph - Brand Graph summary for context indicator
 * @param onBrandGraphClick - Callback when Brand Graph indicator is clicked
 */
export const Director = memo(function Director({
  sessionId: _sessionId,
  onSubmit,
  isGenerating,
  messages = [],
  error = null,
  onRetry,
  onClearError,
  brandGraph = null,
  onBrandGraphClick,
  hasExistingImage = false,
  onNewSession,
  brandsLoading = false,
  availableBrands = [],
  selectedBrandId = null,
  shouldShowBrandSelector = false,
  onSelectBrand,
}: DirectorProps) {
  // sessionId available as _sessionId for future use
  const [inputValue, setInputValue] = useState('');
  const [showBrandSelector, setShowBrandSelector] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive - scroll within container only
  useEffect(() => {
    if (chatContainerRef.current) {
      // Scroll the container to the bottom, not the entire page
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Debounced input change handler for performance (300ms delay)
  // Can be used for auto-save drafts, analytics, or other side effects
  const debouncedSetInputValue = useDebouncedCallback((_value: string) => {
    // Placeholder for future functionality like auto-save drafts or analytics
    // The debounced value is available here for processing
  }, 300);

  // Handle input change with immediate UI update and debounced side effects
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value.length <= MAX_CHARACTERS) {
      setInputValue(value);
      debouncedSetInputValue(value);
    }
  }, [debouncedSetInputValue]);

  const handleSubmit = useCallback((e?: React.FormEvent) => {
    e?.preventDefault();
    
    const trimmedValue = inputValue.trim();
    if (trimmedValue && !isGenerating) {
      // Clear any existing errors when submitting new prompt
      if (error && onClearError) {
        onClearError();
      }
      
      onSubmit(trimmedValue);
      setInputValue('');
      
      // Keep fixed height - no need to reset since we're not auto-resizing
    }
  }, [inputValue, isGenerating, error, onClearError, onSubmit]);

  const handleRetry = useCallback(() => {
    if (onRetry) {
      // Clear error state
      if (onClearError) {
        onClearError();
      }
      onRetry();
    }
  }, [onRetry, onClearError]);

  const handleQuickAction = useCallback((action: QuickAction) => {
    setInputValue(action.prompt);
  }, []);

  // Brand selector handlers
  const handleBrandSelectorClick = useCallback(() => {
    if (onBrandGraphClick && brandGraph) {
      // If brand is selected, show brand details
      onBrandGraphClick();
    } else {
      // If no brand selected or multiple brands, show selector
      setShowBrandSelector(true);
    }
  }, [onBrandGraphClick, brandGraph]);

  const handleBrandSelect = useCallback((brandId: string) => {
    onSelectBrand?.(brandId);
    setShowBrandSelector(false);
  }, [onSelectBrand]);

  const handleCloseBrandSelector = useCallback(() => {
    setShowBrandSelector(false);
  }, []);
  
  // Memoized keyboard handler
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  const characterCount = inputValue.length;
  const isNearLimit = characterCount >= 900;
  const isAtLimit = characterCount >= MAX_CHARACTERS;

  return (
    <>
    <GlassPanel
      className="h-full overflow-hidden"
      spotlight={true}
      shimmer={false}
      data-testid="director"
    >
      <div className="h-full flex flex-col overflow-hidden" style={{ minHeight: 0 }}>
      {/* Header with Brand Selector and New Session Button */}
      {(brandGraph || hasExistingImage || brandsLoading || shouldShowBrandSelector || availableBrands.length > 0) && (
        <div className="flex-shrink-0 flex items-center border-b border-white/10" style={{ padding: '12px 20px' }}>
          {/* Brand Selector Button */}
          <BrandSelectorButton
            brandGraph={brandGraph}
            isGenerating={isGenerating}
            onClick={handleBrandSelectorClick}
            showSelectPrompt={shouldShowBrandSelector}
            brandsLoading={brandsLoading}
          />
          
          {/* New Session Button - only show when there's an existing image */}
          {hasExistingImage && onNewSession && (
            <button
              onClick={onNewSession}
              disabled={isGenerating}
              className="flex-shrink-0 w-8 h-8 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 hover:border-purple-500/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-purple-500 ml-2 group relative"
              data-testid="new-session-button"
              aria-label="Start new session"
              title="Start new session"
            >
              <Plus 
                size={16} 
                style={{ color: luminousTokens.colors.text.body }}
                className="group-hover:text-purple-400 transition-colors"
              />
              {/* Tooltip */}
              <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 text-xs rounded bg-gray-900 text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                Start new session
              </span>
            </button>
          )}
        </div>
      )}

      {/* Chat History - Scrollable */}
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto"
        style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px', minHeight: 0 }}
      >
        {messages.length === 0 && !error ? (
          <div className="flex items-center justify-center h-full">
            <p
              className="text-center text-sm"
              style={{ color: luminousTokens.colors.text.muted }}
            >
              Start a conversation to generate brand assets
            </p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage
                key={`${message.timestamp.getTime()}-${index}`}
                role={message.role}
                content={message.content}
                timestamp={message.timestamp}
              />
            ))}
            
            <div ref={chatEndRef} />
          </>
        )}
        
        {/* Error Display - Always show if error exists */}
        {error && (
          <div
            style={{ padding: '16px', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.3)', backgroundColor: 'rgba(239, 68, 68, 0.1)' }}
            data-testid="error-message"
          >
            <div className="flex items-start gap-3">
              <AlertCircle 
                className="w-5 h-5 mt-0.5 flex-shrink-0"
                style={{ color: luminousTokens.colors.compliance.critical }}
              />
              <div className="flex-1">
                <div
                  className="font-semibold text-sm mb-1"
                  style={{ color: luminousTokens.colors.compliance.critical }}
                >
                  Generation Failed
                </div>
                <p
                  className="text-sm mb-3"
                  style={{ color: luminousTokens.colors.text.body }}
                >
                  {error.message || 'An unexpected error occurred. Please try again.'}
                </p>
                {onRetry && (
                  <button
                    onClick={handleRetry}
                    className="px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 hover:border-red-500/50 transition-all duration-300 flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-red-500"
                    data-testid="retry-button"
                    aria-label="Retry generation"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span
                      className="text-sm font-medium"
                      style={{ color: luminousTokens.colors.text.high }}
                    >
                      Retry
                    </span>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Status Indicator */}
      {isGenerating && (
        <div
          style={{ 
            padding: '8px 24px', 
            borderTop: '1px solid rgba(255, 255, 255, 0.1)' 
          }}
          data-testid="generating-status"
        >
          <GradientText animate>
            Mobius - Thinking...
          </GradientText>
        </div>
      )}

      {/* Quick Actions */}
      <div style={{ padding: '12px 24px', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <div className="flex gap-2 flex-wrap">
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action.id}
              onClick={() => handleQuickAction(action)}
              disabled={isGenerating}
              className="px-3 py-2.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 hover:border-purple-500/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 focus:outline-none focus:ring-2 focus:ring-purple-500"
              style={{ minHeight: '44px' }}
              data-testid={`quick-action-${action.id}`}
            >
              <Zap className="w-3.5 h-3.5" style={{ color: luminousTokens.colors.accent.purple }} />
              <span
                className="text-xs font-medium"
                style={{ color: luminousTokens.colors.text.body }}
              >
                {action.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Field - Fixed height container */}
      <form onSubmit={handleSubmit} className="flex-shrink-0" style={{ padding: '16px 24px 20px' }}>
        <div className="relative" style={{ height: '44px' }}>
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Describe the asset..."
            disabled={isGenerating}
            className="w-full h-full bg-white/5 border border-white/10 rounded-2xl focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            style={{
              color: luminousTokens.colors.text.high,
              backdropFilter: luminousTokens.effects.backdropBlur,
              paddingLeft: '16px',
              paddingRight: '110px',
            }}
            data-testid="prompt-input"
          />

          {/* Character Counter - compact */}
          <div className="absolute top-1/2 -translate-y-1/2 right-14 flex items-center">
            <span
              className={`text-[9px] font-mono transition-colors duration-300 ${
                isAtLimit
                  ? 'text-red-400'
                  : isNearLimit
                  ? 'text-yellow-400'
                  : ''
              }`}
              style={{
                color: isAtLimit || isNearLimit ? undefined : luminousTokens.colors.text.muted,
              }}
              data-testid="character-counter"
            >
              {characterCount}/{MAX_CHARACTERS}
            </span>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!inputValue.trim() || isGenerating}
            className="absolute top-1/2 -translate-y-1/2 right-2 w-10 h-10 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{
              boxShadow: !inputValue.trim() || isGenerating ? 'none' : luminousTokens.effects.glow,
              minWidth: '44px',
              minHeight: '44px',
            }}
            aria-label="Send message"
            data-testid="submit-button"
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </div>
      </form>
      </div>
    </GlassPanel>

    {/* Brand Selector Modal */}
    <BrandSelectorModal
      isOpen={showBrandSelector}
      onClose={handleCloseBrandSelector}
      brands={availableBrands}
      selectedBrandId={selectedBrandId}
      onSelectBrand={handleBrandSelect}
      loading={brandsLoading}
    />
  </>
  );
});

// Display name for debugging
Director.displayName = 'Director';
