<template>
  <div class="variables-panel">
    <!-- Header -->
    <div class="flex items-center justify-between mb-3">
      <h4 class="text-sm font-semibold text-white flex items-center gap-2">
        <i class="fas fa-cube text-yellow-400"></i>
        Custom Variables
      </h4>
      <button
        @click="addVariable"
        class="px-2 py-1 text-xs rounded transition-colors bg-dark-700 hover:bg-dark-600 text-dark-300 hover:text-white"
      >
        <i class="fas fa-plus mr-1"></i>Add
      </button>
    </div>

    <p class="text-xs text-dark-500 mb-3">
      Define reusable variables for building conditions
    </p>

    <!-- Variables List -->
    <div class="space-y-2">
      <div
        v-for="(variable, index) in variables"
        :key="variable.id"
        class="variable-card bg-dark-800/50 rounded-lg border border-dark-700 p-3"
      >
        <!-- Variable Name -->
        <div class="flex items-center gap-2 mb-1">
          <input
            v-model="variable.name"
            @input="updateVariable(index)"
            type="text"
            placeholder="Variable name"
            :class="[
              'flex-1 bg-dark-700 rounded px-2 py-1 text-sm text-white focus:outline-none font-mono',
              isDuplicate(variable)
                ? 'border border-red-500/70 focus:border-red-400'
                : 'border border-dark-600 focus:border-accent-500'
            ]"
          />
          <button
            @click="deleteVariable(index)"
            class="w-6 h-6 flex items-center justify-center text-dark-400 hover:text-red-400 hover:bg-dark-700 rounded transition-colors"
            title="Delete variable"
          >
            <i class="fas fa-times text-xs"></i>
          </button>
        </div>
        <p v-if="isDuplicate(variable)" class="text-xs text-red-400 mb-1 ml-0.5">
          <i class="fas fa-exclamation-circle mr-1"></i>Duplicate name, please use a different name
        </p>

        <!-- Variable Type Selector -->
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs text-dark-400">=</span>
          <div class="flex gap-1 flex-wrap">
            <button
              @click="changeVariableType(index, 'price')"
              :class="[
                'px-2 py-1 text-xs rounded transition-colors',
                getVariableType(variable) === 'price'
                  ? 'bg-blue-500/20 text-blue-400 ring-1 ring-blue-500/50'
                  : 'bg-dark-700 text-dark-400 hover:text-white'
              ]"
            >
              <i class="fas fa-tag mr-1"></i>Price
            </button>
            <button
              @click="changeVariableType(index, 'indicator')"
              :class="[
                'px-2 py-1 text-xs rounded transition-colors',
                getVariableType(variable) === 'indicator'
                  ? 'bg-amber-500/20 text-amber-400 ring-1 ring-amber-500/50'
                  : 'bg-dark-700 text-dark-400 hover:text-white'
              ]"
            >
              <i class="fas fa-chart-line mr-1"></i>Function
            </button>
            <button
              @click="changeVariableType(index, 'expression')"
              :class="[
                'px-2 py-1 text-xs rounded transition-colors',
                getVariableType(variable) === 'expression'
                  ? 'bg-green-500/20 text-green-400 ring-1 ring-green-500/50'
                  : 'bg-dark-700 text-dark-400 hover:text-white'
              ]"
            >
              <i class="fas fa-calculator mr-1"></i>Expression
            </button>
          </div>
        </div>

        <!-- Price Source Selection -->
        <div v-if="getVariableType(variable) === 'price'" class="flex flex-wrap items-center gap-2">
          <select
            v-model="variable.source"
            @change="updateVariable(index)"
            class="bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
          >
            <option v-for="src in priceSources" :key="src.id" :value="src.id">
              {{ src.label }}
            </option>
          </select>
        </div>

        <!-- Expression Builder -->
        <div v-else-if="getVariableType(variable) === 'expression'">
          <ExpressionBuilder
            :modelValue="ensureExprTree(variable.expression)"
            :variables="getOtherVariables(variable.id)"
            @update:modelValue="val => updateExpression(index, val)"
          />
        </div>

        <!-- Indicator Selection -->
        <div v-else-if="getVariableType(variable) === 'indicator'" class="space-y-2">
          <div class="flex flex-wrap items-center gap-2">
            <select
              v-model="variable.indicator"
              @change="onIndicatorChange(index)"
              class="bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
            >
              <optgroup v-for="cat in indicatorCategories" :key="cat.id" :label="cat.label">
                <option
                  v-for="ind in getIndicatorsByCategory(cat.id)"
                  :key="ind.id"
                  :value="ind.id"
                >
                  {{ ind.label }} {{ ind.outputs ? `(${ind.outputs.length} outputs)` : '' }}
                </option>
              </optgroup>
            </select>

            <!-- Indicator Parameters -->
            <template v-if="getIndicator(variable.indicator)">
              <template v-for="param in getIndicator(variable.indicator).params" :key="param.id">
                <template v-if="param.type === 'source'">
                  <select
                    v-model="variable.params[param.id]"
                    @change="updateVariable(index)"
                    class="bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
                  >
                    <option v-for="src in priceSources" :key="src.id" :value="src.id">
                      {{ src.label }}
                    </option>
                  </select>
                </template>
                <template v-else-if="param.type === 'int' || param.type === 'float'">
                  <div class="flex items-center gap-1">
                    <span class="text-xs text-dark-500">{{ param.label }}:</span>
                    <input
                      v-model.number="variable.params[param.id]"
                      @input="updateVariable(index)"
                      type="number"
                      :min="param.min"
                      :max="param.max"
                      :step="param.type === 'float' ? 0.1 : 1"
                      class="w-14 bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
                    />
                  </div>
                </template>
              </template>
            </template>
          </div>

          <!-- Output Selector for multi-output indicators -->
          <div v-if="hasMultipleOutputs(variable.indicator)" class="flex items-center gap-2 flex-wrap">
            <span class="text-xs text-dark-400">Output:</span>
            <button
              v-for="(output, oIdx) in getOutputs(variable.indicator)"
              :key="output.id"
              @click="changeVariableOutputIndex(index, oIdx)"
              :class="[
                'px-2 py-0.5 text-xs rounded transition-colors border',
                (variable.outputIndex ?? 0) === oIdx
                  ? 'bg-green-500/20 text-green-400 border-green-500/50'
                  : 'bg-dark-700 text-dark-500 border-dark-600 hover:text-dark-300'
              ]"
            >
              {{ output.label }}
            </button>
          </div>
        </div>

        <!-- Preview (skip for expression type — ExpressionBuilder has its own) -->
        <div v-if="getVariableType(variable) !== 'expression'" class="mt-2 pt-2 border-t border-dark-700">
          <code class="text-xs text-dark-400 font-mono">
            {{ variable.name }} = {{ getVariablePinescript(variable) }}
          </code>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="variables.length === 0" class="text-center py-6 text-dark-500">
        <i class="fas fa-cube text-2xl mb-2 opacity-50"></i>
        <p class="text-xs">No custom variables</p>
        <p class="text-xs mt-1">Define variables to reuse across multiple conditions</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import ExpressionBuilder from './ExpressionBuilder.vue'
