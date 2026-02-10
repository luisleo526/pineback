/**
 * Formatting utilities for numbers, dates, durations, and financial values.
 *
 * Rules:
 * - Null/NaN/undefined → "—"
 * - Return/PnL: sign + 2 decimals + %  (e.g., "+28.82%")
 * - Dollar: $comma.2dp (e.g., "$12,882.45")
 * - Ratio: 2 decimals (e.g., "2.15")
 * - PnL dollar: sign + $ (e.g., "+$330.83")
 * - Count: integer (e.g., "28")
 * - Duration: human readable (e.g., "3d 4h")
 * - Null metrics: dash "—"
 */

export function formatNull(v) {
  return v == null || (typeof v === 'number' && (isNaN(v) || !isFinite(v)))
}

export function formatPct(v) {
  if (formatNull(v)) return '—'
  const sign = v > 0 ? '+' : ''
  return `${sign}${v.toFixed(2)}%`
}

export function formatDollar(v) {
  if (formatNull(v)) return '—'
  return '$' + v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function formatPnl(v) {
  if (formatNull(v)) return '—'
  const sign = v > 0 ? '+' : v < 0 ? '-' : ''
  return `${sign}$${Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export function formatRatio(v) {
  if (formatNull(v)) return '—'
  return v.toFixed(2)
}

export function formatInt(v) {
  if (formatNull(v)) return '—'
  return v.toLocaleString('en-US')
}

export function formatDate(isoString) {
  if (!isoString) return '—'
  const d = new Date(isoString)
  if (isNaN(d.getTime())) return '—'
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export function formatDateShort(isoString) {
  if (!isoString) return '—'
  const d = new Date(isoString)
  if (isNaN(d.getTime())) return '—'
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

export function formatDuration(durationStr) {
  if (!durationStr || durationStr === 'NaT' || durationStr === 'nan') return '—'
  // Parse pandas Timedelta string like "3 days 04:30:00"
  const match = durationStr.match(/(?:(\d+)\s*days?\s*)?(\d{1,2}):(\d{2}):(\d{2})/)
  if (!match) return durationStr
  const days = parseInt(match[1] || '0')
  const hours = parseInt(match[2])
  const mins = parseInt(match[3])
  const parts = []
  if (days > 0) parts.push(`${days}d`)
  if (hours > 0) parts.push(`${hours}h`)
  if (mins > 0 && days === 0) parts.push(`${mins}m`)
  return parts.length > 0 ? parts.join(' ') : '<1m'
}

/**
 * Color class for financial values.
 * @returns 'text-green-400' | 'text-red-400' | 'text-white/70'
 */
export function pnlColor(v) {
  if (formatNull(v)) return 'text-white/50'
  if (v > 0) return 'text-green-400'
  if (v < 0) return 'text-red-400'
  return 'text-white/70'
}

export function sharpeColor(v) {
  if (formatNull(v)) return 'text-white/50'
  if (v > 1) return 'text-green-400'
  if (v < 0) return 'text-red-400'
  return 'text-white/70'
}

export function winRateColor(v) {
  if (formatNull(v)) return 'text-white/50'
  if (v > 50) return 'text-green-400'
  if (v < 40) return 'text-red-400'
  return 'text-white/70'
}
