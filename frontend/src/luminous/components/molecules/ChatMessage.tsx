import { memo } from 'react';
import { luminousTokens } from '../../tokens';

interface ChatMessageProps {
  role: 'user' | 'system' | 'error';
  content: string;
  timestamp: Date;
}

/**
 * ChatMessage - Individual chat message component for Director
 * 
 * Displays a single message in the chat interface with role-based alignment
 * and styling. User messages are right-aligned with purple tint, system
 * messages are left-aligned with neutral glass background.
 * 
 * @param role - Message sender role ('user' or 'system')
 * @param content - Message text content
 * @param timestamp - Message timestamp
 */
export const ChatMessage = memo(function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isUser = role === 'user';
  const isError = role === 'error';
  
  // Format timestamp to HH:MM
  const timeString = timestamp.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
  
// Get background and border colors based on role
  const getBackgroundColor = () => {
    if (isUser) return 'rgba(168, 85, 247, 0.1)';
    if (isError) return 'rgba(239, 68, 68, 0.1)';
    return 'rgba(255, 255, 255, 0.05)';
  };
  
  const getBorderColor = () => {
    if (isUser) return 'rgba(168, 85, 247, 0.2)';
    if (isError) return 'rgba(239, 68, 68, 0.2)';
    return 'rgba(255, 255, 255, 0.1)';
  };
  
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
      }}
      data-testid="chat-message"
      data-role={role}
    >
      <div
        style={{
          maxWidth: '80%',
          borderRadius: '16px',
          padding: '16px 20px',
          backdropFilter: 'blur(12px)',
          border: `1px solid ${getBorderColor()}`,
          backgroundColor: getBackgroundColor(),
        }}
      >
        <p
          style={{
            fontSize: '14px',
            lineHeight: '1.6',
            margin: 0,
            color: isError ? '#EF4444' : luminousTokens.colors.text.body,
          }}
        >
          {content}
        </p>
        <p
          style={{
            fontSize: '12px',
            color: luminousTokens.colors.text.muted,
            marginTop: '12px',
            marginBottom: 0,
          }}
        >
          {timeString}
        </p>
      </div>
    </div>
  );
});
