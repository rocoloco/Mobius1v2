import { getConnectionColor } from '../../tokens';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

interface ConnectionPulseProps {
  status: 'connected' | 'disconnected' | 'connecting';
}

/**
 * ConnectionPulse - Connection status indicator
 * 
 * Displays a colored dot indicating WebSocket connection status.
 * Applies pulse animation for connected and connecting states.
 * 
 * @param status - Connection status: 'connected' | 'disconnected' | 'connecting'
 */
export function ConnectionPulse({ status }: ConnectionPulseProps) {
  const prefersReducedMotion = useReducedMotion();
  const colorClass = getConnectionColor(status);
  const shouldPulse = (status === 'connected' || status === 'connecting') && !prefersReducedMotion;
  
  return (
    <div
      className={`w-2 h-2 rounded-full ${colorClass} ${shouldPulse ? 'animate-connection-pulse' : ''}`}
      data-testid="connection-pulse"
      aria-label={`Connection status: ${status}`}
      role="status"
    />
  );
}
