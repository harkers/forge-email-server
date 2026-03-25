export interface AuditEvent {
  eventId: string;
  jobId: string;
  timestamp: string;
  actorType: 'user' | 'bot' | 'system' | 'reviewer';
  actorIdOrName: string;
  eventType: string;
  summary: string;
  metadata?: Record<string, unknown>;
}
