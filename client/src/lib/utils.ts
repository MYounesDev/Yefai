import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
}

export function severityColor(severity: string): string {
  switch (severity) {
    case 'critical': return 'text-rose-400';
    case 'high': return 'text-amber-400';
    case 'medium': return 'text-yellow-400';
    case 'low': return 'text-emerald-400';
    default: return 'text-gray-400';
  }
}

export function riskLevelColor(level: string): string {
  switch (level) {
    case 'crisis': return 'text-rose-400';
    case 'at_risk': return 'text-amber-400';
    case 'watch': return 'text-cyan-400';
    default: return 'text-gray-400';
  }
}

export function statusColor(status: string): string {
  switch (status) {
    case 'critical': return '#F43F5E';
    case 'warning': return '#F59E0B';
    case 'watch': return '#EAB308';
    case 'safe': return '#10B981';
    default: return '#6B7280';
  }
}

export function formatWear(um: number): string {
  return `${um} µm`;
}

export function wearLevelColor(wear: number, threshold = 200): string {
  const pct = wear / threshold;
  if (pct > 0.9) return '#F43F5E';
  if (pct > 0.8) return '#F59E0B';
  if (pct > 0.6) return '#EAB308';
  return '#10B981';
}
