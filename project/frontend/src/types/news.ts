// Types khớp với api/schemas.py (backend FastAPI)

export interface NewsItem {
  id: number
  title?: string | null
  publish_date?: string | null
  author?: string | null
  source?: string | null
  url?: string | null
  comments?: number | null
  summary?: string | null
  image?: string | null
}

export interface NewsList {
  total: number
  page: number
  limit: number
  total_pages: number
  items: NewsItem[]
}

export interface CategoryItem {
  name: string
  count: number
}

export interface CategoriesList {
  total: number
  items: CategoryItem[]
}

export interface SearchResult {
  query: string
  total: number
  page: number
  limit: number
  total_pages: number
  items: NewsItem[]
}
