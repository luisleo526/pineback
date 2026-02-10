<template>
  <div class="strategy-builder-page h-screen flex flex-col" style="background: linear-gradient(180deg, #080a16 0%, #0b0e1c 100%);">
    <!-- Header Bar -->
    <header class="flex items-center justify-between px-2 sm:px-3 lg:px-5 py-2 sm:py-2.5 border-b border-white/[0.06] relative z-[9991]" style="background: #080a16;">
      <div class="flex items-center gap-1.5 sm:gap-2 lg:gap-3 min-w-0">
        <input
          v-model="strategy.name"
          type="text"
          class="glass-input px-2 sm:px-3 py-1.5 text-xs sm:text-sm min-w-0 w-20 sm:w-36 lg:w-44 2xl:w-56"
          placeholder="Strategy Name"
        />
      </div>
      
      <div class="flex items-center gap-1 sm:gap-1.5 lg:gap-2 flex-shrink-0">
        <!-- Validation status (clickable to show details) -->
        <div v-if="validationMessages.length > 0" class="relative">
          <button
            @click="showValidationPanel = !showValidationPanel"
            class="glass-btn flex items-center gap-1 sm:gap-1.5 text-xs px-1.5 sm:px-2.5 py-1.5 rounded-lg min-h-[32px] sm:min-h-[34px]"
          >
            <span v-if="errorCount > 0" class="flex items-center gap-1 sm:gap-1.5 text-red-400">
              <span class="w-1.5 h-1.5 rounded-full bg-red-400 pulse-dot"></span>
              <span class="hidden lg:inline">{{ errorCount }} errors</span>
            </span>
            <span v-if="warningCount > 0" class="flex items-center gap-1 sm:gap-1.5 text-amber-400">
              <span class="w-1.5 h-1.5 rounded-full bg-amber-400 pulse-dot"></span>
              <span class="hidden lg:inline">{{ warningCount }} warnings</span>
            </span>
          </button>
          
          <!-- Validation details dropdown -->
          <div 
            v-show="showValidationPanel"
            class="absolute top-full right-0 mt-2 w-[calc(100vw-2rem)] sm:w-80 max-w-80 rounded-xl overflow-hidden z-[9990]"
            style="background: #141828; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.6);"
          >
            <div class="px-3 py-2.5 border-b border-white/[0.06] flex items-center justify-between">
              <span class="text-xs text-white/60 font-medium">Validation Results</span>
              <button @click="showValidationPanel = false" class="text-white/30 hover:text-white text-xs p-1 transition-colors">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="p-2 space-y-1.5 max-h-48 overflow-y-auto">
              <div 
                v-for="(msg, i) in validationMessages" 
                :key="i"
                class="flex items-start gap-2 px-2.5 py-2 rounded-lg text-xs"
                :class="msg.type === 'error' ? 'bg-red-500/10 text-red-400' : 'bg-amber-500/10 text-amber-400'"
              >
                <i :class="['fas mt-0.5', msg.type === 'error' ? 'fa-times-circle' : 'fa-exclamation-triangle']"></i>
                <span>{{ msg.message }}</span>
              </div>
            </div>
          </div>
        </div>
        <span v-else class="hidden sm:flex items-center gap-1.5 text-emerald-400 text-xs px-2 lg:px-2.5 py-1.5 rounded-lg bg-emerald-500/10">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span class="hidden lg:inline">Ready</span>
        </span>
        
        <!-- New strategy -->
        <button 
          @click="newStrategy"
          class="glass-btn flex items-center justify-center gap-1.5 min-w-[32px] sm:min-w-[34px] min-h-[32px] sm:min-h-[34px] px-2 sm:px-2.5 lg:px-3 py-1.5 text-xs rounded-lg"
          title="New Strategy"
        >
          <i class="fas fa-plus text-[10px]"></i>
          <span class="hidden lg:inline">New</span>
        </button>
        
        <div class="hidden sm:block h-5 w-px bg-white/[0.06]"></div>
        
        <!-- Toggle right panel button (hidden on mobile — FAB is used instead) -->
        <button 
          @click="toggleRightPanel"
          class="hidden sm:flex glass-btn items-center justify-center gap-1.5 min-w-[34px] min-h-[34px] px-2.5 lg:px-3 py-1.5 text-xs rounded-lg"
          :class="showRightPanel ? '!bg-indigo-500/10 !text-indigo-400 !border-indigo-500/20' : ''"
          :title="showRightPanel ? 'Collapse variables/inputs panel' : 'Expand variables/inputs panel'"
        >
          <i :class="['fas transition-transform duration-200 text-[10px]', showRightPanel ? 'fa-sidebar-flip' : 'fa-sidebar']" style="font-size: 12px;">
          </i>
          <i class="fas fa-cube text-[10px] hidden lg:inline"></i>
        </button>
      </div>
    </header>
    
    <!-- Main Content - Responsive Layout -->
    <div class="flex-1 flex overflow-hidden relative">
      <!-- Left Column - Signal Condition Builder -->
      <div class="flex-1 min-w-0 flex flex-col">
        <!-- Condition Builder -->
        <SignalConditionBuilder
          v-model:signals="strategy.signals"
          :variables="strategy.variables"
          :inputs="strategy.inputs"
          @create-input="handleCreateInput"
          class="flex-1 min-h-0 overflow-auto"
        />
        
        <!-- Bottom - PineScript Preview (resizable) -->
        <div 
          ref="previewContainerRef"
          class="flex-shrink-0 flex flex-col relative border-t border-white/[0.04]"
          :class="{ 'preview-resizing': isResizing }"
          :style="{ height: previewCollapsed ? '40px' : `${previewHeight}px` }"
        >
          <!-- Resize handle - full-width draggable bar -->
          <div 
            v-show="!previewCollapsed"
            class="resize-handle"
            @mousedown.prevent="startResize"
            @touchstart.prevent="startResizeTouch"
          >
            <div class="resize-handle-inner">
              <div class="resize-grip">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
          
          <!-- Collapse toggle bar -->
          <div 
            class="h-8 flex items-center px-4 select-none flex-shrink-0 cursor-pointer hover:bg-white/[0.02] transition-colors"
            style="background: rgba(14, 17, 32, 0.4);"
            @click="togglePreviewCollapse"
          >
            <span class="text-[11px] font-medium text-white/40 flex items-center gap-2">
              <i :class="['fas fa-chevron-up text-[9px] transition-transform duration-200', previewCollapsed ? 'rotate-180' : '']"></i>
              <i class="fas fa-code text-[9px]"></i>
              PineScript Preview
            </span>
          </div>
          
          <PineScriptPreview 
            v-show="!previewCollapsed"
            :code="generatedCode"
            :warnings="validationMessages"
            class="flex-1 min-h-0"
          />
        </div>
      </div>
      
      <!-- Mobile overlay backdrop -->
      <div
        v-if="showRightPanel"
        class="md:hidden fixed inset-0 bg-black/50 z-30"
        @click="showRightPanel = false"
      ></div>

      <!-- Right Column - Variables & Inputs (side panel on desktop, bottom sheet on mobile) -->
      <div :class="[
        'flex flex-col overflow-hidden transition-all duration-300',
        'md:relative md:z-auto md:border-l md:border-white/[0.04]',
        showRightPanel
          ? 'right-panel-open opacity-100 md:translate-x-0 mobile-sheet-open'
          : 'md:w-0 opacity-0 md:translate-x-full md:border-l-0 mobile-sheet-closed',
        'mobile-bottom-sheet md:mobile-sheet-reset'
      ]" style="background: rgba(14, 17, 32, 0.98); backdrop-filter: blur(20px);">
        <!-- Mobile bottom sheet drag handle -->
        <div class="md:hidden flex flex-col items-center pt-2 pb-1 cursor-grab active:cursor-grabbing"
             @touchstart.prevent="startSheetDrag"
        >
          <div class="w-10 h-1 rounded-full bg-white/20"></div>
          <div class="flex items-center justify-between w-full px-4 mt-2">
            <span class="text-xs font-medium text-white/60">
              {{ rightPanelTab === 'variables' ? 'Variables' : 'Inputs' }}
            </span>
            <button
              @click="showRightPanel = false"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-white/40 hover:text-white hover:bg-white/[0.08] transition-all"
            >
              <i class="fas fa-times text-xs"></i>
            </button>
          </div>
        </div>

        <!-- Right Panel Tabs -->
        <div class="flex p-1.5 gap-1 border-b border-white/[0.04]">
          <button
            @click="rightPanelTab = 'variables'"
            :class="[
              'flex-1 px-3 py-2 text-xs font-medium rounded-lg transition-all',
              rightPanelTab === 'variables'
                ? 'text-white bg-white/[0.08] shadow-sm'
                : 'text-white/40 hover:text-white/70 hover:bg-white/[0.03]'
            ]"
          >
            <i class="fas fa-cube mr-1.5 text-[10px]"></i>Variables
          </button>
          <button
            @click="rightPanelTab = 'inputs'"
            :class="[
              'flex-1 px-3 py-2 text-xs font-medium rounded-lg transition-all',
              rightPanelTab === 'inputs'
                ? 'text-white bg-white/[0.08] shadow-sm'
                : 'text-white/40 hover:text-white/70 hover:bg-white/[0.03]'
            ]"
          >
            <i class="fas fa-sliders-h mr-1.5 text-[10px]"></i>Inputs
          </button>
        </div>

        <!-- Right Panel Content -->
        <div class="flex-1 overflow-y-auto p-4">
          <!-- Variables Tab -->
          <VariablesPanel
            v-show="rightPanelTab === 'variables'"
            v-model:variables="strategy.variables"
            :inputs="strategy.inputs"
          />

          <!-- Inputs Tab -->
          <StrategyInputsPanel
            v-show="rightPanelTab === 'inputs'"
            v-model:inputs="strategy.inputs"
            :variables="strategy.variables"
          />
        </div>
      </div>
    </div>
    
    <!-- Floating toggle button for right panel (mobile only) -->
    <button 
      v-show="!showRightPanel"
      @click="toggleRightPanel"
      class="md:hidden fixed bottom-4 right-4 w-14 h-14 bg-accent-600 hover:bg-accent-500 rounded-full flex items-center justify-center text-white shadow-lg shadow-accent-600/30 z-20 transition-all active:scale-95"
      title="Show variables panel"
    >
      <i class="fas fa-cube text-lg"></i>
    </button>
    
    <!-- Click outside to close dropdowns -->
    <div 
      v-if="showValidationPanel" 
      class="fixed inset-0 z-[9989]" 
      @click="showValidationPanel = false"
    ></div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import SignalConditionBuilder from './SignalConditionBuilder.vue'
