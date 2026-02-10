<template>
  <!-- Shepherd renders its own modal overlay, no template needed -->
  <div></div>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import Shepherd from 'shepherd.js'
import 'shepherd.js/dist/css/shepherd.css'

const props = defineProps({
  active: { type: Boolean, default: false },
})

const emit = defineEmits(['load-template', 'tour-complete', 'start-tour', 'open-backtest'])

let tour = null

function createTour() {
  tour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      classes: 'shepherd-theme-custom',
      scrollTo: { behavior: 'smooth', block: 'center' },
      cancelIcon: { enabled: true },
      modalOverlayOpeningPadding: 12,
      modalOverlayOpeningRadius: 10,
      popperOptions: {
        modifiers: [
          { name: 'offset', options: { offset: [0, 20] } },
          { name: 'preventOverflow', options: { padding: 20 } },
          { name: 'flip', options: { fallbackPlacements: ['right', 'left', 'top', 'bottom'] } },
        ],
      },
    },
  })

  // Step 1: Welcome (read)
  tour.addStep({
    id: 'welcome',
    title: 'Welcome to PineBack',
    text: `
      <p class="mb-2">This interactive tutorial walks you through building a trading strategy and running a backtest.</p>
      <p class="text-sm opacity-70">You will perform each action yourself. Takes about 3 minutes.</p>
      <p class="text-xs opacity-40 mt-3">Step 1 of 12</p>
    `,
    buttons: [
      { text: 'Start Tour →', action: tour.next, classes: 'shepherd-button-primary' },
    ],
  })

  // Step 2: Open template dropdown (action)
  tour.addStep({
    id: 'open-template',
    title: 'Load a Strategy Template',
    text: `
      <p>Click this dropdown to see 12 pre-built strategy templates.</p>
      <p class="text-xs opacity-40 mt-2">Step 2 of 12 · Click the button to continue</p>
    `,
    attachTo: { element: '#template-dropdown', on: 'bottom' },
    advanceOn: { selector: '#template-dropdown button', event: 'click' },
    buttons: [],
  })

  // Step 3: Select MACD (action) — advanced programmatically from BacktestApp.loadTemplate()
  tour.addStep({
    id: 'select-template',
    title: 'Select MACD Crossover',
    text: `
      <p>Click <strong>"MACD Crossover"</strong> from the list to load it into the builder.</p>
      <p class="text-xs opacity-40 mt-2">Step 3 of 12 · Click a template to continue</p>
    `,
    attachTo: { element: '#template-dropdown', on: 'bottom' },
    buttons: [],
  })

  // Step 4: Click Long Exit tab (action)
  tour.addStep({
    id: 'click-long-exit',
    title: 'Explore Signal Conditions',
    text: `
      <p>The strategy now has Long Entry and Long Exit conditions loaded.</p>
      <p class="mt-1">Click the <strong>"Long Exit"</strong> tab to see its exit conditions.</p>
      <p class="text-xs opacity-40 mt-2">Step 4 of 12 · Click the tab to continue</p>
    `,
    attachTo: { element: '[data-signal="longExit"]', on: 'bottom' },
    advanceOn: { selector: '[data-signal="longExit"]', event: 'click' },
    buttons: [],
  })

  // Step 5: Inspect condition (read)
  tour.addStep({
    id: 'inspect-condition',
    title: 'Understanding Conditions',
    text: `
      <p>Each condition has three parts:</p>
      <ul class="list-disc list-inside mt-1 space-y-1 text-sm">
        <li><strong>Left operand</strong> — an indicator or price</li>
        <li><strong>Operator</strong> — crossover, crossunder, >, <, etc.</li>
        <li><strong>Right operand</strong> — another indicator, constant, or variable</li>
      </ul>
      <p class="mt-2 text-sm opacity-70">Here, <em>macdLine crossunder signalLine</em> triggers a long exit.</p>
      <p class="text-xs opacity-40 mt-2">Step 5 of 12</p>
    `,
    attachTo: { element: '.condition-row', on: 'bottom' },
    buttons: [
      { text: '← Back', action: tour.back, classes: 'shepherd-button-secondary' },
      { text: 'Next →', action: tour.next, classes: 'shepherd-button-primary' },
    ],
  })

  // Step 6: Click Variables tab (action)
  tour.addStep({
    id: 'click-variables',
    title: 'Custom Variables',
    text: `
      <p>Click the <strong>"Variables"</strong> tab to see the indicators used by this strategy.</p>
      <p class="text-xs opacity-40 mt-2">Step 6 of 12 · Click the tab to continue</p>
    `,
    attachTo: { element: '[data-tab="variables"]', on: 'bottom' },
    advanceOn: { selector: '[data-tab="variables"]', event: 'click' },
    buttons: [],
  })

  // Step 7: Inspect variables (read)
  tour.addStep({
    id: 'inspect-variables',
    title: 'Strategy Variables',
    text: `
      <p>This strategy defines MACD indicator outputs as reusable variables.</p>
      <p class="mt-1 text-sm opacity-70">Variables can be indicators, price data, or math expressions. They're referenced in conditions.</p>
      <p class="text-xs opacity-40 mt-2">Step 7 of 12</p>
    `,
    attachTo: { element: '[data-tab="variables"]', on: 'bottom' },
    buttons: [
      { text: '← Back', action: tour.back, classes: 'shepherd-button-secondary' },
      { text: 'Next →', action: tour.next, classes: 'shepherd-button-primary' },
    ],
  })

  // Step 8: Click Backtest button (action)
  tour.addStep({
    id: 'click-backtest',
    title: 'Backtest Configuration',
    text: `
      <p>Click the <strong>"Backtest"</strong> button to open the configuration panel.</p>
      <p class="text-xs opacity-40 mt-2">Step 8 of 12 · Click to continue</p>
    `,
    attachTo: { element: '[data-tab="backtest"]', on: 'bottom' },
    advanceOn: { selector: '[data-tab="backtest"]', event: 'click' },
    buttons: [],
  })

  // Step 9: Select timeframe (action or skip)
  tour.addStep({
    id: 'select-timeframe',
    title: 'Select Timeframe',
    text: `
      <p>Select a timeframe for your backtest. Try <strong>"1 Hour"</strong> for a good balance of speed and detail.</p>
      <p class="text-xs opacity-40 mt-2">Step 9 of 12 · Change the timeframe or click Next</p>
    `,
    attachTo: { element: '#timeframe-select', on: 'left' },
    advanceOn: { selector: '#timeframe-select', event: 'change' },
    buttons: [
      { text: 'Next →', action: tour.next, classes: 'shepherd-button-primary' },
    ],
  })

  // Step 10: Set dates (action with conditional Next)
  tour.addStep({
    id: 'set-dates',
    title: 'Set Date Range',
    text: `
      <p>Enter a date range (e.g., <strong>2015-01-01</strong> to <strong>2020-12-31</strong>).</p>
      <p class="mt-1 text-sm opacity-70">Notice the <em>Magnifier</em> toggle — when ON, the backtest uses intra-bar fills for more realistic results.</p>
      <p class="text-xs opacity-40 mt-2">Step 10 of 12 · Fill both dates, then click Next</p>
    `,
    attachTo: { element: '#date-range-inputs', on: 'left' },
    buttons: [
      { text: '← Back', action: tour.back, classes: 'shepherd-button-secondary' },
      { text: 'Next →', action: tour.next, classes: 'shepherd-button-primary' },
    ],
  })

  // Step 11: Run Backtest (action)
  tour.addStep({
    id: 'run-backtest',
    title: 'Run Your Backtest!',
    text: `
      <p>Everything is configured. Click <strong>"Run Backtest"</strong> to submit!</p>
      <p class="mt-1 text-sm opacity-70">The system will compile your PineScript, load SPY data, and run the backtest with progress tracking.</p>
      <p class="text-xs opacity-40 mt-2">Step 11 of 12 · Click Run Backtest to continue</p>
    `,
    attachTo: { element: '#run-backtest-btn', on: 'left' },
    advanceOn: { selector: '#run-backtest-btn', event: 'click' },
    buttons: [],
  })

  // Step 12: View Results (action)
  tour.addStep({
    id: 'view-results',
    title: 'Watch Progress & View Results',
    text: `
      <p>Your backtest is running! Watch the progress bar below.</p>
      <p class="mt-1">When it completes, click <strong>"View Results"</strong> to see the full report including:</p>
      <ul class="list-disc list-inside mt-1 space-y-0.5 text-sm opacity-70">
        <li>Performance Summary (Sharpe, return, drawdown...)</li>
        <li>OHLCV chart with trade entry/exit markers</li>
        <li>TradingView-style trade list</li>
      </ul>
      <p class="text-xs opacity-40 mt-2">Step 12 of 12 · Click View Results when the backtest completes</p>
    `,
    buttons: [
      { text: 'Finish Tour', action: tour.complete, classes: 'shepherd-button-primary' },
    ],
  })

  tour.on('complete', () => {
    localStorage.setItem('tour_completed', 'true')
    emit('tour-complete')
  })

  tour.on('cancel', () => {
    localStorage.setItem('tour_completed', 'true')
  })
}

