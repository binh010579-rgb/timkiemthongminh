import Skeleton from './Skeleton'

/**
 * Skeleton cho Hero Section: mô phỏng badge, tiêu đề, subtitle và thanh tìm kiếm
 * trong lúc trang đang tải dữ liệu lần đầu.
 */
export default function HeroSkeleton() {
  return (
    <section className="relative overflow-hidden bg-white px-4 py-20 sm:py-28 dark:bg-slate-900">
      <div className="absolute inset-0 -z-20 bg-gradient-to-b from-indigo-50 via-white to-white dark:from-indigo-950/40 dark:via-slate-900 dark:to-slate-900" />

      <div className="mx-auto flex max-w-4xl flex-col items-center text-center">
        <Skeleton className="mb-5 h-7 w-40 rounded-full" />

        <Skeleton className="h-10 w-[90%] max-w-xl sm:h-12 md:h-14" />
        <Skeleton className="mt-3 h-10 w-[70%] max-w-md sm:h-12 md:h-14" />

        <Skeleton className="mt-5 h-4 w-full max-w-2xl" />
        <Skeleton className="mt-2 h-4 w-3/4 max-w-xl" />

        <Skeleton className="mx-auto mt-10 h-16 w-full max-w-2xl rounded-3xl" />

        <Skeleton className="mt-4 h-3 w-56" />
      </div>
    </section>
  )
}
