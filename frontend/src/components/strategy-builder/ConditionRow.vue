<template>
  <div class="condition-row p-2.5 sm:p-3 rounded-xl transition-all hover:shadow-lg hover:shadow-indigo-500/[0.03]" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);" @mouseenter="$el.style.borderColor='rgba(255,255,255,0.08)'" @mouseleave="$el.style.borderColor='rgba(255,255,255,0.04)'">
    <!-- Condition Expression Layout -->
    <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap group">
      <!-- Left Operand (Base Value) -->
      <div class="operand-wrapper">
        <OperandSelector
          :modelValue="condition.left"
          @update:modelValue="updateLeft"
          :variables="variables"
          :inputs="inputs"
          @create-input="$emit('create-input', $event)"
        />
      </div>

      <!-- Operator -->
      <div class="operator-wrapper">
        <button
          ref="operatorBtnRef"
          @click="toggleOperatorMenu"
          :class="[
            'px-3 py-2 sm:py-1.5 rounded-lg text-sm font-semibold transition-all flex items-center gap-1 min-h-[36px]',
            isCrossOperator 
              ? 'text-rose-400 hover:bg-rose-500/10' 
              : 'text-white/90 hover:bg-white/[0.06]'
          ]"
          :style="isCrossOperator ? 'background: rgba(244,63,94,0.08); border: 1px solid rgba(244,63,94,0.15);' : 'background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.06);'"
        >
          <span class="font-mono">{{ getOperatorDisplay(condition.operator) }}</span>
          <i class="fas fa-chevron-down text-xs opacity-50"></i>
        </button>
        
        <!-- Operator Dropdown (fixed position, not clipped by parent overflow) -->
        <Teleport to="body">
          <div v-if="showOperatorMenu">
            <div 
              class="fixed inset-0 z-[9998]" 
              @click="showOperatorMenu = false"
            ></div>
            <div 
              class="fixed rounded-xl shadow-xl z-[9999] min-w-[180px]"
              style="background: rgba(20, 24, 40, 0.96); border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(20px);"
              :style="operatorMenuStyle"
            >
              <div class="p-1">
                <div class="px-2 py-1 text-xs text-dark-400 font-medium">Comparison</div>
                <button
                  v-for="op in comparisonOperators"
                  :key="op.id"
                  @click="selectOperator(op.id)"
                  :class="[
                    'w-full px-3 py-2.5 sm:py-1.5 text-left rounded text-sm transition-colors flex items-center gap-2 min-h-[40px] sm:min-h-0',
                    condition.operator === op.id 
                      ? 'bg-accent-600 text-white' 
                      : 'text-dark-300 hover:bg-dark-700 hover:text-white'
                  ]"
                >
                  <span class="w-6 font-mono">{{ op.label }}</span>
                  <span class="text-xs text-dark-400">{{ getOperatorName(op.id) }}</span>
                </button>
              </div>
              <div class="border-t border-dark-700 p-1">
                <div class="px-2 py-1 text-xs text-dark-400 font-medium">Crossover</div>
                <button
                  v-for="op in crossOperators"
                  :key="op.id"
                  @click="selectOperator(op.id)"
                  :class="[
                    'w-full px-3 py-2.5 sm:py-1.5 text-left rounded text-sm transition-colors flex items-center gap-2 min-h-[40px] sm:min-h-0',
                    condition.operator === op.id 
                      ? 'bg-pink-600 text-white' 
                      : 'text-dark-300 hover:bg-dark-700 hover:text-white'
                  ]"
                >
                  <span class="w-6">{{ op.label }}</span>
                  <span class="text-xs text-dark-400">{{ getOperatorName(op.id) }}</span>
                </button>
              </div>
            </div>
          </div>
        </Teleport>
      </div>

      <!-- Right Operand (Secondary Value) -->
      <div class="operand-wrapper">
        <OperandSelector
          :modelValue="condition.right"
          @update:modelValue="updateRight"
          :variables="variables"
          :inputs="inputs"
          :allowConstant="!isCrossOperator"
          @create-input="$emit('create-input', $event)"
        />
      </div>

      <!-- Delete Button -->
      <button
        @click="$emit('delete')"
        class="ml-auto w-8 h-8 flex items-center justify-center text-white/15 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all flex-shrink-0 opacity-0 group-hover:opacity-100"
        title="Delete condition"
      >
        <i class="fas fa-trash-alt text-[10px]"></i>
      </button>
    </div>
    
    <!-- Condition Description -->
    <div class="mt-2 pt-2 border-t border-white/[0.03] text-[11px] text-white/25">
      <span v-if="isCrossOperator">
        Triggers when <span class="text-indigo-400/70">left value</span> 
        {{ condition.operator === 'crossover' ? 'crosses above' : condition.operator === 'crossunder' ? 'crosses below' : 'crosses' }} 
        <span class="text-indigo-400/70">right value</span>
      </span>
      <span v-else>
        Triggers when <span class="text-indigo-400/70">left value</span> 
        {{ getOperatorDescription(condition.operator) }} 
        <span class="text-indigo-400/70">right value</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, nextTick } from 'vue'
