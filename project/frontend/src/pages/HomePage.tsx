import { useState } from 'react'
import HeroSection from '../components/HeroSection'
import HeroSkeleton from '../components/HeroSkeleton'
import NewsSection from '../components/NewsSection'
import FeaturedNews from '../components/FeaturedNews'
import LatestNews from '../components/LatestNews'
import TrendingTopics from '../components/TrendingTopics'
import Footer from '../components/Footer'
import { useLatestNews } from '../hooks/useLatestNews'
import { useFeaturedNews } from '../hooks/useFeaturedNews'
import { searchNews } from '../services/newsService'
import type { NewsItem } from '../types/news'

/**
 * Trang chủ (Home Page).
 * Bố cục: Hero (tiêu đề + subtitle + thanh tìm kiếm) -> Tin nổi bật
 * -> Tin mới nhất (hoặc kết quả tìm kiếm nếu người dùng đã tìm) -> Footer.
 *
 * Nguồn dữ liệu:
 * - Latest News: gọi backend FastAPI (GET /api/news) qua hook useLatestNews.
 *   Backend đọc cleaned_news.csv bằng pandas khi khởi động và giữ trong RAM.
 * - Featured News: gọi GET /api/news/featured (top tin theo số bình luận), qua
 *   useFeaturedNews / services/featuredNewsService.ts.
 */
export default function HomePage() {
  const { items: latestNews, isLoading: isLoadingLatest } = useLatestNews(6)
  const { items: featuredNews, isLoading: isLoadingFeatured } = useFeaturedNews(5)

  // Lần tải đầu tiên: hiển thị skeleton cho toàn bộ trang (kể cả Hero)
  // cho tới khi dữ liệu Featured + Latest sẵn sàng lần đầu.
  const isInitialLoading = isLoadingFeatured || isLoadingLatest

  const [searchQuery, setSearchQuery] = useState<string | null>(null)
  const [searchItems, setSearchItems] = useState<NewsItem[]>([])
  const [isSearching, setIsSearching] = useState(false)

  async function handleSearch(query: string) {
    setIsSearching(true)
    setSearchQuery(query)
    try {
      const result = await searchNews(query, 1, 9)
      setSearchItems(result.items)
    } catch {
      // API chưa sẵn sàng / lỗi mạng -> không chặn trải nghiệm người dùng
      setSearchItems([])
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-white dark:bg-slate-900">
      {isInitialLoading ? (
        <HeroSkeleton />
      ) : (
        <HeroSection onSearch={handleSearch} isSearching={isSearching} />
      )}

      <div className="py-6">
        <TrendingTopics />
      </div>

      {searchQuery && (
        <NewsSection
          title={`Kết quả tìm kiếm cho "${searchQuery}"`}
          subtitle={
            !isSearching && searchItems.length === 0
              ? 'Không tìm thấy kết quả phù hợp, vui lòng thử từ khóa khác.'
              : undefined
          }
          items={searchItems}
          isLoading={isSearching}
        />
      )}

      <FeaturedNews items={featuredNews} isLoading={isLoadingFeatured} />

      <LatestNews items={latestNews} isLoading={isLoadingLatest} />

      <Footer />
    </div>
  )
}
