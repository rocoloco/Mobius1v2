/**
 * WebSocket Manager for Real-Time Brand Compliance Monitoring
 * 
 * Provides real-time communication for compliance scores, reasoning logs,
 * color analysis, and constraint updates during brand audit processes.
 */

import React from 'react';
import { EventEmitter } from 'events';

// WebSocket message types based on design document
export interface WebSocketMessage {
  type: 'compliance_score' | 'reasoning_log' | 'color_analysis' | 'constraint_update' | 'status_change';
  jobId: string;
  timestamp: string;
  payload: unknown;
}

export interface ComplianceScores {
  typography: number;    // 0-1 compliance score
  voice: number;        // 0-1 compliance score
  color: number;        // 0-1 compliance score
  logo: number;         // 0-1 compliance score
}

export interface ComplianceScoreMessage extends WebSocketMessage {
  type: 'compliance_score';
  payload: ComplianceScores;
}

export interface ReasoningLog {
  id: string;
  timestamp: Date;
  step: string;
  message: string;
  level: 'info' | 'warning' | 'error' | 'success';
}

export interface ReasoningLogMessage extends WebSocketMessage {
  type: 'reasoning_log';
  payload: ReasoningLog;
}

export interface ColorAnalysisData {
  color: string;        // Hex color code
  name: string;         // Color name
  percentage: number;   // 0-100 usage percentage
  usage: 'primary' | 'secondary' | 'accent' | 'neutral';
}

export interface ColorAnalysisMessage extends WebSocketMessage {
  type: 'color_analysis';
  payload: ColorAnalysisData[];
}

export interface ConstraintStatus {
  id: string;
  category: string;
  label: string;
  status: 'satisfied' | 'warning' | 'violation' | 'critical';
  description?: string;
  lastUpdated: Date;
}

export interface ConstraintUpdateMessage extends WebSocketMessage {
  type: 'constraint_update';
  payload: ConstraintStatus[];
}

export interface AuditStatus {
  jobId: string;
  status: 'pending' | 'processing' | 'generating' | 'auditing' | 'correcting' | 'completed' | 'failed';
  progress: number;
  currentStep: string;
}

export interface StatusChangeMessage extends WebSocketMessage {
  type: 'status_change';
  payload: AuditStatus;
}

export type WebSocketConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface WebSocketManagerConfig {
  baseUrl?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  messageTimeout?: number;
}

/**
 * WebSocket Manager for real-time monitoring communication
 * 
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Message validation and type safety
 * - Event-driven architecture for component updates
 * - Graceful fallback to polling mode
 * - Connection state management
 */
export class WebSocketManager extends EventEmitter {
  private ws: WebSocket | null = null;
  private jobId: string | null = null;
  private connectionStatus: WebSocketConnectionStatus = 'disconnected';
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private config: Required<WebSocketManagerConfig>;
  private messageQueue: WebSocketMessage[] = [];
  private isReconnecting = false;

  constructor(config: WebSocketManagerConfig = {}) {
    super();
    
    this.config = {
      baseUrl: config.baseUrl || this.getWebSocketUrl(),
      reconnectInterval: config.reconnectInterval || 1000,
      maxReconnectAttempts: config.maxReconnectAttempts || 10,
      heartbeatInterval: config.heartbeatInterval || 30000,
      messageTimeout: config.messageTimeout || 5000,
    };
  }

  /**
   * Get WebSocket URL based on current environment
   */
  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    
    // For development, use localhost backend
    if (host.includes('localhost') || host.includes('127.0.0.1')) {
      return `${protocol}//${host}/ws`;
    }
    
