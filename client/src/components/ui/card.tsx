'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
  glow?: 'cyan' | 'violet' | 'amber' | 'rose' | 'emerald' | null;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({ hover = false, glow = null, padding = 'md', className, children, ...props }: CardProps) {
  const paddings = {
    none: '',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-6',
  };

  const glowMap = {
    cyan: 'border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.15)]',
    violet: 'border-violet-500/30 shadow-[0_0_20px_rgba(139,92,246,0.15)]',
    amber: 'border-amber-500/30 shadow-[0_0_20px_rgba(245,158,11,0.15)]',
    rose: 'border-rose-500/30 shadow-[0_0_20px_rgba(244,63,94,0.2)]',
    emerald: 'border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.15)]',
  };

  const Component = hover ? motion.div : 'div';
  const motionProps = hover
    ? {
        whileHover: { y: -2, scale: 1.005 },
        transition: { type: 'spring', stiffness: 400, damping: 25 },
      }
    : {};

  return (
    <Component
      {...motionProps}
      className={cn(
        'glass-card',
        paddings[padding],
        glow && glowMap[glow],
        hover && 'cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}
