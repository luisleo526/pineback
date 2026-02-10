/**
 * API client for the backtest server.
 *
 * All endpoints are relative to /api (proxied by Vite dev server to localhost:8000).
 */

const BASE = '/api'

async function request(path, options = {}) {
  const url = `${BASE}${path}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const message = body.detail || `HTTP ${res.status}`
    throw new Error(message)
  }

  return res.json()
}

// ── Backtests ─────────────────────────────────────────────────

export async function submitBacktest(payload) {
  return request('/backtests', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function getBacktest(id) {
  return request(`/backtests/${id}`)
}

export async function listBacktests() {
  return request('/backtests')
}

// ── Symbols & Strategies ────────────────────────────────────

export async function getSymbols() {
  return request('/symbols')
}

export async function getStrategies() {
  return request('/strategies')
}

export async function compilePinescript(pinescript) {
  return request('/compile', {
    method: 'POST',
    body: JSON.stringify({ pinescript }),
  })
}

// ── Health ───────────────────────────────────────────────────

export async function healthCheck() {
  return request('/health')
}
