import type { NewsItem } from '../types/news'
import NewsCard from './NewsCard'
import CardSkeleton from './CardSkeleton'

interface NewsSectionProps {
  title: string
  subtitle?: string
  items: NewsItem[]
  variant?: 'featured' | 'default'
  isLoading?: boolean
}

/**
 * Section hiển thị một lưới tin bài, dùng chung cho
 * "Tin nổi bật", "Tin mới nhất" và kết quả tìm kiếm trên Home Page.
 */
export default function NewsSection({
  title,
  subtitle,
  items,
  variant = 'default',
  isLoading = false,
}: NewsSectionProps) {
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{title}</h2>
        {subtitle && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <CardSkeleton key={i} variant="grid" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="text-sm text-slate-500 dark:text-slate-400">Không có bài báo nào để hiển thị.</p>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <NewsCard key={item.id} news={item} variant={variant} />
          ))}
        </div>
      )}
    </section>
  )
}
