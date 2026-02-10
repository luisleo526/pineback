<template>
  <div class="p-4 space-y-4">
    <h3 class="text-sm font-semibold text-white flex items-center gap-2">
      <i class="fas fa-flask text-accent-500"></i>
      Backtest Configuration
    </h3>

    <!-- Timeframe -->
    <div>
      <label class="block text-xs text-white/40 mb-1">Timeframe</label>
      <select
        v-model="config.timeframe"
        id="timeframe-select"
        class="w-full bg-dark-800 border border-dark-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
      >
        <option
          v-for="tf in timeframes"
          :key="tf.value"
          :value="tf.value"
        >
          {{ tf.label }}
        </option>
      </select>
    </div>

    <!-- Date Range -->
    <div id="date-range-inputs">
      <div v-if="symbolInfo" class="text-[10px] text-white/25 mb-1.5">
        <i class="fas fa-database mr-1"></i>
        SPY data: {{ symbolInfo.minDate }} to {{ symbolInfo.maxDate }}
      </div>
      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="block text-xs text-white/40 mb-1">Start Date</label>
          <input
            v-model="config.startDate"
            type="date"
            id="date-start"
            required
            class="w-full bg-dark-800 border border-dark-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
            :min="symbolInfo?.minDate"
            :max="symbolInfo?.maxDate"
          />
        </div>
        <div>
          <label class="block text-xs text-white/40 mb-1">End Date</label>
          <input
            v-model="config.endDate"
            type="date"
            id="date-end"
            required
            class="w-full bg-dark-800 border border-dark-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
            :min="symbolInfo?.minDate"
            :max="symbolInfo?.maxDate"
          />
        </div>
      </div>
    </div>

    <!-- Capital + Commission -->
    <div class="grid grid-cols-2 gap-2">
      <div>
        <label class="block text-xs text-white/40 mb-1">Initial Capital ($)</label>
        <input
          v-model.number="config.initialCapital"
          type="number"
          min="100"
          class="w-full bg-dark-800 border border-dark-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
        />
      </div>
      <div>
        <label class="block text-xs text-white/40 mb-1">Commission (%)</label>
        <input
          v-model.number="config.commission"
          type="number"
          min="0"
          step="0.01"
          class="w-full bg-dark-800 border border-dark-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
        />
      </div>
    </div>

    <!-- Slippage -->
    <div>
      <label class="block text-xs text-white/40 mb-1">Slippage (%)</label>
      <input
        v-model.number="config.slippage"
        type="number"
        min="0"
        step="0.01"
        class="w-full bg-dark-800 border border-dark-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
      />
    </div>

    <!-- Magnifier Toggle -->
    <div class="flex items-center justify-between py-2">
      <div>
        <label class="text-xs text-white/70">Magnifier Mode</label>
        <p class="text-[10px] text-white/30 mt-0.5">Realistic intra-bar fill prices</p>
      </div>
      <button
        @click="config.magnifier = !config.magnifier"
        :class="[
          'w-10 h-5 rounded-full transition-colors relative',
          config.magnifier ? 'bg-accent-500' : 'bg-dark-600',
        ]"
      >
        <span
          :class="[
            'absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform',
            config.magnifier ? 'left-5' : 'left-0.5',
          ]"
        ></span>
      </button>
    </div>

    <!-- Dynamic Strategy Parameter Overrides -->
    <div v-if="Object.keys(discoveredParams).length > 0" class="space-y-2">
      <div class="text-xs text-white/40 font-medium pt-2 border-t border-white/[0.04]">
        Strategy Parameters
      </div>
      <div v-for="(info, key) in discoveredParams" :key="key">
        <label class="block text-xs text-white/40 mb-1">{{ info.title || key }}</label>
        <input
          v-model.number="paramOverrides[key]"
          type="number"
          :step="info.type === 'float' ? '0.1' : '1'"
          :min="info.minval"
          :max="info.maxval"
          :placeholder="String(info.default)"
          class="w-full bg-dark-800 border border-dark-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
        />
      </div>
    </div>

    <!-- Compile status -->
    <div v-if="compileError" class="flex items-start gap-2 p-2.5 rounded-lg bg-red-500/10 text-red-400 text-[11px]">
      <i class="fas fa-exclamation-circle mt-0.5 flex-shrink-0"></i>
      <span>{{ compileError }}</span>
    </div>
    <div v-if="isCompiling" class="flex items-center gap-2 text-[11px] text-white/30">
      <i class="fas fa-spinner fa-spin"></i>
      <span>Compiling strategy...</span>
    </div>

    <!-- Run Button -->
    <button
      id="run-backtest-btn"
      @click="runBacktest"
      :disabled="!canRun"
      :class="[
        'w-full py-3 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2',
        canRun
          ? 'bg-accent-500 hover:bg-accent-600 text-white shadow-lg shadow-accent-500/20'
          : 'bg-dark-700 text-white/30 cursor-not-allowed',
      ]"
    >
      <i class="fas fa-play text-xs"></i>
      Run Backtest
    </button>

    <!-- Validation hints -->
    <p v-if="dateError" class="text-[10px] text-amber-400/70">
      <i class="fas fa-exclamation-triangle mr-1"></i>
      {{ dateError }}
    </p>
    <p v-else-if="!props.generatedCode || props.generatedCode.length < 20" class="text-[10px] text-amber-400/70">
      <i class="fas fa-exclamation-triangle mr-1"></i>
      Build a strategy with entry/exit signals first
    </p>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { getSymbols, compilePinescript } from '../../api/index.js'