import VariablesPanel from './VariablesPanel.vue'
import StrategyInputsPanel from './StrategyInputsPanel.vue'
import PineScriptPreview from './PineScriptPreview.vue'
import { 
  createEmptyStrategy, 
  createEmptySignal,
  createConditionGroup,
  createCondition,
  deepClone,
  migrateExpression,
} from '../../utils/condition-types.js'
import { generatePineScriptFromConditions, validateStrategy } from '../../utils/pinescript-generator.js'

// Props
const props = defineProps({
  initialStrategy: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['strategy-changed'])

// State
const strategy = reactive(createEmptyStrategy())
const showValidationPanel = ref(false)
const showRightPanel = ref(typeof window !== 'undefined' && window.innerWidth >= 768)
const rightPanelTab = ref('variables')

// Resizable preview state
const previewContainerRef = ref(null)
const previewHeight = ref(typeof window !== 'undefined' ? (window.innerWidth < 640 ? 180 : window.innerWidth >= 2560 ? 350 : 256) : 256)
const previewCollapsed = ref(typeof window !== 'undefined' && window.innerWidth < 640)
const isResizing = ref(false)
const startY = ref(0)
const startHeight = ref(0)

function togglePreviewCollapse() {
  previewCollapsed.value = !previewCollapsed.value
}

function toggleRightPanel() {
  showRightPanel.value = !showRightPanel.value
}

// Resize functionality
const MIN_HEIGHT = 100
const HEADER_RESERVE = 160 // space for top header + signal tabs

function startResize(e) {
  isResizing.value = true
  startY.value = e.clientY
  startHeight.value = previewHeight.value
  
  document.addEventListener('mousemove', doResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'ns-resize'
  document.body.style.userSelect = 'none'
}

function startResizeTouch(e) {
  if (!e.touches.length) return
  isResizing.value = true
  startY.value = e.touches[0].clientY
  startHeight.value = previewHeight.value
  
  document.addEventListener('touchmove', doResizeTouch, { passive: false })
  document.addEventListener('touchend', stopResizeTouch)
}

function doResize(e) {
  if (!isResizing.value) return
  applyResize(e.clientY)
}

function doResizeTouch(e) {
  if (!isResizing.value || !e.touches.length) return
  e.preventDefault()
  applyResize(e.touches[0].clientY)
}

function applyResize(clientY) {
  const deltaY = startY.value - clientY
  const maxHeight = window.innerHeight - HEADER_RESERVE
  const newHeight = Math.max(MIN_HEIGHT, Math.min(maxHeight, startHeight.value + deltaY))
  previewHeight.value = newHeight
  
  // Auto-hide right panel when preview gets very tall (over 60% of viewport)
  if (newHeight > window.innerHeight * 0.6 && showRightPanel.value) {
    showRightPanel.value = false
  }
}

function stopResize() {
  isResizing.value = false
  document.removeEventListener('mousemove', doResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

function stopResizeTouch() {
  isResizing.value = false
  document.removeEventListener('touchmove', doResizeTouch)
  document.removeEventListener('touchend', stopResizeTouch)
}

// Mobile bottom sheet drag-to-dismiss
const sheetDragStartY = ref(0)
const sheetDragDelta = ref(0)
const isDraggingSheet = ref(false)

function startSheetDrag(e) {
  if (!e.touches.length) return
  isDraggingSheet.value = true
  sheetDragStartY.value = e.touches[0].clientY
  sheetDragDelta.value = 0
  document.addEventListener('touchmove', doSheetDrag, { passive: false })
  document.addEventListener('touchend', stopSheetDrag)
}

function doSheetDrag(e) {
  if (!isDraggingSheet.value || !e.touches.length) return
  e.preventDefault()
  const delta = e.touches[0].clientY - sheetDragStartY.value
  // Only allow dragging down (positive delta)
  sheetDragDelta.value = Math.max(0, delta)
  const sheet = document.querySelector('.mobile-bottom-sheet')
  if (sheet && window.innerWidth < 768) {
    sheet.style.transform = `translateY(${sheetDragDelta.value}px)`
    sheet.style.transition = 'none'
  }
}

function stopSheetDrag() {
  isDraggingSheet.value = false
  document.removeEventListener('touchmove', doSheetDrag)
  document.removeEventListener('touchend', stopSheetDrag)
  const sheet = document.querySelector('.mobile-bottom-sheet')
  if (sheet) {
    sheet.style.transition = ''
    sheet.style.transform = ''
  }
  // If dragged more than 100px down, close the panel
  if (sheetDragDelta.value > 100) {
    showRightPanel.value = false
  }
  sheetDragDelta.value = 0
}

// Computed
const generatedCode = computed(() => {
  return generatePineScriptFromConditions(strategy)
})

const validationMessages = computed(() => {
  return validateStrategy(strategy)
})

const errorCount = computed(() => validationMessages.value.filter(m => m.type === 'error').length)
const warningCount = computed(() => validationMessages.value.filter(m => m.type === 'warning').length)

// Methods
function handleCreateInput(inputConfig) {
  strategy.inputs.push(inputConfig)
}

function newStrategy() {
  const hasContent = Object.values(strategy.signals).some(s => s.groups.length > 0)
  if (hasContent) {
    if (!confirm('Are you sure you want to create a new strategy? Current content will be cleared.')) return
  }
  Object.assign(strategy, createEmptyStrategy())
}


function copyCode() {
  navigator.clipboard.writeText(generatedCode.value).then(() => {
    // Could show a toast notification here
  }).catch(err => {
    console.error('Failed to copy:', err)
  })
}

// Load initial strategy if provided
function applyStrategyData(data) {
  const empty = createEmptyStrategy()
  const loaded = deepClone(data)
  Object.keys(empty).forEach(key => {
    strategy[key] = key in loaded ? loaded[key] : empty[key]
  })
  if (loaded.settings) {
    strategy.settings = { ...empty.settings, ...loaded.settings }
  }
  // Migrate old flat expression format { left, operator, right }
  // to new tree format { type: 'binary', operator, left, right }
  if (strategy.variables) {
    strategy.variables.forEach(v => {
      if (v.type === 'expression' && v.expression) {
        v.expression = migrateExpression(v.expression)
      }
    })
  }
}

// Handle window resize for responsive behavior
function handleResize() {
  const w = window.innerWidth
  // Close mobile nav on resize to desktop
  // (no mobile nav in this version, but keep resize handler for future use)
}

onMounted(() => {
  if (props.initialStrategy?.strategy_data) {
    applyStrategyData(props.initialStrategy.strategy_data)
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// Watch for external strategy load
watch(() => props.initialStrategy, (newStrategy) => {
  if (newStrategy?.strategy_data) {
    applyStrategyData(newStrategy.strategy_data)
  }
}, { deep: true })

// Emit strategy-changed whenever generated code changes
watch(generatedCode, (code) => {
  emit('strategy-changed', { generatedCode: code, strategy })
}, { immediate: true })

// Expose internal state for parent components (e.g. BacktestApp)
defineExpose({ applyStrategyData, strategy, generatedCode })
</script>

<style scoped>
/* Scoped overrides are now minimal -- global styles in strategy-builder.css */
</style>
