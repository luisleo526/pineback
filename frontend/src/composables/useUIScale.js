/**
 * Global UI scale composable.
 *
 * Uses CSS `zoom` on #app to uniformly scale everything —
 * text, padding, icons, borders, spacing, charts.
 * Applied to #app (not <html>) so that overlay libraries like
 * Shepherd.js keep correct getBoundingClientRect() coordinates.
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
  const el = document.getElementById('app')
  if (el) {
    el.style.zoom = String(value)
  }
}

const scale = ref(loadScale())

// Apply immediately if #app exists, otherwise defer to DOMContentLoaded
applyZoom(scale.value)
if (!document.getElementById('app')) {
  document.addEventListener('DOMContentLoaded', () => applyZoom(scale.value), { once: true })
}

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
