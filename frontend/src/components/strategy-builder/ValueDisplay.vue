<template>
  <div class="value-display inline-flex items-center gap-0.5">
    <!-- Empty / Placeholder -->
    <template v-if="value.type === 'empty' || !value.type">
      <span class="px-3 py-1 rounded-lg text-xs font-medium text-white/25 border border-dashed border-white/10 flex items-center gap-1.5 hover:border-indigo-500/30 hover:text-white/40 transition-all">
        <i class="fas fa-plus text-[9px]"></i>
        Select value
      </span>
    </template>

    <!-- Input Reference (strategy parameter) -->
    <template v-else-if="value.type === 'input'">
      <span class="px-2.5 py-1 rounded-lg text-xs font-mono font-medium flex items-center gap-1 text-cyan-300" style="background: linear-gradient(135deg, rgba(34,211,238,0.1), rgba(6,182,212,0.08)); border: 1px solid rgba(34,211,238,0.15);" title="Strategy input - adjustable in TradingView">
        <i class="fas fa-sliders-h" style="font-size: 8px;"></i>
        {{ value.inputName || 'Input' }}
      </span>
    </template>

    <!-- Constant Value -->
    <template v-else-if="value.type === 'constant'">
      <span class="px-2.5 py-1 rounded-lg text-xs font-mono font-medium text-cyan-300" style="background: linear-gradient(135deg, rgba(34,211,238,0.1), rgba(6,182,212,0.08)); border: 1px solid rgba(34,211,238,0.15);" title="Constant value - click to switch to function, price or variable">
        {{ value.value }}
      </span>
    </template>

    <!-- Variable Reference -->
    <template v-else-if="value.type === 'variable'">
      <span class="px-2.5 py-1 rounded-lg text-xs font-mono font-medium flex items-center gap-1 text-violet-300" style="background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(124,58,237,0.08)); border: 1px solid rgba(139,92,246,0.15);" title="Custom variable - click to switch to function, price or constant">
        <i class="fas fa-cube" style="font-size: 8px;"></i>
        {{ getVariableName(value.variableId) }}
      </span>
    </template>

    <!-- Price Source -->
    <template v-else-if="value.type === 'price'">
      <span class="px-2.5 py-1 rounded-lg text-xs font-mono font-medium text-blue-300" style="background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(37,99,235,0.08)); border: 1px solid rgba(59,130,246,0.15);" title="Price source - click to switch to function, variable or constant">
        {{ getPriceLabel(value.source) }}
      </span>
    </template>

    <!-- Indicator/Function -->
    <template v-else-if="value.type === 'indicator'">
      <span class="function-call inline-flex items-center">
        <!-- Function Name -->
        <span class="px-2 py-1 rounded-l-lg text-xs font-mono font-semibold text-amber-300" style="background: linear-gradient(135deg, rgba(245,158,11,0.12), rgba(217,119,6,0.08));">
          {{ getIndicatorLabel(value.indicator) }}
        </span>
        <!-- Opening Paren -->
        <span class="text-white/25 text-xs">(</span>
        <!-- Arguments -->
        <span class="args flex items-center gap-0.5">
          <template v-for="(param, index) in getIndicatorParams(value.indicator)" :key="param.id">
            <span v-if="index > 0" class="text-white/15 text-[10px]">,</span>
            <!-- Input Reference Param -->
            <span 
              v-if="isParamInput(param.id, value.params)"
              class="arg px-1.5 py-0.5 rounded text-[11px] font-mono text-cyan-300/80 flex items-center gap-0.5" style="background: rgba(34,211,238,0.06);"
              :title="'Linked strategy input (adjustable in TradingView)'"
            >
              <i class="fas fa-sliders-h" style="font-size: 7px;"></i>
              {{ getParamVariableName(param.id, value.params) }}
            </span>
            <!-- Variable Reference Param -->
            <span 
              v-else-if="isParamVariable(param.id, value.params)"
              class="arg px-1.5 py-0.5 rounded text-[11px] font-mono text-violet-300/80 flex items-center gap-0.5" style="background: rgba(139,92,246,0.06);"
              :title="'Linked variable (click to modify)'"
            >
              <i class="fas fa-cube" style="font-size: 7px;"></i>
              {{ getParamVariableName(param.id, value.params) }}
            </span>
            <!-- Constant Param -->
            <span 
              v-else
              class="arg px-1.5 py-0.5 rounded text-[11px] font-mono"
              :class="getParamClass(param.type)"
              :title="getArgTooltip(param)"
            >
              {{ getParamDisplay(param, value.params) }}
            </span>
          </template>
        </span>
        <!-- Closing Paren -->
        <span class="text-white/25 text-xs">)</span>
        <!-- Output selector badge for multi-output -->
        <span 
          v-if="getOutputLabel(value.indicator, value.outputIndex)"
          class="ml-1 px-1.5 py-0.5 bg-green-500/20 text-green-400 rounded text-xs font-mono"
        >
          .{{ getOutputLabel(value.indicator, value.outputIndex) }}
        </span>
      </span>
    </template>
  </div>
