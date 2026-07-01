import type { NewsItem } from '../types/news'
import { formatDate } from '../utils/formatDate'
import CardSkeleton from './CardSkeleton'

interface LatestNewsProps {
  items: NewsItem[]
  title?: string
  subtitle?: string
  isLoading?: boolean
  /** Số card skeleton hiển thị khi đang loading. */
  skeletonCount?: number
}

const FALLBACK_IMAGE =
  'https://images.unsplash.com/photo-1495020689067-958852a7765e?w=500&h=320&fit=crop'

/**
 * Component "Tin mới nhất": hiển thị danh sách bài báo dạng grid responsive.
 * - Desktop: 3 cột
 * - Tablet: 2 cột
 * - Mobile: 1 cột
 *
 * Hoàn toàn tự chứa (chỉ cần truyền `items`), có thể tái sử dụng ở
 * bất kỳ đâu cần hiển thị danh sách tin dạng lưới.
 */
export default function LatestNews({
  items,
  title = 'Tin mới nhất',
  subtitle = 'Cập nhật liên tục từ nhiều nguồn báo',
  isLoading = false,
  skeletonCount = 6,
}: LatestNewsProps) {
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      {(title || subtitle) && (
        <div className="mb-6">
          {title && <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{title}</h2>}
          {subtitle && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: skeletonCount }).map((_, i) => (
            <CardSkeleton key={i} variant="grid" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="text-sm text-slate-500 dark:text-slate-400">Không có bài báo nào để hiển thị.</p>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <LatestNewsCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </section>
  )
}

/* ----------------------------- Sub-component ------------------------------ */

function LatestNewsCard({ item }: { item: NewsItem }) {
  function handleClick() {
    if (item.url) {
      window.open(item.url, '_blank')
    }
  }

  return (
    <article
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') handleClick()
      }}
      className="group flex cursor-pointer flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
    >
      <div className="aspect-[16/10] w-full overflow-hidden bg-slate-100 dark:bg-slate-700">
        <img
          src={item.image ?? FALLBACK_IMAGE}
          alt={item.title ?? 'Ảnh bài báo'}
          loading="lazy"
          className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
        />
      </div>

      <div className="flex flex-1 flex-col p-5">
        {item.source && (
          <span className="mb-3 inline-flex w-fit items-center rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-400">
            {item.source}
          </span>
        )}

        <h3 className="text-base font-semibold leading-snug text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
          {item.title ?? 'Không có tiêu đề'}
        </h3>

        {item.summary && (
          <p className="mt-2 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">{item.summary}</p>
        )}

        <div className="mt-3 text-xs text-slate-400 dark:text-slate-500">{formatDate(item.publish_date)}</div>

        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation()
            handleClick()
          }}
          className="mt-4 inline-flex w-fit items-center gap-1.5 rounded-full border border-indigo-200 px-4 py-2 text-sm font-medium text-indigo-600 transition hover:bg-indigo-600 hover:text-white dark:border-indigo-500/40 dark:text-indigo-400 dark:hover:bg-indigo-500 dark:hover:text-white"
        >
          Đọc tiếp
          <svg
            className="h-4 w-4 transition-transform group-hover:translate-x-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M13 6l6 6-6 6" />
          </svg>
        </button>
      </div>
    </article>
  )
}
