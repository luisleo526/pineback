/**
 * Global UI scale composable.
 *
 * Uses CSS `zoom` on <html> to uniformly scale everything —
 * text, padding, icons, borders, spacing, charts.
 * The chosen scale is persisted in localStorage.
 */

import { ref, watch } from 'vue'

const STORAGE_KEY = 'pineback_ui_scale'
const DEFAULT_SCALE = 1.0
const MIN_SCALE = 0.85
const MAX_SCALE = 1.4
const STEP = 0.05

function loadScale() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored !== null) {
      const val = parseFloat(stored)
      if (!isNaN(val) && val >= MIN_SCALE && val <= MAX_SCALE) return val
    }
  } catch { /* localStorage unavailable */ }
  return DEFAULT_SCALE
}

function applyZoom(value) {
  document.documentElement.style.zoom = String(value)
}

const scale = ref(loadScale())

// Apply immediately on module load
applyZoom(scale.value)

// Reactively sync changes to DOM + localStorage
watch(scale, (val) => {
  applyZoom(val)
  try { localStorage.setItem(STORAGE_KEY, String(val)) } catch { /* noop */ }
})

export function useUIScale() {
  function scaleUp() {
    scale.value = Math.min(MAX_SCALE, +(scale.value + STEP).toFixed(2))
  }

  function scaleDown() {
    scale.value = Math.max(MIN_SCALE, +(scale.value - STEP).toFixed(2))
  }

  function resetScale() {
    scale.value = DEFAULT_SCALE
  }

  return {
    scale,
    scaleUp,
    scaleDown,
    resetScale,
    MIN_SCALE,
    MAX_SCALE,
  }
}
