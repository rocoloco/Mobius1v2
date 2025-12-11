/**
 * Monitoring System Types
 * 
 * Type definitions for the real-time brand compliance monitoring system
 */

// Base monitoring component props
export interface MonitoringComponentProps {
  className?: string;
  style?: React.CSSProperties;
  onError?: (error: Error) => void;
}

// Reasoning log entry for terminal teleprinter
export interface ReasoningLog {
  id: string;
  timestamp: Date;
  step: string;
  message: string;
  level: 'info' | 'warning' | 'error' | 'success';
}

// Color analysis data for spectral gauges
export interface ColorAnalysisData {
  color: string;        // Hex color code
  name: string;         // Color name
  percentage: number;   // 0-100 usage percentage
  usage: 'primary' | 'secondary' | 'accent' | 'neutral';
}

// Constraint status for caution matrix
export interface ConstraintStatus {
  id: string;
  category: string;
  label: string;
  status: 'satisfied' | 'warning' | 'violation' | 'critical';
  description?: string;
  lastUpdated: Date;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'compliance_score' | 'reasoning_log' | 'color_analysis' | 'constraint_update' | 'status_change';
  jobId: string;
  timestamp: Date;
  payload: unknown;
}

export interface ComplianceScoreMessage extends WebSocketMessage {
  type: 'compliance_score';
  payload: ComplianceScores;
}

export interface ReasoningLogMessage extends WebSocketMessage {
  type: 'reasoning_log';
  payload: ReasoningLog;
}

export interface ColorAnalysisMessage extends WebSocketMessage {
  type: 'color_analysis';
  payload: ColorAnalysisData[];
}

export interface ConstraintUpdateMessage extends WebSocketMessage {
  type: 'constraint_update';
  payload: ConstraintStatus[];
}

export interface StatusChangeMessage extends WebSocketMessage {
  type: 'status_change';
  payload: AuditStatus;
}

// Audit status
export interface AuditStatus {
  jobId: string;
  status: 'pending' | 'processing' | 'generating' | 'auditing' | 'correcting' | 'completed' | 'failed';
  progress: number;
  currentStep: string;
}

// Component state management
export interface MonitoringState {
  isConnected: boolean;
  currentJob: string | null;
  complianceScores: ComplianceScores;
  reasoningLogs: ReasoningLog[];
  colorAnalysis: ColorAnalysisData[];
  constraints: ConstraintStatus[];
  auditStatus: AuditStatus;
  lastUpdate: Date;
}

// Compliance scores (re-exported from CRT component)
export interface ComplianceScores {
  typography: number;    // 0-1 compliance score
  voice: number;        // 0-1 compliance score
  color: number;        // 0-1 compliance score
  logo: number;         // 0-1 compliance score
}

// WebSocket manager interface
export interface WebSocketManager {
  connect(jobId: string): Promise<void>;
  disconnect(): void;
  onComplianceUpdate: (callback: (scores: ComplianceScores) => void) => void;
  onReasoningLog: (callback: (log: ReasoningLog) => void) => void;
  onColorAnalysis: (callback: (data: ColorAnalysisData[]) => void) => void;
  onConstraintUpdate: (callback: (constraints: ConstraintStatus[]) => void) => void;
  onStatusChange: (callback: (status: AuditStatus) => void) => void;
}