</template>

<script setup>
import { PriceSources, getIndicator, isMultiOutput, getIndicatorOutputs } from '../../utils/condition-types.js'

const props = defineProps({
  value: {
    type: Object,
    required: true,
  },
  variables: {
    type: Array,
    default: () => [],
  },
})

function getVariableName(id) {
  const variable = props.variables.find(v => v.id === id)
  return variable?.name || id
}

function getPriceLabel(sourceId) {
  const source = PriceSources.find(s => s.id === sourceId)
  return source?.label || sourceId
}

function getIndicatorLabel(indicatorId) {
  const indicator = getIndicator(indicatorId)
  return indicator?.label || indicatorId
}

function getIndicatorParams(indicatorId) {
  const indicator = getIndicator(indicatorId)
  return indicator?.params || []
}

function getParamClass(paramType) {
  switch (paramType) {
    case 'source':
      return 'text-blue-300/70'
    case 'int':
    case 'float':
      return 'text-cyan-300/70'
    default:
      return 'text-white/40'
  }
}

function isParamVariable(paramId, params) {
  const value = params?.[paramId]
  return value && typeof value === 'object' && (value.type === 'variable' || value.type === 'input')
}

function getParamVariableName(paramId, params) {
  const value = params?.[paramId]
  if (value && typeof value === 'object' && value.type === 'variable') {
    const variable = props.variables.find(v => v.id === value.variableId)
    return variable?.name || value.variableId
  }
  if (value && typeof value === 'object' && value.type === 'input') {
    return value.inputName || value.inputId || '?'
  }
  return ''
}

function isParamInput(paramId, params) {
  const value = params?.[paramId]
  return value && typeof value === 'object' && value.type === 'input'
}

function getParamDisplay(param, params) {
  const value = params?.[param.id] ?? param.default
  
  // Handle variable reference (shouldn't reach here, but just in case)
  if (value && typeof value === 'object' && value.type === 'variable') {
    return getParamVariableName(param.id, params)
  }
  
  if (param.type === 'source') {
    const source = PriceSources.find(s => s.id === value)
    return source?.label || value
  }
  
  return value
}

function getArgTooltip(param) {
  if (param.type === 'source') {
    return `${param.label}: Click to modify price source`
  }
  if (param.type === 'int' || param.type === 'float') {
    return `${param.label}: Click to modify value or create a strategy input`
  }
  return `${param.label}: Click to modify`
}

function getOutputLabel(indicatorId, outputIndex) {
  if (!isMultiOutput(indicatorId)) return null
  const outputs = getIndicatorOutputs(indicatorId)
  const idx = outputIndex ?? 0
  return outputs[idx]?.label || null
}
</script>

<style scoped>
.function-call {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.06) 0%, rgba(217, 119, 6, 0.03) 100%);
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
  padding: 1px;
}

</style>