    // For production, use the same host
    return `${protocol}//${host}/ws`;
  }

  /**
   * Connect to WebSocket server for a specific job
   */
  async connect(jobId: string): Promise<void> {
    if (this.ws && this.ws.readyState === WebSocket.OPEN && this.jobId === jobId) {
      return; // Already connected to this job
    }

    this.jobId = jobId;
    this.setConnectionStatus('connecting');

    try {
      const wsUrl = `${this.config.baseUrl}/monitoring/${jobId}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);

      // Wait for connection to open or fail
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, this.config.messageTimeout);

        this.ws!.onopen = (event) => {
          clearTimeout(timeout);
          this.handleOpen(event);
          resolve();
        };

        this.ws!.onerror = (event) => {
          clearTimeout(timeout);
          this.handleError(event);
          reject(new Error('WebSocket connection failed'));
        };
      });

    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.setConnectionStatus('error');
      
      // Attempt reconnection if not at max attempts
      if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
        this.scheduleReconnect();
      } else {
        this.emit('fallback_to_polling', { jobId, error });
      }
      
      throw error;
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.clearTimers();
    this.isReconnecting = false;
    this.reconnectAttempts = 0;
    this.jobId = null;

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.setConnectionStatus('disconnected');
  }

  /**
   * Get current connection status
   */
  getConnectionStatus(): WebSocketConnectionStatus {
    return this.connectionStatus;
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN && this.connectionStatus === 'connected';
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(event: Event): void {
    console.log('WebSocket connected:', this.jobId);
    this.setConnectionStatus('connected');
    this.reconnectAttempts = 0;
    this.isReconnecting = false;
    
    // Start heartbeat
    this.startHeartbeat();
    
    // Process queued messages
    this.processMessageQueue();
    
    this.emit('connected', { jobId: this.jobId });
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      // Validate message structure
      if (!this.validateMessage(message)) {
        console.warn('Invalid WebSocket message received:', message);
        return;
      }

      // Emit specific event based on message type
      switch (message.type) {
        case 'compliance_score':
          this.emit('compliance_update', (message as ComplianceScoreMessage).payload);
          break;
        case 'reasoning_log':
          this.emit('reasoning_log', (message as ReasoningLogMessage).payload);
          break;
        case 'color_analysis':
          this.emit('color_analysis', (message as ColorAnalysisMessage).payload);
          break;
        case 'constraint_update':
          this.emit('constraint_update', (message as ConstraintUpdateMessage).payload);
          break;
        case 'status_change':
          this.emit('status_change', (message as StatusChangeMessage).payload);
          break;
        default:
          console.warn('Unknown message type:', message.type);
      }

      // Emit generic message event
      this.emit('message', message);

    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
      this.emit('message_error', { error, rawData: event.data });
    }
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason);
    this.clearTimers();
    this.setConnectionStatus('disconnected');

    // Attempt reconnection if not a clean close and we have a job ID
    if (event.code !== 1000 && this.jobId && !this.isReconnecting) {
      this.scheduleReconnect();
    }

    this.emit('disconnected', { 
      jobId: this.jobId, 
      code: event.code, 
      reason: event.reason 
    });
  }

  /**
   * Handle WebSocket error event
   */
  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.setConnectionStatus('error');
    this.emit('error', { jobId: this.jobId, event });
  }

  /**
   * Schedule reconnection with exponential backoff
   */
  private scheduleReconnect(): void {
    if (this.isReconnecting || this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      return;
    }

    this.isReconnecting = true;
    const delay = Math.min(
      this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts),
      30000 // Max 30 seconds
    );

    console.log(`Scheduling WebSocket reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);

    this.reconnectTimer = setTimeout(async () => {
      if (this.jobId) {
        this.reconnectAttempts++;
        try {
          await this.connect(this.jobId);
        } catch (error) {
          console.error('Reconnection failed:', error);
          // scheduleReconnect will be called again from handleError if needed
        }
      }
    }, delay);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: new Date().toISOString() }));
      }
    }, this.config.heartbeatInterval);
  }

  /**
   * Clear all timers
   */
  private clearTimers(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * Set connection status and emit event
   */
  private setConnectionStatus(status: WebSocketConnectionStatus): void {
    if (this.connectionStatus !== status) {
      this.connectionStatus = status;
      this.emit('status_change', status);
    }
  }

  /**
   * Validate incoming message structure
   */
  private validateMessage(message: any): message is WebSocketMessage {
    return (
      message &&
      typeof message === 'object' &&
      typeof message.type === 'string' &&
      typeof message.jobId === 'string' &&
      typeof message.timestamp === 'string' &&
      message.payload !== undefined
    );
  }

  /**
   * Process queued messages after reconnection
   */
  private processMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        // Re-emit queued messages
        this.emit('message', message);
      }
    }
  }

  /**
   * Event listener registration helpers
   */
  onComplianceUpdate(callback: (scores: ComplianceScores) => void): void {
    this.on('compliance_update', callback);
  }

  onReasoningLog(callback: (log: ReasoningLog) => void): void {
    this.on('reasoning_log', callback);
  }

  onColorAnalysis(callback: (data: ColorAnalysisData[]) => void): void {
    this.on('color_analysis', callback);
  }

  onConstraintUpdate(callback: (constraints: ConstraintStatus[]) => void): void {
    this.on('constraint_update', callback);
  }

  onStatusChange(callback: (status: AuditStatus) => void): void {
    this.on('status_change', callback);
  }

  onConnectionStatusChange(callback: (status: WebSocketConnectionStatus) => void): void {
    this.on('status_change', callback);
  }

  onError(callback: (error: any) => void): void {
    this.on('error', callback);
  }

  onFallbackToPolling(callback: (data: { jobId: string; error: any }) => void): void {
    this.on('fallback_to_polling', callback);
  }
}

// Singleton instance for global use
let globalWebSocketManager: WebSocketManager | null = null;

/**
 * Get or create global WebSocket manager instance
 */
export function getWebSocketManager(config?: WebSocketManagerConfig): WebSocketManager {
  if (!globalWebSocketManager) {
    globalWebSocketManager = new WebSocketManager(config);
  }
  return globalWebSocketManager;
}

/**
 * React hook for WebSocket connection management
 */
export function useWebSocket(jobId: string | null) {
  const [connectionStatus, setConnectionStatus] = React.useState<WebSocketConnectionStatus>('disconnected');
  const [error, setError] = React.useState<Error | null>(null);
  const wsManager = React.useRef<WebSocketManager | null>(null);

  React.useEffect(() => {
    if (!jobId) return;

    wsManager.current = getWebSocketManager();
    
    const handleStatusChange = (status: WebSocketConnectionStatus) => {
      setConnectionStatus(status);
    };

    const handleError = (errorData: any) => {
      setError(new Error(errorData.event?.message || 'WebSocket error'));
    };

    const handleFallback = () => {
      console.warn('WebSocket failed, falling back to polling mode');
      // Could implement polling fallback here
    };

    wsManager.current.onConnectionStatusChange(handleStatusChange);
    wsManager.current.onError(handleError);
    wsManager.current.onFallbackToPolling(handleFallback);

    // Connect to WebSocket
    wsManager.current.connect(jobId).catch((err) => {
      console.error('Failed to connect to WebSocket:', err);
      setError(err);
    });

    return () => {
      wsManager.current?.disconnect();
    };
  }, [jobId]);

  return {
    connectionStatus,
    error,
    wsManager: wsManager.current,
    isConnected: connectionStatus === 'connected',
  };
}