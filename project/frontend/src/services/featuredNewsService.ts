import type { NewsList } from '../types/news'
import { apiGet } from './apiClient'

/**
 * Service riêng cho "Featured News".
 * Gọi endpoint /api/news/featured của backend FastAPI.
 */
export async function fetchFeaturedNews(limit = 5): Promise<NewsList> {
  return apiGet<NewsList>(`/api/news/featured?limit=${limit}`)
}
