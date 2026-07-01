import type { NewsItem } from '../types/news'

interface NewsCardProps {
  news: NewsItem
  variant?: 'featured' | 'default'
}

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}

/**
 * Thẻ hiển thị một bài báo. Dùng chung cho các section
 * "Tin nổi bật" và "Tin mới nhất" trên Home Page (và có thể
 * tái sử dụng cho trang danh sách / tìm kiếm sau này).
 */
export default function NewsCard({ news, variant = 'default' }: NewsCardProps) {
  const isFeatured = variant === 'featured'

  function handleClick() {
    if (news.url) {
      window.open(news.url, '_blank')
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
      className={`group flex cursor-pointer flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-700 dark:bg-slate-800 ${
        isFeatured ? 'h-full' : ''
      }`}
    >
      {news.source && (
        <span className="mb-3 inline-flex w-fit items-center rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-400">
          {news.source}
        </span>
      )}

      <h3
        className={`font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400 ${
          isFeatured ? 'text-lg leading-snug' : 'text-base leading-snug'
        }`}
      >
        {news.title ?? 'Không có tiêu đề'}
      </h3>

      {news.summary && (
        <p className="mt-2 line-clamp-3 text-sm text-slate-500 dark:text-slate-400">{news.summary}</p>
      )}

      <div className="mt-4 flex items-center justify-between text-xs text-slate-400 dark:text-slate-500">
        <span>{news.author ?? 'Ẩn danh'}</span>
        <span>{formatDate(news.publish_date)}</span>
      </div>
    </div>
  )
}
