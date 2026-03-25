import type { Task } from '../types/forge-pipeline';

const DAY = 1000 * 60 * 60 * 24;

export function getTimeState(task: Task, now = new Date()): 'on_track' | 'due_soon' | 'overdue' | 'stale' {
  const nowMs = now.getTime();

  if (task.dueAt) {
    const dueMs = new Date(task.dueAt).getTime();
    if (task.status !== 'done' && dueMs < nowMs) return 'overdue';
    if (task.status !== 'done' && dueMs - nowMs <= 7 * DAY) return 'due_soon';
  }

  const lastActivityMs = new Date(task.lastActivityAt).getTime();
  if (nowMs - lastActivityMs >= 5 * DAY) return 'stale';

  return 'on_track';
}

export function getDerivedRisk(task: Task, now = new Date()): 'none' | 'watch' | 'at_risk' | 'critical' {
  const timeState = getTimeState(task, now);

  if (timeState === 'overdue') return task.priority === 'critical' ? 'critical' : 'at_risk';
  if (task.status === 'blocked') return 'at_risk';
  if ((task.priority === 'high' || task.priority === 'critical') && timeState === 'due_soon') return 'at_risk';
  if (timeState === 'stale' && (task.priority === 'high' || task.priority === 'critical')) return 'at_risk';

  return task.riskState ?? 'none';
}

export function getFocusScore(task: Task, now = new Date()): number {
  let score = 0;
  const timeState = getTimeState(task, now);

  if (task.priority === 'critical') score += 100;
  if (task.priority === 'high') score += 60;
  if (task.priority === 'medium') score += 30;
  if (task.priority === 'low') score += 10;

  if (timeState === 'overdue') score += 50;
  if (timeState === 'due_soon') score += 25;
  if (timeState === 'stale') score += 20;
  if (task.status === 'blocked') score -= 40;

  return score;
}
