import { ActivityEvent, Source, Task } from '../types/forge-pipeline';

export const mockTasks: Task[] = [
  {
    id: 'task-1',
    projectId: 'proj-display',
    title: 'Add scheduling logic',
    status: 'in_progress',
    priority: 'high',
    riskState: 'watch',
    dueAt: '2026-03-28T17:00:00Z',
    createdAt: '2026-03-24T14:00:00Z',
    updatedAt: '2026-03-24T18:04:00Z',
    lastActivityAt: '2026-03-24T18:04:00Z',
    sourceId: 'src-display',
    sourceRef: 'display-forge',
    owner: 'Stu',
    tags: ['scheduling'],
  },
  {
    id: 'task-2',
    projectId: 'proj-privacy',
    title: 'Review intake template',
    status: 'todo',
    priority: 'high',
    riskState: 'watch',
    dueAt: '2026-03-31T17:00:00Z',
    createdAt: '2026-03-24T13:00:00Z',
    updatedAt: '2026-03-24T17:16:00Z',
    lastActivityAt: '2026-03-24T17:16:00Z',
    sourceId: 'src-privacy',
    sourceRef: 'privacy-dsar',
    owner: 'Stu',
    tags: ['intake'],
  },
  {
    id: 'task-3',
    projectId: 'proj-memory',
    title: 'Review Memory Stack architecture',
    status: 'todo',
    priority: 'high',
    riskState: 'none',
    createdAt: '2026-03-24T10:00:00Z',
    updatedAt: '2026-03-24T16:16:00Z',
    lastActivityAt: '2026-03-24T16:16:00Z',
    sourceId: 'src-memory',
    sourceRef: 'memory-stack',
    owner: 'Stu',
    tags: ['architecture'],
  },
];

export const mockActivity: ActivityEvent[] = [
  {
    id: 'act-1',
    taskId: 'task-3',
    type: 'status_changed',
    timestamp: '2026-03-24T18:02:00Z',
    details: 'Status changed to todo',
    source: 'Memory Stack',
  },
  {
    id: 'act-2',
    taskId: 'task-3',
    type: 'priority_changed',
    timestamp: '2026-03-24T17:38:00Z',
    details: 'Priority changed to medium',
    source: 'Memory Stack',
  },
];

export const mockSources: Source[] = [
  { id: 'src-memory', name: 'Memory Stack', type: 'workspace', healthState: 'healthy', lastSyncAt: '2026-03-24T18:14:00Z' },
  { id: 'src-display', name: 'Display Forge', type: 'workspace', healthState: 'healthy', lastSyncAt: '2026-03-24T18:13:00Z' },
  { id: 'src-privacy', name: 'Privacy-DSAR', type: 'workspace', healthState: 'delayed', lastSyncAt: '2026-03-24T17:58:00Z' },
  { id: 'src-calendar', name: 'Forge Calendar', type: 'workspace', healthState: 'healthy', lastSyncAt: '2026-03-24T18:15:00Z' },
];
