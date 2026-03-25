export type TaskStatus = 'todo' | 'in_progress' | 'blocked' | 'done' | 'archived';
export type Priority = 'low' | 'medium' | 'high' | 'critical';
export type RiskState = 'none' | 'watch' | 'at_risk' | 'critical';
export type TimeState = 'on_track' | 'due_soon' | 'overdue' | 'stale';
export type SourceHealth = 'healthy' | 'delayed' | 'error' | 'paused';

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  type: string;
  status: string;
}

export interface Project {
  id: string;
  workspaceId: string;
  name: string;
  description?: string;
  status: string;
}

export interface Task {
  id: string;
  projectId: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: Priority;
  riskState: RiskState;
  dueAt?: string;
  createdAt: string;
  updatedAt: string;
  lastActivityAt: string;
  blockedAt?: string;
  blockedReason?: string;
  sourceId: string;
  sourceRef?: string;
  owner?: string;
  tags?: string[];
}

export interface ActivityEvent {
  id: string;
  taskId: string;
  type: string;
  timestamp: string;
  actor?: string;
  source?: string;
  details?: string;
}

export interface Source {
  id: string;
  name: string;
  type: string;
  healthState: SourceHealth;
  lastSyncAt: string;
  latencyMs?: number;
  errorMessage?: string;
}
