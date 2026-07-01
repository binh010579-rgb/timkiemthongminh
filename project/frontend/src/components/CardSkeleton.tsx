import Skeleton from './Skeleton'

interface CardSkeletonProps {
  /** 'grid' = card có thumbnail lớn (dùng cho Latest News), 'row' = card nằm ngang nhỏ (dùng cho Featured side card) */
  variant?: 'grid' | 'row'
}

/**
 * Skeleton mô phỏng đúng hình dạng của 1 card tin tức
 * (thumbnail, tiêu đề, tóm tắt, ngày đăng, nút) để tái sử dụng
 * ở cả Featured News và Latest News.
 */
export default function CardSkeleton({ variant = 'grid' }: CardSkeletonProps) {
  if (variant === 'row') {
    return (
      <div className="flex gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <Skeleton className="h-20 w-24 shrink-0 rounded-lg" />
        <div className="flex min-w-0 flex-1 flex-col justify-center gap-2">
          <Skeleton className="h-3.5 w-full" />
          <Skeleton className="h-3.5 w-3/4" />
          <Skeleton className="h-3 w-1/3" />
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <Skeleton className="aspect-[16/10] w-full rounded-none" />
      <div className="flex flex-1 flex-col gap-3 p-5">
        <Skeleton className="h-5 w-16 rounded-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-1/2" />
        <Skeleton className="mt-2 h-3 w-1/4" />
        <Skeleton className="mt-2 h-9 w-28 rounded-full" />
      </div>
    </div>
  )
}
