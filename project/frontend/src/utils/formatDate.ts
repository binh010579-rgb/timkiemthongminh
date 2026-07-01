/**
 * Định dạng ngày tháng kiểu Việt Nam (dd/mm/yyyy).
 * Trả về chuỗi rỗng nếu không có giá trị hoặc không parse được.
 */
export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return dateStr
  return d.toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}
