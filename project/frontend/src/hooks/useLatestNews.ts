import { useQuery } from '@tanstack/react-query'
import { fetchNewsList } from '../services/newsService'
import type { NewsItem } from '../types/news'

/**
 * Lấy danh sách tin mới nhất từ backend (GET /api/news).
 */
export function useLatestNews(limit = 6) {
  const query = useQuery({
    queryKey: ['news', 'latest', limit],
    queryFn: () => fetchNewsList(1, limit),
  })

  const items: NewsItem[] = query.data?.items ?? []

  return {
    items,
    isLoading: query.isLoading,
    isError: query.isError,
  }
}
