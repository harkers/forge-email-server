export type JobStatus =
  | 'new'
  | 'validating'
  | 'routed'
  | 'in_progress'
  | 'awaiting_input'
  | 'awaiting_review'
  | 'approved'
  | 'completed'
  | 'archived'
  | 'failed'
  | 'cancelled';

export type RequestType =
  | 'privacy_incident'
  | 'vendor_assessment'
  | 'general_project'
  | 'unclassified';

export interface JobRecord {
  jobId: string;
  requestType: RequestType;
  guildId: string;
  guildKey: string;
  channelId: string;
  channelKey: string;
  threadId?: string;
  requesterId: string;
  requesterRole: string;
  workspaceKey?: string;
  workflowId?: string;
  primaryAgent?: string;
  reviewerRole?: string;
  approvalRequired?: boolean | 'conditional' | 'optional';
  auditLevel?: 'medium' | 'high' | 'critical';
  status: JobStatus;
  createdAt: string;
  updatedAt: string;
}
