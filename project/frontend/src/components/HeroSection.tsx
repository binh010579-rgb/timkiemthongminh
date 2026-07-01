import SearchBar from './SearchBar'

interface HeroSectionProps {
  onSearch: (query: string) => void
  isSearching?: boolean
}

/**
 * Hero Section của Home Page: tiêu đề, subtitle và thanh tìm kiếm lớn.
 * Phong cách lấy cảm hứng từ Google AI / ChatGPT / Apple:
 * background gradient nhẹ, các khối blur trôi nổi, card nổi (glass) chứa search bar.
 * Chỉ dùng Tailwind + CSS thuần (xem keyframes trong index.css), không dùng thư viện animation ngoài.
 */
export default function HeroSection({ onSearch, isSearching }: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden bg-white px-4 py-20 sm:py-28 dark:bg-slate-900">
      {/* Background gradient nhẹ */}
      <div className="absolute inset-0 -z-20 bg-gradient-to-b from-indigo-50 via-white to-white dark:from-indigo-950/40 dark:via-slate-900 dark:to-slate-900" />

      {/* Các khối blur trôi nổi (pure CSS, không dùng thư viện ngoài) */}
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <div className="animate-float-slow absolute -top-24 left-1/4 h-72 w-72 -translate-x-1/2 rounded-full bg-indigo-300/30 blur-3xl sm:h-96 sm:w-96 dark:bg-indigo-500/20" />
        <div className="animate-float-slow-reverse absolute -top-10 right-0 h-64 w-64 translate-x-1/4 rounded-full bg-fuchsia-200/30 blur-3xl sm:h-80 sm:w-80 dark:bg-fuchsia-500/15" />
        <div className="animate-float-slow absolute bottom-[-6rem] left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-sky-200/30 blur-3xl sm:h-96 sm:w-96 dark:bg-sky-500/15" />
      </div>

      <div className="mx-auto max-w-4xl text-center">
        <span className="mb-5 inline-flex items-center gap-2 rounded-full border border-slate-200/80 bg-white/70 px-4 py-1.5 text-xs font-medium text-slate-600 backdrop-blur-sm dark:border-slate-700/80 dark:bg-slate-800/70 dark:text-slate-300">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
          Được hỗ trợ bởi AI
        </span>

        <h1 className="text-balance text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl md:text-6xl dark:text-white">
          Tìm kiếm tin tức{' '}
          <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-500 bg-clip-text text-transparent">
            thông minh
          </span>{' '}
          bằng AI
        </h1>

        <p className="mx-auto mt-5 max-w-2xl text-pretty text-base text-slate-500 sm:text-lg dark:text-slate-400">
          Khám phá hàng nghìn bài báo được tổng hợp và tìm kiếm bằng công nghệ
          semantic search — nhanh chóng, chính xác và đúng ý bạn cần.
        </p>

        {/* Card nổi chứa thanh tìm kiếm — hiệu ứng glass + shadow nổi */}
        <div className="mx-auto mt-10 max-w-2xl rounded-3xl border border-white/60 bg-white/60 p-3 shadow-[0_8px_40px_rgba(79,70,229,0.12)] backdrop-blur-xl sm:p-4 dark:border-slate-700/60 dark:bg-slate-800/60 dark:shadow-[0_8px_40px_rgba(0,0,0,0.4)]">
          <SearchBar onSearch={onSearch} isLoading={isSearching} />
        </div>

        <p className="mt-4 text-xs text-slate-400 dark:text-slate-500">
          Thử tìm: "trí tuệ nhân tạo", "kinh tế Việt Nam", "thể thao hôm nay"...
        </p>
      </div>
    </section>
  )
}