function startTour() {
  if (tour) {
    tour.cancel()
  }
  createTour()
  tour.start()
}

function advanceIfActive() {
  if (tour && tour.isActive()) {
    tour.next()
  }
}

onMounted(() => {
  // Auto-start on first visit
  const completed = localStorage.getItem('tour_completed')
  if (!completed) {
    // Small delay to let the UI render
    setTimeout(() => startTour(), 500)
  }
})

onUnmounted(() => {
  if (tour) {
    tour.cancel()
    tour = null
  }
})

// Allow parent to trigger
watch(() => props.active, (val) => {
  if (val) startTour()
})

defineExpose({ startTour, advanceIfActive })
</script>

<style>
/* ─────────────────────────────────────────────────────────────
   DARK THEME + STRONG SPOTLIGHT overrides for Shepherd.js
   Must use !important to override shepherd's default styles
   ───────────────────────────────────────────────────────────── */

/* ── Tooltip container ───────────────────────────────────── */
.shepherd-element {
  z-index: 9999 !important;
  max-width: 400px !important;
  background: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

/* Kill ALL white borders from shepherd internals */
.shepherd-element,
.shepherd-element *,
.shepherd-element *::before,
.shepherd-element *::after {
  border-color: transparent !important;
}

/* ── Content card ────────────────────────────────────────── */
.shepherd-element .shepherd-content {
  background: #0e1120 !important;
  border: 1px solid rgba(99, 102, 241, 0.25) !important;
  outline: none !important;
  border-radius: 14px !important;
  box-shadow:
    0 0 0 1px rgba(99, 102, 241, 0.15),
    0 24px 60px rgba(0, 0, 0, 0.9) !important;
  padding: 0 !important;
}

/* ── Arrow ───────────────────────────────────────────────── */
.shepherd-element .shepherd-arrow:before {
  background: #0e1120 !important;
  border: 1px solid rgba(99, 102, 241, 0.25) !important;
}

/* ── Header ──────────────────────────────────────────────── */
.shepherd-element .shepherd-header {
  background: rgba(99, 102, 241, 0.15) !important;
  border-bottom: 1px solid rgba(99, 102, 241, 0.15) !important;
  padding: 14px 18px !important;
  border-radius: 14px 14px 0 0 !important;
}

.shepherd-element .shepherd-title {
  color: #fff !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  font-family: 'Inter', sans-serif !important;
}

.shepherd-element .shepherd-cancel-icon {
  color: rgba(255, 255, 255, 0.3) !important;
  font-size: 20px !important;
}

.shepherd-element .shepherd-cancel-icon:hover {
  color: rgba(255, 255, 255, 0.7) !important;
}

/* ── Body text ───────────────────────────────────────────── */
.shepherd-element .shepherd-text {
  color: rgba(255, 255, 255, 0.75) !important;
  font-size: 13px !important;
  line-height: 1.7 !important;
  padding: 16px 18px !important;
  font-family: 'Inter', sans-serif !important;
}

.shepherd-element .shepherd-text p {
  margin: 0 0 8px !important;
}

/* ── Footer / buttons ────────────────────────────────────── */
.shepherd-element .shepherd-footer {
  padding: 0 18px 16px !important;
  border-top: none !important;
}

.shepherd-element .shepherd-button {
  border-radius: 8px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  font-family: 'Inter', sans-serif !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
}

.shepherd-button-primary {
  background: #6366f1 !important;
  color: #fff !important;
  border: none !important;
  padding: 9px 22px !important;
}

.shepherd-button-primary:hover {
  background: #4f46e5 !important;
}

.shepherd-button-secondary {
  background: rgba(255, 255, 255, 0.06) !important;
  color: rgba(255, 255, 255, 0.6) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  padding: 8px 16px !important;
}

.shepherd-button-secondary:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #fff !important;
}