import {
  IndicatorList,
  IndicatorCategories,
  PriceSources,
  getIndicator as getIndicatorById,
  getPriceSource,
  createVariable,
  deepClone,
  isMultiOutput,
  getIndicatorOutputs,
  getDefaultOutputIndex,
  collectAllNames,
  generateUniqueName,
  migrateExpression,
} from '../../utils/condition-types.js'

const props = defineProps({
  variables: {
    type: Array,
    default: () => [],
  },
  inputs: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:variables'])

const indicatorCategories = IndicatorCategories
const priceSources = PriceSources

import { computed } from 'vue'

/**
 * Returns a Set of variable names that are duplicated (appear more than once
 * across variables and inputs).
 */
const duplicateNames = computed(() => {
  const dupes = new Set()
  const allNames = collectAllNames([], props.inputs)
  props.variables.forEach(v => {
    if (v.name && allNames.has(v.name)) {
      dupes.add(v.name)
    }
    allNames.add(v.name)
  })
  // Also check within variables for self-duplicates
  const seen = new Set()
  props.variables.forEach(v => {
    if (v.name && seen.has(v.name)) {
      dupes.add(v.name)
    }
    seen.add(v.name)
  })
  return dupes
})

function isDuplicate(variable) {
  return variable.name && duplicateNames.value.has(variable.name)
}

function getIndicatorsByCategory(categoryId) {
  return IndicatorList.filter(ind => ind.category === categoryId)
}

function getIndicator(id) {
  return getIndicatorById(id)
}

function getVariableType(variable) {
  // Support both old format (no type field) and new format
  return variable.type || 'indicator'
}

function getOtherVariables(currentId) {
  // Get variables that can be referenced (excluding current to prevent circular reference)
  return props.variables.filter(v => v.id !== currentId)
}

function addVariable() {
  const newVar = createVariable()
  const existingNames = collectAllNames(props.variables, props.inputs)
  newVar.name = generateUniqueName(newVar.name, existingNames)
  const updated = [...props.variables, newVar]
  emit('update:variables', updated)
}

function updateVariable(index) {
  const updated = deepClone(props.variables)
  emit('update:variables', updated)
}

function deleteVariable(index) {
  const updated = [...props.variables]
  updated.splice(index, 1)
  emit('update:variables', updated)
}

function changeVariableType(index, newType) {
  const updated = deepClone(props.variables)
  const variable = updated[index]
  const currentType = getVariableType(variable)
  
  if (currentType === newType) return
  
  if (newType === 'price') {
    // Convert to price type
    updated[index] = {
      id: variable.id,
      name: variable.name,
      type: 'price',
      source: 'close',
    }
  } else if (newType === 'expression') {
    // Convert to expression type
    updated[index] = {
      id: variable.id,
      name: variable.name,
      type: 'expression',
      expression: {
        left: { type: 'price', source: 'close' },
        operator: '-',
        right: { type: 'price', source: 'open' },
      },
    }
  } else {
    // Convert to indicator type
    updated[index] = {
      id: variable.id,
      name: variable.name,
      type: 'indicator',
      indicator: 'sma',
      params: { source: 'close', period: 14 },
    }
  }
  
  emit('update:variables', updated)
}

function hasMultipleOutputs(indicatorId) {
  return isMultiOutput(indicatorId)
}

function getOutputs(indicatorId) {
  return getIndicatorOutputs(indicatorId)
}

function changeVariableOutputIndex(index, outputIndex) {
  const updated = deepClone(props.variables)
  updated[index].outputIndex = outputIndex
  emit('update:variables', updated)
}

function onIndicatorChange(index) {
  const variable = props.variables[index]
  const indicator = getIndicatorById(variable.indicator)
  
  if (indicator) {
    // Reset params to defaults
    const params = {}
    indicator.params.forEach(p => {
      params[p.id] = p.default
    })
    
    const updated = deepClone(props.variables)
    updated[index].params = params
    
    // Set default output index for multi-output indicators
    if (isMultiOutput(variable.indicator)) {
      updated[index].outputIndex = getDefaultOutputIndex(variable.indicator)
    } else {
      delete updated[index].outputIndex
    }
    
    emit('update:variables', updated)
  }
}

// Expression builder functions

/**
 * Ensure expression is in the new tree format (migrate old flat format)
 */
function ensureExprTree(expr) {
  return migrateExpression(expr)
}

/**
 * Update expression tree for a variable
 */
function updateExpression(index, newExprTree) {
  const updated = deepClone(props.variables)
  updated[index].expression = newExprTree
  emit('update:variables', updated)
}

function getVariablePinescript(variable) {
  const varType = getVariableType(variable)
  
  if (varType === 'price') {
    const source = getPriceSource(variable.source)
    return source?.pinescript || variable.source || 'close'
  }
  
  // Expression preview is handled by ExpressionBuilder component
  if (varType === 'expression') return '...'
  
  const indicator = getIndicatorById(variable.indicator)
  if (!indicator) return '...'
  
  try {
    if (isMultiOutput(variable.indicator)) {
      const outputIndex = variable.outputIndex ?? 0
      return indicator.pinescript(variable.params, outputIndex)
    }
    return indicator.pinescript(variable.params)
  } catch (e) {
    return '...'
  }
}
</script>

<style scoped>
.variable-card {
  transition: border-color 0.2s ease;
}

.variable-card:hover {
  border-color: #475569;
}

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