import OperandSelector from './OperandSelector.vue'
import { OperatorList, isCrossOperator as checkCrossOp } from '../../utils/condition-types.js'

const props = defineProps({
  condition: {
    type: Object,
    required: true,
  },
  variables: {
    type: Array,
    default: () => [],
  },
  inputs: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:condition', 'delete', 'create-input'])

const showOperatorMenu = ref(false)
const operatorBtnRef = ref(null)
const operatorMenuPos = reactive({ top: 0, left: 0 })

const operatorMenuStyle = computed(() => ({
  top: `${operatorMenuPos.top}px`,
  left: `${operatorMenuPos.left}px`,
}))

function toggleOperatorMenu() {
  if (showOperatorMenu.value) {
    showOperatorMenu.value = false
    return
  }
  // Position the dropdown relative to the button
  if (operatorBtnRef.value) {
    const rect = operatorBtnRef.value.getBoundingClientRect()
    const menuWidth = 180
    const menuHeight = 320 // estimated
    
    let top = rect.bottom + 4
    let left = rect.left + rect.width / 2 - menuWidth / 2
    
    // Keep within viewport
    if (top + menuHeight > window.innerHeight) {
      top = Math.max(8, rect.top - menuHeight - 4)
    }
    if (left + menuWidth > window.innerWidth) {
      left = window.innerWidth - menuWidth - 8
    }
    if (left < 8) left = 8
    
    operatorMenuPos.top = top
    operatorMenuPos.left = left
  }
  showOperatorMenu.value = true
}

// Split operators into comparison and cross types
const comparisonOperators = OperatorList.filter(op => !checkCrossOp(op.id))
const crossOperators = OperatorList.filter(op => checkCrossOp(op.id))

const isCrossOperator = computed(() => {
  return checkCrossOp(props.condition.operator)
})

function getOperatorDisplay(opId) {
  const op = OperatorList.find(o => o.id === opId)
  return op?.label || opId
}

function getOperatorName(opId) {
  const names = {
    lt: 'Less than',
    gt: 'Greater than',
    lte: 'Less or equal',
    gte: 'Greater or equal',
    eq: 'Equal to',
    neq: 'Not equal',
    crossover: 'Cross above',
    crossunder: 'Cross below',
    cross: 'Cross (either direction)',
  }
  return names[opId] || ''
}

function getOperatorDescription(opId) {
  const descriptions = {
    lt: 'is less than',
    gt: 'is greater than',
    lte: 'is less than or equal to',
    gte: 'is greater than or equal to',
    eq: 'equals',
    neq: 'is not equal to',
  }
  return descriptions[opId] || ''
}

function selectOperator(opId) {
  showOperatorMenu.value = false
  updateOperator(opId)
}

function updateLeft(newLeft) {
  emit('update:condition', {
    ...props.condition,
    left: newLeft,
  })
}

function updateRight(newRight) {
  emit('update:condition', {
    ...props.condition,
    right: newRight,
  })
}

function updateOperator(newOp) {
  const updated = {
    ...props.condition,
    operator: newOp,
  }
  
  // If switching to crossover/crossunder, ensure right is not a constant
  if (checkCrossOp(newOp) && props.condition.right.type === 'constant') {
    updated.right = {
      type: 'indicator',
      indicator: 'sma',
      params: { source: 'close', period: 20 },
    }
  }
  
  emit('update:condition', updated)
}
</script>

<style scoped>
.condition-row {
  min-height: 56px;
}

.operand-wrapper {
  flex-shrink: 0;
}

.operator-wrapper {
  flex-shrink: 0;
}
</style>
