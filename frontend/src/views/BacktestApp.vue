<template>
  <div class="h-screen flex flex-col" style="background: linear-gradient(180deg, #080a16 0%, #0b0e1c 100%);">
    <!-- Header -->
    <header
      class="flex items-center justify-between px-4 py-2.5 border-b border-white/[0.06] relative z-[100]"
      style="background: #080a16;"
    >
      <!-- Left: branding + template -->
      <div class="flex items-center gap-3">
        <h1 class="text-sm font-semibold text-white/80">
          <i class="fas fa-chart-line mr-1.5 text-accent-500"></i>
          Backtest System
        </h1>

        <div class="h-5 w-px bg-white/[0.06]"></div>

        <!-- Load Template dropdown -->
        <div class="relative" id="template-dropdown">
          <button
            ref="templateBtnRef"
            @click="showTemplateMenu = !showTemplateMenu"
            class="glass-btn flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg"
          >
            <i class="fas fa-folder-open text-[10px]"></i>
            Load Template
            <i class="fas fa-chevron-down text-[9px] opacity-50"></i>
          </button>
        </div>

        <!-- Teleport dropdown to body so it's never clipped -->
        <Teleport to="body">
          <div v-if="showTemplateMenu">
            <div class="fixed inset-0 z-[9998]" @click="showTemplateMenu = false"></div>
            <div
              class="fixed z-[9999] w-64 rounded-xl overflow-hidden"
              :style="templateMenuStyle"
            >
              <div class="p-1 max-h-80 overflow-y-auto">
                <button
                  v-for="t in templates"
                  :key="t.filename"
                  @click="loadTemplate(t)"
                  class="w-full text-left px-3 py-2.5 text-xs text-white/70 hover:text-white hover:bg-white/[0.06] rounded-lg transition-all"
                >
                  {{ t.name }}
                </button>
                <div
                  v-if="templates.length === 0"
                  class="px-3 py-4 text-xs text-white/30 text-center"
                >
                  <i class="fas fa-spinner fa-spin mr-1"></i> Loading...
                </div>
              </div>
            </div>
          </div>
        </Teleport>
      </div>

      <!-- Right: actions -->
      <div class="flex items-center gap-2">
        <button
          @click="showTutorial"
          class="glass-btn flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg"
          title="Show Tutorial"
        >
          <i class="fas fa-graduation-cap text-[10px]"></i>
          <span class="hidden sm:inline">Tutorial</span>
        </button>

        <button
          @click="toggleBacktestPanel"
          class="glass-btn flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg"
          :class="showBacktestPanel ? '!bg-accent-500/10 !text-accent-400' : ''"
        >
          <i class="fas fa-flask text-[10px]"></i>
          <span class="hidden sm:inline">Backtest</span>
        </button>
      </div>
    </header>

    <!-- Main content -->
    <div class="flex-1 flex overflow-hidden relative">
      <!-- Strategy Builder (left) -->
      <StrategyBuilderPage
        ref="builderRef"
        class="flex-1 min-w-0"
        @strategy-changed="onStrategyChanged"
      />

      <!-- Backtest Panel (right slide) -->
      <transition name="slide-panel">
        <div
          v-if="showBacktestPanel"
          class="w-[380px] flex-shrink-0 border-l border-white/[0.04] flex flex-col overflow-hidden"
          style="background: rgba(14, 17, 32, 0.98);"
        >
          <div class="flex-1 overflow-y-auto">
            <BacktestConfigPanel
              :generated-code="generatedCode"
              @run-backtest="handleRunBacktest"
            />

            <div class="border-t border-white/[0.04]">
              <BacktestJobTracker
                ref="jobTrackerRef"
                @view-result="handleViewResult"
              />
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- Result Detail (slide up from bottom) -->
    <transition name="slide-up">
      <div
        v-if="activeResult"
        class="border-t border-white/[0.06]"
        style="max-height: 60vh; overflow-y: auto; background: #0b0e1c;"
      >
        <ResultDetail :result="activeResult" @close="activeResult = null" />
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import StrategyBuilderPage from '../components/strategy-builder/StrategyBuilderPage.vue'
import BacktestConfigPanel from '../components/backtest/BacktestConfigPanel.vue'
import BacktestJobTracker from '../components/backtest/BacktestJobTracker.vue'
import ResultDetail from '../components/backtest/ResultDetail.vue'
import { getStrategies } from '../api/index.js'

