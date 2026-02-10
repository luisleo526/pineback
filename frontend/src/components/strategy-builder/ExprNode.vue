<template>
  <!-- Leaf node: price / variable / constant / input -->
  <div v-if="isLeaf" class="inline-flex items-center gap-1">
    <select
      :value="node.type"
      @change="changeLeafType($event.target.value)"
      class="bg-dark-700 border border-dark-600 rounded px-1.5 py-0.5 text-[11px] text-dark-300 focus:outline-none focus:border-accent-500"
    >
      <option value="price">Price</option>
      <option value="variable" :disabled="variables.length === 0">Variable</option>
      <option value="constant">Constant</option>
    </select>

    <!-- Price source -->
    <select
      v-if="node.type === 'price'"
      :value="node.source || 'close'"
      @change="emitUpdate({ ...node, source: $event.target.value })"
      class="bg-dark-700 border border-dark-600 rounded px-1.5 py-0.5 text-[11px] text-white focus:outline-none focus:border-accent-500"
    >
      <option v-for="src in priceSources" :key="src.id" :value="src.id">{{ src.label }}</option>
    </select>

    <!-- Variable ref -->
    <select
      v-else-if="node.type === 'variable'"
      :value="node.variableId || ''"
      @change="emitUpdate({ ...node, variableId: $event.target.value })"
      class="bg-dark-700 border border-dark-600 rounded px-1.5 py-0.5 text-[11px] text-white focus:outline-none focus:border-accent-500"
    >
      <option value="" disabled>Select</option>
      <option v-for="v in variables" :key="v.id" :value="v.id">{{ v.name }}</option>
    </select>

    <!-- Constant -->
    <input
      v-else-if="node.type === 'constant'"
      type="number"
      :value="node.value ?? 0"
      @input="emitUpdate({ ...node, value: parseFloat($event.target.value) || 0 })"
      step="any"
      class="w-16 bg-dark-700 border border-dark-600 rounded px-1.5 py-0.5 text-[11px] text-white focus:outline-none focus:border-accent-500"
    />
  </div>

  <!-- Binary node: left op right -->
  <div
    v-else-if="node.type === 'binary'"
    class="inline-flex flex-wrap items-center gap-1 rounded-md px-1 py-0.5"
    :class="depth > 0 ? 'bg-dark-800/60 border border-dark-700/50' : ''"
  >
    <span v-if="depth > 0" class="text-[10px] text-dark-600 select-none">(</span>
    <ExprNode
      :node="node.left"
      :variables="variables"
      :depth="depth + 1"
      @update="val => emitUpdate({ ...node, left: val })"
    />
    <select
      :value="node.operator"
      @change="emitUpdate({ ...node, operator: $event.target.value })"
      class="bg-dark-600 border border-dark-500 rounded px-1.5 py-0.5 text-xs text-white font-bold focus:outline-none focus:border-accent-500 mx-0.5"
    >
      <option v-for="op in mathOperators" :key="op.id" :value="op.id">{{ op.label }}</option>
    </select>
    <ExprNode
      :node="node.right"
      :variables="variables"
      :depth="depth + 1"
      @update="val => emitUpdate({ ...node, right: val })"
    />
    <span v-if="depth > 0" class="text-[10px] text-dark-600 select-none">)</span>
    <!-- Remove this binary level (unwrap to left operand) -->
    <button
      v-if="depth > 0"
      @click="emitUpdate(node.left)"
      class="w-4 h-4 flex items-center justify-center text-dark-500 hover:text-red-400 rounded transition-colors ml-0.5"
      title="Remove this operation"
    >
      <i class="fas fa-times text-[8px]"></i>
    </button>
  </div>

  <!-- Unary node: -x -->
  <div
    v-else-if="node.type === 'unary'"
    class="inline-flex items-center gap-0.5 rounded-md px-1 py-0.5 bg-purple-500/10 border border-purple-500/20"
  >
    <span class="text-[11px] text-purple-400 font-mono font-bold mr-0.5">
      {{ node.func === 'negate' ? '-' : node.func }}
    </span>
    <span v-if="node.func !== 'negate'" class="text-[10px] text-purple-400/60">(</span>
    <ExprNode
      :node="node.operand"
      :variables="variables"
      :depth="depth + 1"
      @update="val => emitUpdate({ ...node, operand: val })"
    />
    <span v-if="node.func !== 'negate'" class="text-[10px] text-purple-400/60">)</span>
    <button
      @click="emitUpdate(node.operand)"
      class="w-4 h-4 flex items-center justify-center text-dark-500 hover:text-red-400 rounded transition-colors"
      title="Remove negation"
    >
      <i class="fas fa-times text-[8px]"></i>
    </button>
  </div>

  <!-- Function node: func(args...) -->
  <div
    v-else-if="node.type === 'func'"
    class="inline-flex flex-wrap items-center gap-0.5 rounded-md px-1.5 py-0.5 bg-cyan-500/10 border border-cyan-500/20"
  >
    <span class="text-[11px] text-cyan-400 font-mono font-bold">{{ node.name }}</span>
    <span class="text-[10px] text-cyan-400/60">(</span>
    <template v-for="(arg, i) in node.args" :key="i">
      <span v-if="i > 0" class="text-[10px] text-dark-500 mx-0.5">,</span>
      <ExprNode
        :node="arg"
        :variables="variables"
        :depth="depth + 1"
        @update="val => updateFuncArg(i, val)"
      />
    </template>
    <span class="text-[10px] text-cyan-400/60">)</span>
    <button
      @click="unwrapFunc"
      class="w-4 h-4 flex items-center justify-center text-dark-500 hover:text-red-400 rounded transition-colors ml-0.5"
      title="Remove function wrapper"
    >
      <i class="fas fa-times text-[8px]"></i>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  PriceSources,
  MathOperators,
  isExprLeaf,
  createExprLeaf,
} from '../../utils/condition-types.js'

const props = defineProps({
  node: {
    type: Object,
    required: true,
  },
  variables: {
    type: Array,
    default: () => [],
  },
  depth: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['update'])

const priceSources = PriceSources
const mathOperators = MathOperators

const isLeaf = computed(() => isExprLeaf(props.node))

function emitUpdate(newNode) {
  emit('update', newNode)
}

function changeLeafType(newType) {
  if (newType === 'price') {
    emitUpdate(createExprLeaf('price'))
  } else if (newType === 'variable') {
    emitUpdate(createExprLeaf('variable', { variableId: props.variables[0]?.id || '' }))
  } else if (newType === 'constant') {
    emitUpdate(createExprLeaf('constant', { value: 0 }))
  }
}

function updateFuncArg(index, newArg) {
  const newArgs = [...props.node.args]
  newArgs[index] = newArg
  emitUpdate({ ...props.node, args: newArgs })
}

/**
 * Unwrap a function: replace this func node with its first argument
 */
function unwrapFunc() {
  if (props.node.args && props.node.args.length > 0) {
    emitUpdate(props.node.args[0])
  }
}
</script>

<style scoped>
/* Hide number input spinners */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  -moz-appearance: textfield;
}
</style>
