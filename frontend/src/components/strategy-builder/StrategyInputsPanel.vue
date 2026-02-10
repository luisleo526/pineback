<template>
  <div class="strategy-inputs-panel">
    <!-- Header -->
    <div class="flex items-center justify-between mb-3">
      <h4 class="text-sm font-semibold text-white flex items-center gap-2">
        <i class="fas fa-sliders-h text-cyan-400"></i>
        Strategy Inputs
      </h4>
      <button
        @click="addInput"
        class="px-2 py-1 text-xs rounded transition-colors bg-dark-700 hover:bg-dark-600 text-dark-300 hover:text-white"
      >
        <i class="fas fa-plus mr-1"></i>Add
      </button>
    </div>

    <p class="text-xs text-dark-500 mb-3">
      Define adjustable parameters for use in TradingView
    </p>

    <!-- Inputs List -->
    <div class="space-y-2">
      <div
        v-for="(input, index) in inputs"
        :key="input.id"
        class="input-card bg-dark-800/50 rounded-lg border border-dark-700 p-3"
      >
        <div class="flex items-start gap-2">
          <!-- Input Name -->
          <div class="flex-1 min-w-0 space-y-2">
            <div class="flex items-center gap-2">
              <input
                :value="input.name"
                @input="input.name = $event.target.value.replace(/[^a-zA-Z0-9_]/g, ''); updateInput(index)"
                type="text"
                placeholder="myParam"
                :class="[
                  'flex-1 min-w-0 bg-dark-700 rounded px-2 py-1.5 text-sm text-white focus:outline-none font-mono',
                  isDuplicate(input)
                    ? 'border border-red-500/70 focus:border-red-400'
                    : 'border border-dark-600 focus:border-accent-500'
                ]"
              />
              <select
                v-model="input.type"
                @change="onTypeChange(index)"
                class="w-16 flex-shrink-0 bg-dark-700 border border-dark-600 rounded px-1.5 py-1.5 text-[11px] text-white focus:outline-none focus:border-accent-500"
              >
                <option value="int">Int</option>
                <option value="float">Float</option>
                <option value="bool">Bool</option>
              </select>
            </div>
            <p v-if="isDuplicate(input)" class="text-xs text-red-400 ml-0.5">
              <i class="fas fa-exclamation-circle mr-1"></i>Duplicate name
            </p>

            <!-- Value Configuration -->
            <div class="grid grid-cols-3 gap-1.5 text-xs">
              <template v-if="input.type === 'int' || input.type === 'float'">
                <div>
                  <span class="text-dark-500 text-[10px] block mb-0.5">Default</span>
                  <input
                    v-model.number="input.default"
                    @input="updateInput(index)"
                    type="number"
                    :step="input.type === 'float' ? 0.1 : 1"
                    class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1.5 text-white focus:outline-none focus:border-accent-500"
                  />
                </div>
                <div>
                  <span class="text-dark-500 text-[10px] block mb-0.5">Min</span>
                  <input
                    v-model.number="input.min"
                    @input="updateInput(index)"
                    type="number"
                    :step="input.type === 'float' ? 0.1 : 1"
                    class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1.5 text-white focus:outline-none focus:border-accent-500"
                  />
                </div>
                <div>
                  <span class="text-dark-500 text-[10px] block mb-0.5">Max</span>
                  <input
                    v-model.number="input.max"
                    @input="updateInput(index)"
                    type="number"
                    :step="input.type === 'float' ? 0.1 : 1"
                    placeholder="—"
                    class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1.5 text-white focus:outline-none focus:border-accent-500"
                  />
                </div>
              </template>
              <template v-else-if="input.type === 'bool'">
                <div class="col-span-3">
                  <span class="text-dark-500 text-[10px] block mb-0.5">Default</span>
                  <select
                    v-model="input.default"
                    @change="updateInput(index)"
                    class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1.5 text-white focus:outline-none focus:border-accent-500"
                  >
                    <option :value="true">true</option>
                    <option :value="false">false</option>
                  </select>
                </div>
              </template>
            </div>
          </div>

          <!-- Delete Button -->
          <button
            @click="deleteInput(index)"
            class="w-6 h-6 flex items-center justify-center text-dark-400 hover:text-red-400 hover:bg-dark-700 rounded transition-colors"
            title="Delete input"
          >
            <i class="fas fa-times text-xs"></i>
          </button>
        </div>

        <!-- Preview -->
        <div class="mt-2 pt-2 border-t border-dark-700 overflow-hidden">
          <code class="text-[10px] text-dark-400 font-mono break-all leading-relaxed">
            {{ getInputPinescript(input) }}
          </code>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="inputs.length === 0" class="text-center py-6 text-dark-500">
        <i class="fas fa-sliders-h text-2xl mb-2 opacity-50"></i>
        <p class="text-xs">No strategy inputs</p>
        <p class="text-xs mt-1">Inputs can be adjusted in real-time in TradingView</p>
      </div>
    </div>

    <!-- Auto-generated Inputs Info -->
    <div v-if="autoInputs.length > 0" class="mt-4 pt-4 border-t border-dark-700">
      <h5 class="text-xs font-medium text-dark-400 mb-2">
        <i class="fas fa-magic mr-1"></i>
        Auto-generated Inputs
      </h5>
      <div class="space-y-1">
        <div
          v-for="input in autoInputs"
          :key="input.id"
          class="text-xs text-dark-500 font-mono"
        >
          {{ input.name }} = {{ input.default }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { createInput, deepClone, collectAllNames, generateUniqueName } from '../../utils/condition-types.js'

const props = defineProps({
  inputs: {
    type: Array,
    default: () => [],
  },
  autoInputs: {
    type: Array,
    default: () => [],
  },
  variables: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:inputs'])

/**
 * Returns a Set of input names that are duplicated (appear more than once
 * across inputs and variables).
 */
const duplicateNames = computed(() => {
  const dupes = new Set()
  const allNames = collectAllNames(props.variables, [])
  props.inputs.forEach(i => {
    if (i.name && allNames.has(i.name)) {
      dupes.add(i.name)
    }
    allNames.add(i.name)
  })
  // Also check within inputs for self-duplicates
  const seen = new Set()
  props.inputs.forEach(i => {
    if (i.name && seen.has(i.name)) {
      dupes.add(i.name)
    }
    seen.add(i.name)
  })
  return dupes
})

function isDuplicate(input) {
  return input.name && duplicateNames.value.has(input.name)
}

function addInput() {
  const baseName = `param${props.inputs.length + 1}`
  const existingNames = collectAllNames(props.variables, props.inputs)
  const uniqueName = generateUniqueName(baseName, existingNames)
  const newInput = createInput('int', uniqueName, 14)
  emit('update:inputs', [...props.inputs, newInput])
}

function updateInput(index) {
  const updated = deepClone(props.inputs)
  emit('update:inputs', updated)
}

function deleteInput(index) {
  const updated = [...props.inputs]
  updated.splice(index, 1)
  emit('update:inputs', updated)
}

function onTypeChange(index) {
  const updated = deepClone(props.inputs)
  const input = updated[index]
  
  // Set appropriate default based on type
  if (input.type === 'bool') {
    input.default = true
    input.min = undefined
    input.max = undefined
  } else {
    input.default = input.type === 'float' ? 1.0 : 1
    input.min = input.type === 'float' ? 0.1 : 1
    input.max = undefined
  }
  
  emit('update:inputs', updated)
}

function getInputPinescript(input) {
  const name = toCamelCase(input.name)
  
  if (input.type === 'int') {
    let code = `${name} = input.int(${input.default}, "${input.name}"`
    if (input.min !== undefined && input.min !== null) {
      code += `, minval=${input.min}`
    }
    if (input.max !== undefined && input.max !== null) {
      code += `, maxval=${input.max}`
    }
    return code + ')'
  }
  
  if (input.type === 'float') {
    let code = `${name} = input.float(${input.default}, "${input.name}"`
    if (input.min !== undefined && input.min !== null) {
      code += `, minval=${input.min}`
    }
    if (input.max !== undefined && input.max !== null) {
      code += `, maxval=${input.max}`
    }
    return code + ')'
  }
  
  if (input.type === 'bool') {
    return `${name} = input.bool(${input.default}, "${input.name}")`
  }
  
  return ''
}

function toCamelCase(str) {
  return str
    .replace(/[^a-zA-Z0-9\s]/g, '')
    .split(/\s+/)
    .map((word, index) => {
      if (index === 0) return word.toLowerCase()
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    })
    .join('')
}
</script>

<style scoped>
.input-card {
  transition: border-color 0.2s ease;
}

.input-card:hover {
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
