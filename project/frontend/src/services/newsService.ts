import type { NewsItem, NewsList, CategoriesList, SearchResult } from '../types/news'
import { apiGet, apiPost } from './apiClient'

/**
 * Service layer cho resource "news".
 *
 * Gọi trực tiếp backend FastAPI (đọc dữ liệu từ CSV, giữ trong RAM —
 * xem thư mục `backend/`). Chữ ký hàm giữ nguyên như trước để các
 * hook/component gọi chúng không cần thay đổi.
 */

export async function fetchNewsList(page = 1, limit = 10): Promise<NewsList> {
  return apiGet<NewsList>(`/api/news?page=${page}&limit=${limit}`)
}

export async function fetchCategories(): Promise<CategoriesList> {
  return apiGet<CategoriesList>('/api/categories')
}

/** Hình dạng response thô từ backend POST /search (Search Pipeline). */
interface SearchPipelineApiItem {
  id: number
  title: string | null
  summary: string | null
  content: string | null
  url: string | null
  image: string | null
  date: string | null
  source: string | null
  score: number
}

/**
 * Tìm kiếm tin tức bằng Search Pipeline (POST /search): embedding query ->
 * Qdrant search -> top kết quả -> content đầy đủ lấy từ database.
 *
 * Backend trả cố định top SEARCH_TOP_K (5), không phân trang, nên
 * `page`/`limit` được giữ lại trong chữ ký hàm để không phải sửa nơi gọi
 * (SearchPage), nhưng không còn tác dụng phân trang thực sự.
 */
export async function searchNews(
  query: string,
  _page = 1,
  limit = 10,
): Promise<SearchResult> {
  const trimmed = query.trim()
  if (!trimmed) {
    return { query, total: 0, page: 1, limit, total_pages: 1, items: [] }
  }

  const results = await apiPost<SearchPipelineApiItem[]>('/search', { query: trimmed })

  const items: NewsItem[] = results.map((r) => ({
    id: r.id,
    title: r.title,
    publish_date: r.date,
    author: null,
    source: r.source,
    url: r.url,
    comments: null,
    summary: r.summary,
    image: r.image,
  }))

  return {
    query,
    total: items.length,
    page: 1,
    limit: items.length || limit,
    total_pages: 1,
    items,
  }
}
