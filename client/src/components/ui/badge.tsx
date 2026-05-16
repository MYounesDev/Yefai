import { cn } from '@/lib/utils';

type BadgeVariant = 'cyan' | 'violet' | 'amber' | 'rose' | 'emerald' | 'gray' | 'blue';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  pulse?: boolean;
  size?: 'sm' | 'md';
}

const variantStyles: Record<BadgeVariant, string> = {
  cyan: 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30',
  violet: 'bg-violet-500/15 text-violet-400 border border-violet-500/30',
  amber: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  rose: 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
  emerald: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  gray: 'bg-white/5 text-gray-400 border border-white/10',
  blue: 'bg-blue-500/15 text-blue-400 border border-blue-500/30',
};

export function Badge({ variant = 'gray', pulse = false, size = 'sm', className, children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full font-medium',
        size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1',
        variantStyles[variant],
        pulse && 'animate-pulse',
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

// Convenience wrappers
export function SeverityBadge({ severity }: { severity: string }) {
  const map: Record<string, BadgeVariant> = {
    critical: 'rose',
    high: 'amber',
    medium: 'cyan',
    low: 'emerald',
  };
  return <Badge variant={map[severity] ?? 'gray'} pulse={severity === 'critical'}>{severity.charAt(0).toUpperCase() + severity.slice(1)}</Badge>;
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, BadgeVariant> = {
    new: 'cyan',
    reviewed: 'violet',
    resolved: 'emerald',
    active: 'emerald',
    invited: 'amber',
    disabled: 'gray',
  };
  return <Badge variant={map[status] ?? 'gray'}>{status.charAt(0).toUpperCase() + status.slice(1)}</Badge>;
}

export function RiskBadge({ level }: { level: string }) {
  const map: Record<string, BadgeVariant> = {
    crisis: 'rose',
    at_risk: 'amber',
    watch: 'cyan',
    none: 'gray',
  };
  const labels: Record<string, string> = { crisis: 'Crisis', at_risk: 'At Risk', watch: 'Watch', none: 'None' };
  return <Badge variant={map[level] ?? 'gray'} pulse={level === 'crisis'}>{labels[level] ?? level}</Badge>;
}

export function RoleBadge({ role }: { role: string }) {
  const map: Record<string, BadgeVariant> = {
    manager: 'violet',
    operator: 'cyan',
    technician: 'amber',
    procurement: 'emerald',
    viewer: 'gray',
    admin: 'rose',
  };
  return <Badge variant={map[role] ?? 'gray'}>{role.charAt(0).toUpperCase() + role.slice(1)}</Badge>;
}
