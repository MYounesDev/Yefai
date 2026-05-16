import { cn } from '@/lib/utils';

type DotColor = 'green' | 'amber' | 'rose' | 'cyan' | 'gray';
type MachineStatus = 'safe' | 'watch' | 'warning' | 'critical';

const STATUS_TO_COLOR: Record<MachineStatus, DotColor> = {
  safe: 'green', watch: 'cyan', warning: 'amber', critical: 'rose',
};

interface StatusDotProps {
  color?: DotColor;
  status?: MachineStatus;
  pulse?: boolean;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

const colorMap: Record<DotColor, string> = {
  green: 'bg-emerald-400',
  amber: 'bg-amber-400',
  rose: 'bg-rose-400',
  cyan: 'bg-cyan-400',
  gray: 'bg-gray-500',
};

const sizeMap = { sm: 'w-1.5 h-1.5', md: 'w-2 h-2', lg: 'w-2.5 h-2.5' };

export function StatusDot({ color, status, pulse, size = 'md', label }: StatusDotProps) {
  const resolvedColor: DotColor = color ?? (status ? STATUS_TO_COLOR[status] : 'green');
  const resolvedPulse = pulse ?? (status === 'critical');
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="relative inline-flex">
        <span className={cn('rounded-full', sizeMap[size], colorMap[resolvedColor])} />
        {resolvedPulse && (
          <span
            className={cn('absolute inset-0 rounded-full animate-ping opacity-75', colorMap[resolvedColor])}
          />
        )}
      </span>
      {label && <span className="text-xs text-muted">{label}</span>}
    </span>
  );
}

export function machineStatusDot(status: string) {
  const map: Record<string, DotColor> = {
    safe: 'green',
    watch: 'amber',
    warning: 'amber',
    critical: 'rose',
  };
  return <StatusDot color={map[status] ?? 'gray'} pulse={status === 'critical'} />;
}
