'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

// ===== BADGE COMPONENTS =====

type Severity = 'low' | 'medium' | 'high' | 'critical';
type AnomalyStatus = 'new' | 'reviewed' | 'resolved';

const severityConfig: Record<Severity, { label: string; className: string }> = {
  critical: { label: 'Kritik', className: 'bg-rose-500/12 text-rose-400 border-rose-500/20' },
  high: { label: 'Yüksek', className: 'bg-amber-500/12 text-amber-400 border-amber-500/20' },
  medium: { label: 'Orta', className: 'bg-cyan-500/12 text-cyan-400 border-cyan-500/20' },
  low: { label: 'Düşük', className: 'bg-emerald-500/12 text-emerald-400 border-emerald-500/20' },
};

const statusConfig: Record<AnomalyStatus, { label: string; className: string }> = {
  new: { label: 'Yeni', className: 'bg-rose-500/12 text-rose-400 border-rose-500/20' },
  reviewed: { label: 'İncelendi', className: 'bg-cyan-500/12 text-cyan-400 border-cyan-500/20' },
  resolved: { label: 'Çözüldü', className: 'bg-emerald-500/12 text-emerald-400 border-emerald-500/20' },
};

const roleConfig: Record<string, { label: string; className: string }> = {
  admin: { label: 'Admin', className: 'bg-rose-500/12 text-rose-400' },
  manager: { label: 'Yönetici', className: 'bg-violet-500/12 text-violet-400' },
  operator: { label: 'Operatör', className: 'bg-cyan-500/12 text-cyan-400' },
  technician: { label: 'Teknisyen', className: 'bg-emerald-500/12 text-emerald-400' },
  procurement: { label: 'Satın Alma', className: 'bg-amber-500/12 text-amber-400' },
  viewer: { label: 'İzleyici', className: 'bg-muted/15 text-muted' },
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  const config = severityConfig[severity] || severityConfig.low;
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold border tracking-wide uppercase', config.className)}>
      {config.label}
    </span>
  );
}

export function StatusBadge({ status }: { status: AnomalyStatus }) {
  const config = statusConfig[status] || statusConfig.new;
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold border tracking-wide', config.className)}>
      {config.label}
    </span>
  );
}

export function RoleBadge({ role }: { role: string }) {
  const config = roleConfig[role] || roleConfig.viewer;
  return (
    <span className={cn('inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wider uppercase', config.className)}>
      {config.label}
    </span>
  );
}

// ===== CARD =====

export function Card({
  children,
  className,
  hover = false,
  glow,
}: {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: 'cyan' | 'rose' | 'amber' | 'emerald';
}) {
  return (
    <motion.div
      whileHover={hover ? { y: -2, transition: { duration: 0.2 } } : undefined}
      className={cn(
        'bg-surface border border-border rounded-xl transition-all duration-200',
        hover && 'hover:border-border-strong hover:shadow-elevated cursor-pointer',
        glow === 'cyan' && 'glow-border-cyan',
        glow === 'rose' && 'glow-border-rose',
        glow === 'amber' && 'glow-border-amber',
        glow === 'emerald' && 'glow-border-emerald',
        className
      )}
    >
      {children}
    </motion.div>
  );
}

// ===== BUTTON =====

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

const buttonVariants: Record<ButtonVariant, string> = {
  primary: 'bg-cyan text-background hover:brightness-110 shadow-lg shadow-cyan/15',
  secondary: 'bg-surface-2 text-foreground border border-border hover:border-border-strong hover:bg-surface-3',
  ghost: 'text-muted hover:text-foreground hover:bg-surface-2',
  danger: 'bg-rose/10 text-rose border border-rose/20 hover:bg-rose/20',
};

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  className,
  disabled,
  ...props
}: {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  disabled?: boolean;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-150 active:scale-[0.97]',
        buttonVariants[variant],
        size === 'sm' && 'px-3 py-1.5 text-xs',
        size === 'md' && 'px-4 py-2.5 text-sm',
        size === 'lg' && 'px-6 py-3 text-base',
        disabled && 'opacity-50 cursor-not-allowed pointer-events-none',
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}

// ===== INPUT =====

export function Input({
  label,
  error,
  className,
  ...props
}: {
  label?: string;
  error?: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div className="space-y-1.5">
      {label && <label className="block text-xs font-medium text-muted">{label}</label>}
      <input
        className={cn(
          'w-full px-3.5 py-2.5 rounded-lg bg-surface-2 border border-border text-foreground text-sm',
          'placeholder:text-muted/60 focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10',
          'transition-all duration-200',
          error && 'border-rose/50 focus:border-rose/60 focus:ring-rose/10',
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-rose">{error}</p>}
    </div>
  );
}

// ===== SKELETON =====

export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn('rounded-lg animate-shimmer', className)} />
  );
}

// ===== PROGRESS BAR =====

export function ProgressBar({
  value,
  max = 100,
  color = 'cyan',
  size = 'sm',
  showLabel = false,
}: {
  value: number;
  max?: number;
  color?: 'cyan' | 'rose' | 'amber' | 'emerald' | 'violet';
  size?: 'xs' | 'sm' | 'md';
  showLabel?: boolean;
}) {
  const pct = Math.min(100, (value / max) * 100);
  const colorMap = {
    cyan: 'bg-cyan',
    rose: 'bg-rose',
    amber: 'bg-amber',
    emerald: 'bg-emerald',
    violet: 'bg-violet',
  };
  const sizeMap = { xs: 'h-1', sm: 'h-1.5', md: 'h-2.5' };

  return (
    <div className="space-y-1">
      {showLabel && (
        <div className="flex justify-between text-[10px] text-muted">
          <span>{value}</span>
          <span>{max}</span>
        </div>
      )}
      <div className={cn('w-full rounded-full bg-surface-3 overflow-hidden', sizeMap[size])}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={cn('h-full rounded-full', colorMap[color])}
        />
      </div>
    </div>
  );
}

// ===== STATUS DOT =====

export function StatusDot({ status, pulse = true }: { status: string; pulse?: boolean }) {
  const colorMap: Record<string, string> = {
    critical: 'bg-rose',
    warning: 'bg-amber',
    watch: 'bg-cyan',
    safe: 'bg-emerald',
    healthy: 'bg-emerald',
    degraded: 'bg-amber',
    down: 'bg-rose',
  };

  return (
    <span className="relative flex items-center justify-center w-3 h-3">
      {pulse && (status === 'critical' || status === 'down') && (
        <span className={cn('absolute inset-0 rounded-full opacity-40 animate-ping', colorMap[status] || 'bg-muted')} />
      )}
      <span className={cn('relative block w-2 h-2 rounded-full', colorMap[status] || 'bg-muted')} />
    </span>
  );
}

// ===== ANIMATED COUNTER =====

export function AnimatedCounter({ value, className }: { value: number; className?: string }) {
  return (
    <motion.span
      key={value}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className={className}
    >
      {value}
    </motion.span>
  );
}

// ===== MODAL =====

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}: {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}) {
  if (!isOpen) return null;

  const sizeMap = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl' };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 8 }}
        className={cn(
          'relative w-full bg-surface border border-border rounded-2xl shadow-elevated overflow-hidden',
          sizeMap[size]
        )}
      >
        {title && (
          <div className="px-6 py-4 border-b border-border">
            <h3 className="text-base font-semibold font-heading text-foreground">{title}</h3>
          </div>
        )}
        <div className="p-6">{children}</div>
      </motion.div>
    </motion.div>
  );
}
