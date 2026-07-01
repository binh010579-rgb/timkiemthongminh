/**
 * Client gọi backend FastAPI.
 *
 * Backend trả JSON có cấu trúc khớp 1-1 với các type trong `types/news.ts`
 * (NewsList, CategoriesList, SearchResult), nên không cần lớp mapping
 * trung gian như khi còn đọc file JSON tĩnh.
 */

// Có thể override qua biến môi trường Vite (VITE_API_BASE_URL) khi deploy.
const API_BASE_URL =
  (import.meta as ImportMeta & { env?: { VITE_API_BASE_URL?: string } }).env
    ?.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`)
  if (!res.ok) {
    throw new Error(`API lỗi (HTTP ${res.status}) khi gọi ${path}`)
  }
  return (await res.json()) as T
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    throw new Error(`API lỗi (HTTP ${res.status}) khi gọi ${path}`)
  }
  return (await res.json()) as T
}
