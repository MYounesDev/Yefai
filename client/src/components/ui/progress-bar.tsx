'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number;
  max?: number;
  color?: 'cyan' | 'violet' | 'amber' | 'rose' | 'emerald' | 'gradient' | 'wear';
  size?: 'xs' | 'sm' | 'md';
  showLabel?: boolean;
  className?: string;
  animate?: boolean;
}

const colorMap = {
  cyan: 'bg-cyan-500',
  violet: 'bg-violet-500',
  amber: 'bg-amber-500',
  rose: 'bg-rose-500',
  emerald: 'bg-emerald-500',
  gradient: 'bg-gradient-to-r from-cyan-500 to-violet-500',
  wear: '', // computed
};

const sizeMap = { xs: 'h-1', sm: 'h-1.5', md: 'h-2' };

export function ProgressBar({
  value,
  max = 100,
  color = 'cyan',
  size = 'sm',
  showLabel = false,
  className,
  animate = true,
}: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));

  // Dynamic color for wear
  let barClass = colorMap[color];
  if (color === 'wear') {
    if (pct > 90) barClass = 'bg-rose-500';
    else if (pct > 80) barClass = 'bg-amber-500';
    else if (pct > 60) barClass = 'bg-yellow-500';
    else barClass = 'bg-emerald-500';
  }

  return (
    <div className={cn('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between text-xs text-muted mb-1">
          <span>{value}</span>
          <span>{max}</span>
        </div>
      )}
      <div className={cn('w-full bg-surface-2 rounded-full overflow-hidden', sizeMap[size])}>
        <motion.div
          className={cn('h-full rounded-full', barClass)}
          initial={animate ? { width: 0 } : { width: `${pct}%` }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        />
      </div>
    </div>
  );
}
