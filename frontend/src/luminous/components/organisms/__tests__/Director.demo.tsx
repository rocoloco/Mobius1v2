import { useState } from 'react';
import { Director } from '../Director';

/**
 * Director Demo Page
 * 
 * Interactive demo showcasing the Director chat interface with:
 * - Mock chat history
 * - Working input field
 * - Quick action chips
 * - Generation status indicator
 */
export function DirectorDemo() {
  const [messages, setMessages] = useState([
    {
      role: 'system' as const,
      content: 'Hello! I\'m Mobius. I can help you generate brand-compliant assets. What would you like to create today?',
      timestamp: new Date(Date.now() - 120000),
    },
    {
      role: 'user' as const,
      content: 'Create a LinkedIn post image for our new product launch',
      timestamp: new Date(Date.now() - 90000),
    },
    {
      role: 'system' as const,
      content: 'I\'ve generated a LinkedIn post image featuring your brand colors and typography. The design includes your logo with proper spacing and uses the approved color palette.',
      timestamp: new Date(Date.now() - 60000),
    },
    {
      role: 'user' as const,
      content: 'Can you make the text more prominent and add a call-to-action?',
      timestamp: new Date(Date.now() - 30000),
    },
  ]);
  
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSubmit = (prompt: string) => {
    // Add user message
    setMessages(prev => [...prev, {
      role: 'user' as const,
      content: prompt,
      timestamp: new Date(),
    }]);

    // Simulate generation
    setIsGenerating(true);
    
    setTimeout(() => {
      setMessages(prev => [...prev, {
        role: 'system' as const,
        content: `I've updated the design based on your request: "${prompt}". The text is now more prominent and includes a clear call-to-action button.`,
        timestamp: new Date(),
      }]);
      setIsGenerating(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-[#101012] p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-white">Director Component Demo</h1>
          <p className="text-slate-400">Multi-turn chat interface for AI prompt interaction</p>
        </div>

        {/* Demo Controls */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white">Demo Controls</h2>
          
          <div className="flex gap-4">
            <button
              onClick={() => setIsGenerating(!isGenerating)}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors"
            >
              Toggle Generating State
            </button>
            
            <button
              onClick={() => setMessages([])}
              className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors"
            >
              Clear Messages
            </button>
            
            <button
              onClick={() => {
                setMessages([
                  {
                    role: 'system',
                    content: 'Hello! I\'m Mobius. I can help you generate brand-compliant assets. What would you like to create today?',
                    timestamp: new Date(Date.now() - 120000),
                  },
                  {
                    role: 'user',
                    content: 'Create a LinkedIn post image for our new product launch',
                    timestamp: new Date(Date.now() - 90000),
                  },
                  {
                    role: 'system',
                    content: 'I\'ve generated a LinkedIn post image featuring your brand colors and typography. The design includes your logo with proper spacing and uses the approved color palette.',
                    timestamp: new Date(Date.now() - 60000),
                  },
                  {
                    role: 'user',
                    content: 'Can you make the text more prominent and add a call-to-action?',
                    timestamp: new Date(Date.now() - 30000),
                  },
                ]);
              }}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
            >
              Reset to Default
            </button>
          </div>

          <div className="text-sm text-slate-400">
            <p><strong>Current State:</strong></p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Messages: {messages.length}</li>
              <li>Generating: {isGenerating ? 'Yes' : 'No'}</li>
            </ul>
          </div>
        </div>

        {/* Director Component */}
        <div className="h-[600px]">
          <Director
            sessionId="demo-session-123"
            onSubmit={handleSubmit}
            isGenerating={isGenerating}
            messages={messages}
          />
        </div>

        {/* Feature Notes */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-3">
          <h2 className="text-lg font-semibold text-white">Features to Test</h2>
          <ul className="list-disc list-inside text-slate-400 space-y-2">
            <li>Type a message and press Enter to submit (or click send button)</li>
            <li>Try Shift+Enter for multi-line input</li>
            <li>Click Quick Action chips to populate input field</li>
            <li>Watch character counter change color as you approach 1000 limit</li>
            <li>Toggle generating state to see "Mobius - Thinking..." indicator</li>
            <li>Scroll through chat history to see message alignment (user right, system left)</li>
            <li>Submit button glows when input is valid</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
