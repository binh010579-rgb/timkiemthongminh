interface SkeletonProps {
  className?: string
}

/**
 * Khối skeleton cơ bản — chỉ dùng Tailwind utility `animate-pulse` (CSS thuần,
 * không phải thư viện ngoài). Dùng làm building block cho mọi skeleton khác.
 */
export default function Skeleton({ className = '' }: SkeletonProps) {
  return <div className={`animate-pulse rounded-md bg-slate-200/80 dark:bg-slate-700/60 ${className}`} />
}