/* ─────────────────────────────────────────────────────────
   SPOTLIGHT: Extremely dark overlay with bright glow
   NOTE: .shepherd-modal-overlay-container IS the SVG itself
   (not a wrapper). Default opacity is 0.5 — we override to 1
   and control darkness via the path fill.
   ───────────────────────────────────────────────────────── */

/* Overlay SVG z-index */
.shepherd-modal-overlay-container {
  z-index: 9998 !important;
}

/* Override default 0.5 opacity to full — let fill control darkness */
.shepherd-modal-overlay-container.shepherd-modal-is-visible {
  opacity: 1 !important;
}

/* SVG path fill — near-black overlay (0.85 = very dark) */
.shepherd-modal-overlay-container path {
  fill: rgba(0, 0, 0, 0.85) !important;
  fill-rule: evenodd !important;
}

/* ── Target highlight — bright animated glow ──────────── */
.shepherd-has-active-tour .shepherd-target {
  position: relative;
  z-index: 9999 !important;
  box-shadow:
    0 0 0 3px rgba(99, 102, 241, 0.6),
    0 0 20px 6px rgba(99, 102, 241, 0.35),
    0 0 40px 12px rgba(99, 102, 241, 0.15) !important;
  border-radius: 8px;
  animation: shepherd-pulse 2s ease-in-out infinite !important;
}

@keyframes shepherd-pulse {
  0%, 100% {
    box-shadow:
      0 0 0 3px rgba(99, 102, 241, 0.6),
      0 0 20px 6px rgba(99, 102, 241, 0.35),
      0 0 40px 12px rgba(99, 102, 241, 0.15);
  }
  50% {
    box-shadow:
      0 0 0 4px rgba(99, 102, 241, 0.8),
      0 0 30px 10px rgba(99, 102, 241, 0.45),
      0 0 50px 16px rgba(99, 102, 241, 0.2);
  }
}
</style>
