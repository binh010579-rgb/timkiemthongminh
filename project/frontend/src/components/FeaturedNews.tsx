import type { NewsItem } from '../types/news'
import { formatDate } from '../utils/formatDate'
import CardSkeleton from './CardSkeleton'

interface FeaturedNewsProps {
  /** Bài đầu tiên sẽ hiển thị lớn bên trái, 4 bài tiếp theo hiển thị nhỏ bên phải. */
  items: NewsItem[]
  title?: string
  subtitle?: string
  isLoading?: boolean
}

const FALLBACK_IMAGE =
  'https://images.unsplash.com/photo-1495020689067-958852a7765e?w=900&h=600&fit=crop'

/**
 * Component "Tin nổi bật": 1 bài lớn bên trái + 4 bài nhỏ bên phải.
 * Hoàn toàn tự chứa (chỉ cần truyền `items`), có thể tái sử dụng ở
 * bất kỳ đâu cần bố cục featured (Home Page, trang chuyên mục, v.v.).
 */
export default function FeaturedNews({
  items,
  title = 'Tin nổi bật',
  subtitle = 'Những bài viết được quan tâm nhiều nhất',
  isLoading = false,
}: FeaturedNewsProps) {
  const mainItem = items[0]
  const sideItems = items.slice(1, 5)

  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      {(title || subtitle) && (
        <div className="mb-6">
          {title && <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{title}</h2>}
          {subtitle && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
        </div>
      )}

      {isLoading ? (
        <FeaturedNewsSkeleton />
      ) : !mainItem ? (
        <p className="text-sm text-slate-500 dark:text-slate-400">Không có bài báo nào để hiển thị.</p>
      ) : (
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          <MainCard item={mainItem} />

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
            {sideItems.map((item) => (
              <SideCard key={item.id} item={item} />
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

/* ----------------------------- Sub-components ---------------------------- */

function MainCard({ item }: { item: NewsItem }) {
  function handleClick() {
    if (item.url) {
      window.open(item.url, '_blank')
    }
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') handleClick()
      }}
      className="group flex cursor-pointer flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg dark:border-slate-700 dark:bg-slate-800"
    >
      <div className="aspect-[16/10] w-full overflow-hidden bg-slate-100 dark:bg-slate-700">
        <img
          src={item.image ?? FALLBACK_IMAGE}
          alt={item.title ?? 'Ảnh bài báo'}
          loading="lazy"
          className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
        />
      </div>

      <div className="flex flex-1 flex-col p-5 sm:p-6">
        {item.source && (
          <span className="mb-3 inline-flex w-fit items-center rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-400">
            {item.source}
          </span>
        )}

        <h3 className="text-xl font-semibold leading-snug text-slate-900 group-hover:text-indigo-600 sm:text-2xl dark:text-white dark:group-hover:text-indigo-400">
          {item.title ?? 'Không có tiêu đề'}
        </h3>

        {item.summary && (
          <p className="mt-3 line-clamp-3 text-sm text-slate-500 sm:text-base dark:text-slate-400">
            {item.summary}
          </p>
        )}

        <div className="mt-auto flex items-center justify-between pt-5 text-xs text-slate-400 dark:text-slate-500">
          <span>{item.author ?? 'Ẩn danh'}</span>
          <span>{formatDate(item.publish_date)}</span>
        </div>
      </div>
    </div>
  )
}

function SideCard({ item }: { item: NewsItem }) {
  function handleClick() {
    if (item.url) {
      window.open(item.url, '_blank')
    }
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') handleClick()
      }}
      className="group flex cursor-pointer gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
    >
      <div className="h-20 w-24 shrink-0 overflow-hidden rounded-lg bg-slate-100 dark:bg-slate-700">
        <img
          src={item.image ?? FALLBACK_IMAGE}
          alt={item.title ?? 'Ảnh bài báo'}
          loading="lazy"
          className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
        />
      </div>

      <div className="flex min-w-0 flex-1 flex-col">
        <h4 className="line-clamp-2 text-sm font-semibold leading-snug text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
          {item.title ?? 'Không có tiêu đề'}
        </h4>
        {item.summary && (
          <p className="mt-1 line-clamp-1 text-xs text-slate-500 dark:text-slate-400">{item.summary}</p>
        )}
        <span className="mt-auto pt-1 text-xs text-slate-400 dark:text-slate-500">
          {formatDate(item.publish_date)}
        </span>
      </div>
    </div>
  )
}

function FeaturedNewsSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
      <CardSkeleton variant="grid" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} variant="row" />
        ))}
      </div>
    </div>
  )
}
