import { useState } from 'react'
import type { FormEvent } from 'react'

interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  isLoading?: boolean
}

/**
 * Thanh tìm kiếm lớn dùng trong Hero Section.
 * Tách riêng để có thể tái sử dụng ở trang kết quả tìm kiếm sau này.
 */
export default function SearchBar({
  onSearch,
  placeholder = 'Nhập từ khóa bạn muốn tìm kiếm...',
  isLoading = false,
}: SearchBarProps) {
  const [value, setValue] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = value.trim()
    if (trimmed) {
      onSearch(trimmed)
    }
  }

  const [isFocused, setIsFocused] = useState(false)

  return (
    <form
      onSubmit={handleSubmit}
      className={[
        'group mx-auto flex w-full max-w-xl items-center gap-3',
        'rounded-full border bg-white px-5 py-3.5 sm:py-4 dark:bg-slate-800',
        'transition-all duration-200 ease-out',
        isFocused
          ? 'scale-[1.02] border-transparent shadow-[0_2px_14px_rgba(79,70,229,0.18)] ring-2 ring-indigo-500/40'
          : 'border-slate-200 shadow-sm hover:scale-[1.01] hover:border-slate-300 hover:shadow-md dark:border-slate-700 dark:hover:border-slate-600',
      ].join(' ')}
    >
      <svg
        className={`h-5 w-5 shrink-0 transition-colors duration-200 ${
          isFocused ? 'text-indigo-500' : 'text-slate-400 group-hover:text-slate-500 dark:text-slate-500'
        }`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M21 21l-4.35-4.35M17 10.5A6.5 6.5 0 1 1 4 10.5a6.5 6.5 0 0 1 13 0Z"
        />
      </svg>

      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder}
        disabled={isLoading}
        className="w-full min-w-0 bg-transparent text-base text-slate-900 placeholder:text-slate-400 focus:outline-none disabled:cursor-not-allowed dark:text-white dark:placeholder:text-slate-500"
      />

      {isLoading ? (
        <span className="h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
      ) : (
        value && (
          <button
            type="submit"
            aria-label="Tìm kiếm"
            className="shrink-0 rounded-full p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-indigo-600 dark:text-slate-500 dark:hover:bg-slate-700 dark:hover:text-indigo-400"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2.5}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </button>
        )
      )}
    </form>
  )
}
