import { useQuery } from '@tanstack/react-query'
import { fetchFeaturedNews } from '../services/featuredNewsService'
import type { NewsItem } from '../types/news'

/**
 * Lấy danh sách tin nổi bật từ backend (GET /api/news/featured).
 */
export function useFeaturedNews(limit = 5) {
  const query = useQuery({
    queryKey: ['news', 'featured', limit],
    queryFn: () => fetchFeaturedNews(limit),
  })

  const items: NewsItem[] = query.data?.items ?? []

  return {
    items,
    isLoading: query.isLoading,
    isError: query.isError,
  }
}