// ── Props & Emits ─────────────────────────────────────────────
const props = defineProps({
  generatedCode: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['run-backtest'])

// ── Timeframe options ─────────────────────────────────────────
const timeframes = [
  { value: '1m', label: '1 Minute' },
  { value: '5m', label: '5 Minutes' },
  { value: '15m', label: '15 Minutes' },
  { value: '30m', label: '30 Minutes' },
  { value: '1h', label: '1 Hour' },
  { value: '4h', label: '4 Hours' },
  { value: '1d', label: '1 Day' },
]

// ── Reactive config state ─────────────────────────────────────
const config = reactive({
  timeframe: '1h',
  startDate: '',
  endDate: '',
  initialCapital: 10000,
  commission: 0.1,
  slippage: 0.05,
  magnifier: true,
})

// ── Symbol info (date bounds) ─────────────────────────────────
const symbolInfo = ref(null)

// ── Dynamic parameter discovery ───────────────────────────────
const discoveredParams = ref({})
const paramOverrides = reactive({})
const isCompiling = ref(false)
const compileError = ref('')

// ── Auto-toggle magnifier based on timeframe ──────────────────
// Magnifier is most useful when TF > 1m (provides realistic intra-bar fills)
watch(
  () => config.timeframe,
  (tf) => {
    config.magnifier = tf !== '1m'
  }
)

// ── Load symbol info on mount for date range bounds ───────────
onMounted(async () => {
  try {
    const symbols = await getSymbols()
    if (symbols.length > 0) {
      const first = symbols[0]
      // Extract YYYY-MM-DD from timestamps like "2008-01-22 07:30:00+00"
      const extractDate = (raw) => {
        if (!raw) return ''
        // Try ISO format first (has T), then space-separated
        const m = raw.match(/^(\d{4}-\d{2}-\d{2})/)
        return m ? m[1] : ''
      }
      symbolInfo.value = {
        minDate: extractDate(first.min_ts),
        maxDate: extractDate(first.max_ts),
      }
    }
  } catch (e) {
    console.error('Failed to load symbols:', e)
  }
})

// ── Discover strategy parameters via /api/compile ─────────────
// Debounced: waits 1s after last code change before compiling.
let compileDebounce = null

watch(
  () => props.generatedCode,
  (code) => {
    if (compileDebounce) clearTimeout(compileDebounce)
    compileError.value = ''

    if (!code || code.length < 20) {
      discoveredParams.value = {}
      return
    }

    isCompiling.value = true
    compileDebounce = setTimeout(async () => {
      try {
        const result = await compilePinescript(code)
        discoveredParams.value = result.inputs || {}
        compileError.value = ''

        // Seed defaults for any newly discovered params
        for (const [key, info] of Object.entries(result.inputs || {})) {
          if (!(key in paramOverrides)) {
            paramOverrides[key] = info.default
          }
        }
      } catch (e) {
        // Compile errors are expected while user is still editing
        compileError.value = e.message || 'Compilation failed'
        discoveredParams.value = {}
      } finally {
        isCompiling.value = false
      }
    }, 1000)
  },
  { immediate: true }
)

// ── Validation ────────────────────────────────────────────────
const dateError = computed(() => {
  if (!config.startDate || !config.endDate) return 'Please select a date range'
  if (config.startDate >= config.endDate) return 'Start date must be before end date'
  if (symbolInfo.value) {
    if (config.startDate < symbolInfo.value.minDate) return `Start date before available data (${symbolInfo.value.minDate})`
    if (config.endDate > symbolInfo.value.maxDate) return `End date after available data (${symbolInfo.value.maxDate})`
  }
  return null
})

const canRun = computed(() => {
  return (
    !dateError.value &&
    props.generatedCode.length > 20 &&
    !isCompiling.value &&
    !compileError.value
  )
})

// ── Run backtest ──────────────────────────────────────────────
function runBacktest() {
  if (!canRun.value) return

  // Build param overrides — only include values the user actually set
  const params = {}
  for (const [key, val] of Object.entries(paramOverrides)) {
    if (val != null && val !== '') {
      params[key] = val
    }
  }

  emit('run-backtest', {
    pinescript: props.generatedCode,
    timeframe: config.timeframe,
    start_date: config.startDate,
    end_date: config.endDate,
    initial_capital: config.initialCapital,
    commission: config.commission / 100,   // UI shows %, API expects fraction
    slippage: config.slippage / 100,       // UI shows %, API expects fraction
    params,
    mode: config.magnifier ? 'magnifier' : 'standard',
  })
}
</script>
