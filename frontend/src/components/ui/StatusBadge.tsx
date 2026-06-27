import React from 'react';
import { cn } from '@/lib/utils';
import { IndexingStatus } from '@/types/repository';

interface StatusBadgeProps {
  status: IndexingStatus;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const styles: Record<IndexingStatus, string> = {
    pending: 'bg-yellow-500/20 text-yellow-400',
    running: 'bg-emerald-500/20 text-emerald-400 animate-pulse',
    complete: 'bg-green-500/20 text-green-400',
    failed: 'bg-red-500/20 text-red-400',
  };

  const labels: Record<IndexingStatus, string> = {
    pending: 'Pending',
    running: 'Indexing...',
    complete: 'Ready',
    failed: 'Failed',
  };

  return (
    <span className={cn('px-2.5 py-0.5 rounded-full text-xs font-medium', styles[status])}>
      {labels[status]}
    </span>
  );
}