// ── Refs ──────────────────────────────────────────────────────
const builderRef = ref(null)
const jobTrackerRef = ref(null)
const templateBtnRef = ref(null)
const showBacktestPanel = ref(true)
const showTemplateMenu = ref(false)

// Position the dropdown below the button using fixed positioning
const templateMenuStyle = computed(() => {
  if (!templateBtnRef.value) return { top: '48px', left: '140px' }
  const rect = templateBtnRef.value.getBoundingClientRect()
  return {
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
    background: '#141828',
    border: '1px solid rgba(255,255,255,0.1)',
    boxShadow: '0 8px 32px rgba(0,0,0,0.6)',
  }
})
const templates = ref([])
const generatedCode = ref('')
const activeResult = ref(null)

// ── Lifecycle ─────────────────────────────────────────────────
onMounted(async () => {
  try {
    templates.value = await getStrategies()
  } catch (e) {
    console.error('Failed to load templates:', e)
  }
})

// ── Template loading ──────────────────────────────────────────
function loadTemplate(template) {
  showTemplateMenu.value = false
  if (builderRef.value && template.strategy_data) {
    // StrategyBuilderPage exposes applyStrategyData via defineExpose
    const builder = builderRef.value
    if (builder.applyStrategyData) {
      builder.applyStrategyData(template.strategy_data)
    }
  }
}

// ── Strategy change listener ──────────────────────────────────
function onStrategyChanged(data) {
  if (data?.generatedCode) {
    generatedCode.value = data.generatedCode
  }
}

// Poll the builder's exposed generatedCode since Vue ref proxying
// doesn't propagate computed reactivity from child instances
let codeSync = null
onMounted(() => {
  codeSync = setInterval(() => {
    if (builderRef.value?.generatedCode) {
      const code = builderRef.value.generatedCode
      if (code !== generatedCode.value) {
        generatedCode.value = code
      }
    }
  }, 500)
})
onUnmounted(() => {
  if (codeSync) clearInterval(codeSync)
})

// ── Backtest panel toggle ─────────────────────────────────────
function toggleBacktestPanel() {
  showBacktestPanel.value = !showBacktestPanel.value
}

// ── Backtest execution ────────────────────────────────────────
function handleRunBacktest(config) {
  console.log('handleRunBacktest called:', config)
  console.log('jobTrackerRef:', jobTrackerRef.value)
  // BacktestConfigPanel emits this with the full config payload.
  // Forward it to BacktestJobTracker which handles API submission + polling.
  if (jobTrackerRef.value && jobTrackerRef.value.submitBacktest) {
    jobTrackerRef.value.submitBacktest(config)
  } else {
    console.error('jobTrackerRef not available or submitBacktest not exposed')
  }
}

// ── Result viewing ────────────────────────────────────────────
function handleViewResult(result) {
  activeResult.value = result
}

// ── Tutorial (stub — implemented in GuidedTour commit) ────────
function showTutorial() {
  console.log('Tutorial requested')
}

// Expose for external use (e.g. e2e tests)
defineExpose({ loadTemplate })
</script>

<style scoped>
/* Panel slide transition */
.slide-panel-enter-active,
.slide-panel-leave-active {
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.2s ease;
}
.slide-panel-enter-from,
.slide-panel-leave-to {
  width: 0 !important;
  opacity: 0;
  overflow: hidden;
}

/* Result slide-up transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: max-height 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.2s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  max-height: 0 !important;
  opacity: 0;
  overflow: hidden;
}
</style>
