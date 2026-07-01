import { useNavigate } from 'react-router-dom'

interface TrendingTopicsProps {
  topics?: string[]
  title?: string
}

export const DEFAULT_TRENDING_TOPICS = [
  'AI',
  'Blockchain',
  'Game',
  'Kinh tế',
  'Công nghệ',
  'Thể thao',
]

/**
 * Hiển thị danh sách chủ đề thịnh hành dạng chip.
 * Click vào một chip sẽ điều hướng sang trang tìm kiếm theo chủ đề đó
 * (route /search?q=<topic>), không thay đổi logic tìm kiếm hiện có —
 * trang /search tái sử dụng cùng service `searchNews`.
 */
export default function TrendingTopics({
  topics = DEFAULT_TRENDING_TOPICS,
  title = 'Chủ đề thịnh hành',
}: TrendingTopicsProps) {
  const navigate = useNavigate()

  function handleClick(topic: string) {
    navigate(`/search?q=${encodeURIComponent(topic)}`)
  }

  if (topics.length === 0) return null

  return (
    <div className="mx-auto max-w-4xl px-4">
      <div className="flex flex-wrap items-center justify-center gap-2">
        {title && (
          <span className="mr-1 text-sm font-medium text-slate-500 dark:text-slate-400">{title}:</span>
        )}
        {topics.map((topic) => (
          <button
            key={topic}
            type="button"
            onClick={() => handleClick(topic)}
            className="rounded-full border border-slate-200 bg-white px-4 py-1.5 text-sm font-medium text-slate-600 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-600 hover:shadow-md active:translate-y-0 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-indigo-500/50 dark:hover:bg-indigo-500/10 dark:hover:text-indigo-400"
          >
            {topic}
          </button>
        ))}
      </div>
    </div>
  )
}
