import { cn } from '@/lib/utils';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  rounded?: 'sm' | 'md' | 'lg' | 'full';
}

export function Skeleton({ className, rounded = 'md', ...props }: SkeletonProps) {
  const radiusMap = { sm: 'rounded-sm', md: 'rounded-lg', lg: 'rounded-xl', full: 'rounded-full' };
  return (
    <div
      className={cn('animate-shimmer bg-surface', radiusMap[rounded], className)}
      {...props}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex items-center gap-3">
        <Skeleton className="w-10 h-10" rounded="lg" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-3 w-1/3" />
        </div>
      </div>
      <Skeleton className="h-8 w-2/3" />
      <Skeleton className="h-2 w-full" />
    </div>
  );
}

export function TableRowSkeleton({ cols = 6 }: { cols?: number }) {
  return (
    <tr>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  );
}
