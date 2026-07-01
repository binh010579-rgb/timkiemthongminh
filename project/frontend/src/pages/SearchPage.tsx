import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import SearchBar from '../components/SearchBar'
import LatestNews from '../components/LatestNews'
import TrendingTopics from '../components/TrendingTopics'
import Footer from '../components/Footer'
import { searchNews } from '../services/newsService'
import type { NewsItem } from '../types/news'

/**
 * Trang tìm kiếm theo chủ đề / từ khóa (route: /search?q=...).
 * Được điều hướng tới từ TrendingTopics (chip chủ đề) hoặc thanh tìm kiếm.
 * Dùng API Search ngữ nghĩa (POST /search ở backend, qua services/newsService.ts)
 * — không còn dữ liệu mock.
 */
export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const query = searchParams.get('q') ?? ''

  const [items, setItems] = useState<NewsItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    if (!query.trim()) {
      setItems([])
      return
    }

    let cancelled = false
    setIsLoading(true)
    setHasError(false)

    searchNews(query, 1, 12)
      .then((result) => {
        if (cancelled) return
        setItems(result.items)
      })
      .catch(() => {
        if (cancelled) return
        setItems([])
        setHasError(true)
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [query])

  function handleSearch(newQuery: string) {
    setSearchParams({ q: newQuery })
  }

  return (
    <div className="flex min-h-screen flex-col bg-white dark:bg-slate-900">
      <section className="border-b border-slate-100 bg-gradient-to-b from-indigo-50 via-white to-white px-4 py-10 sm:py-14 dark:border-slate-800 dark:from-indigo-950/40 dark:via-slate-900 dark:to-slate-900">
        <div className="mx-auto max-w-4xl text-center">
          <Link
            to="/"
            className="mb-4 inline-flex items-center gap-1 text-sm font-medium text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 17l-5-5 5-5M18 12H6" />
            </svg>
            Về trang chủ
          </Link>

          <h1 className="text-2xl font-semibold text-slate-900 sm:text-3xl dark:text-white">
            Kết quả tìm kiếm{query && <>: "{query}"</>}
          </h1>

          <div className="mt-6">
            <SearchBar onSearch={handleSearch} isLoading={isLoading} />
          </div>

          <div className="mt-6">
            <TrendingTopics />
          </div>
        </div>
      </section>

      {!query.trim() ? (
        <p className="mx-auto max-w-6xl px-4 py-16 text-center text-sm text-slate-500 dark:text-slate-400">
          Nhập từ khóa hoặc chọn một chủ đề thịnh hành để bắt đầu tìm kiếm.
        </p>
      ) : (
        <LatestNews
          items={items}
          isLoading={isLoading}
          title=""
          subtitle={
            !isLoading && items.length === 0
              ? hasError
                ? 'Không thể kết nối tới máy chủ tìm kiếm, vui lòng thử lại sau.'
                : 'Không tìm thấy kết quả phù hợp, vui lòng thử từ khóa khác.'
              : undefined
          }
        />
      )}

      <Footer />
    </div>
  )
}
