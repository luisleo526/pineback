<template>
  <div class="expression-builder space-y-2">
    <!-- Expression tree rendered as nested formula -->
    <div class="expr-tree flex flex-wrap items-center gap-1">
      <ExprNode
        :node="modelValue"
        :variables="variables"
        :depth="0"
        @update="handleRootUpdate"
      />
    </div>

    <!-- Action buttons -->
    <div class="flex items-center gap-2 pt-1">
      <button
        @click="addOperation"
        class="px-2 py-1 text-xs rounded transition-colors bg-dark-700 text-dark-400 hover:text-white hover:bg-dark-600"
        title="Append operation"
      >
        <i class="fas fa-plus mr-1 text-[9px]"></i>Operation
      </button>
      <div class="relative" ref="funcMenuRef">
        <button
          @click="showFuncMenu = !showFuncMenu"
          class="px-2 py-1 text-xs rounded transition-colors bg-dark-700 text-dark-400 hover:text-white hover:bg-dark-600"
          title="Apply function"
        >
          <i class="fas fa-function mr-1 text-[9px]">f</i>(x) Function
        </button>
        <!-- Function picker dropdown -->
        <div
          v-if="showFuncMenu"
          class="absolute left-0 bottom-full mb-1 w-52 rounded-lg border border-dark-600 shadow-xl z-50 overflow-hidden"
          style="background: rgba(20, 24, 40, 0.98);"
        >
          <div class="p-1.5 border-b border-dark-700">
            <span class="text-[10px] text-dark-500 font-medium px-1.5">1 argument</span>
          </div>
          <div class="p-1 max-h-48 overflow-y-auto">
            <button
              v-for="fn in mathFuncs1"
              :key="fn.id"
              @click="wrapInFunction(fn.id)"
              class="w-full text-left px-2.5 py-1.5 text-xs rounded hover:bg-dark-700 text-dark-300 hover:text-white transition-colors flex items-center justify-between"
            >
              <span class="font-mono">{{ fn.label }}(x)</span>
              <span class="text-[10px] text-dark-500">{{ fn.description }}</span>
            </button>
          </div>
          <div class="p-1.5 border-t border-dark-700">
            <span class="text-[10px] text-dark-500 font-medium px-1.5">2 arguments</span>
          </div>
          <div class="p-1">
            <button
              v-for="fn in mathFuncs2"
              :key="fn.id"
              @click="wrapInFunction(fn.id)"
              class="w-full text-left px-2.5 py-1.5 text-xs rounded hover:bg-dark-700 text-dark-300 hover:text-white transition-colors flex items-center justify-between"
            >
              <span class="font-mono">{{ fn.label }}(x, y)</span>
              <span class="text-[10px] text-dark-500">{{ fn.description }}</span>
            </button>
          </div>
          <div class="p-1 border-t border-dark-700">
            <button
              @click="wrapInNegate()"
              class="w-full text-left px-2.5 py-1.5 text-xs rounded hover:bg-dark-700 text-dark-300 hover:text-white transition-colors flex items-center justify-between"
            >
              <span class="font-mono">-x</span>
              <span class="text-[10px] text-dark-500">Negate</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- PineScript preview -->
    <div class="pt-1.5 border-t border-dark-700">
      <code class="text-xs text-dark-400 font-mono">{{ previewCode }}</code>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import ExprNode from './ExprNode.vue'
import {
  MathFunctions,
  MathOperators,
  PriceSources,
  getPriceSource,
  getMathFunction,
  createExprLeaf,
  createExprBinary,
  createExprUnary,
  createExprFunc,
  isExprLeaf,
  deepClone,
} from '../../utils/condition-types.js'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
  variables: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

const showFuncMenu = ref(false)
const funcMenuRef = ref(null)

const mathFuncs1 = MathFunctions.filter(f => f.argCount === 1)
const mathFuncs2 = MathFunctions.filter(f => f.argCount === 2)

// Close func menu on outside click
function handleClickOutside(e) {
  if (funcMenuRef.value && !funcMenuRef.value.contains(e.target)) {
    showFuncMenu.value = false
  }
}
onMounted(() => document.addEventListener('click', handleClickOutside, true))
onUnmounted(() => document.removeEventListener('click', handleClickOutside, true))

function handleRootUpdate(newNode) {
  emit('update:modelValue', newNode)
}

/**
 * Append a new operation: wraps current tree as left side of a new binary node
 */
function addOperation() {
  const current = deepClone(props.modelValue)
  const newNode = createExprBinary('+', current, createExprLeaf('constant', { value: 0 }))
  emit('update:modelValue', newNode)
}

/**
 * Wrap the entire expression in a math function
 */
function wrapInFunction(funcId) {
  const fn = getMathFunction(funcId)
  if (!fn) return
  const current = deepClone(props.modelValue)
  if (fn.argCount === 1) {
    emit('update:modelValue', createExprFunc(funcId, [current]))
  } else {
    // 2-arg: current becomes first arg, second is a default leaf
    emit('update:modelValue', createExprFunc(funcId, [current, createExprLeaf('constant', { value: 0 })]))
  }
  showFuncMenu.value = false
}

/**
 * Wrap the expression in a negate unary
 */
function wrapInNegate() {
  const current = deepClone(props.modelValue)
  emit('update:modelValue', createExprUnary('negate', current))
  showFuncMenu.value = false
}

/**
 * Generate PineScript preview for the expression tree
 */
const previewCode = computed(() => {
  return renderNode(props.modelValue)
})

function renderNode(node) {
  if (!node) return 'na'

  switch (node.type) {
    case 'price': {
      const src = getPriceSource(node.source)
      return src?.pinescript || node.source || 'close'
    }
    case 'variable': {
      const v = props.variables.find(v => v.id === node.variableId)
      return v?.name || 'na'
    }
    case 'constant':
      return String(node.value ?? 0)
    case 'input':
      return node.inputName || 'na'
    case 'binary': {
      const left = renderNode(node.left)
      const right = renderNode(node.right)
      return `(${left} ${node.operator} ${right})`
    }
    case 'unary': {
      const operand = renderNode(node.operand)
      if (node.func === 'negate') return `(-${operand})`
      return `${node.func}(${operand})`
    }
    case 'func': {
      const fn = getMathFunction(node.name)
      if (!fn) return 'na'
      const argStrs = (node.args || []).map(a => renderNode(a))
      return fn.pinescript(argStrs)
    }
    default:
      return 'na'
  }
}
</script>
