<template>
  <div class="signal-condition-builder h-full flex flex-col" style="background: linear-gradient(180deg, rgba(14,17,32,0.5) 0%, rgba(8,10,22,0.8) 100%);">
    <!-- Signal Tabs -->
    <div class="flex p-1.5 gap-1 border-b border-white/[0.04] overflow-x-auto" style="background: rgba(14,17,32,0.4);">
      <button
        v-for="signal in signalList"
        :key="signal.id"
        :data-signal="signal.id"
        @click="activeSignal = signal.id"
        :class="[
          'flex-1 min-w-0 px-2 sm:px-4 py-2.5 text-xs sm:text-xs font-medium transition-all relative whitespace-nowrap rounded-lg',
          activeSignal === signal.id
            ? 'text-white bg-white/[0.08] shadow-sm'
            : 'text-white/40 hover:text-white/70 hover:bg-white/[0.03]',
        ]"
      >
        <span :class="getSignalColorClass(signal.id)">
          <i :class="['fas sm:mr-1.5 mr-1', getSignalIcon(signal.id)]" style="font-size: 10px;"></i>
          <span class="hidden sm:inline">{{ signal.label }}</span>
          <span class="sm:hidden">{{ signal.shortLabel || signal.label }}</span>
        </span>
        <!-- Condition count badge -->
        <span
          v-if="getConditionCount(signal.id) > 0"
          class="ml-1 sm:ml-1.5 px-1.5 py-0.5 text-[10px] rounded-full bg-white/[0.1] text-white/60"
        >
          {{ getConditionCount(signal.id) }}
        </span>
      </button>
    </div>

    <!-- Signal Content -->
    <div class="flex-1 overflow-y-auto p-2.5 sm:p-5">
      <div v-for="signal in signalList" :key="signal.id" v-show="activeSignal === signal.id">
        <!-- Enable Toggle -->
        <div class="flex items-center justify-between mb-4 pb-4 border-b border-white/[0.04]">
          <div class="flex items-center gap-3">
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                :checked="signals[signal.id].enabled"
                @change="toggleSignalEnabled(signal.id)"
                class="sr-only peer"
              />
              <div class="w-9 h-5 bg-white/[0.08] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-blue-500 peer-checked:to-indigo-500"></div>
            </label>
            <span class="text-sm text-white/70">
              Enable {{ signal.label }} signal
            </span>
          </div>
          <span class="text-xs text-white/30">
            {{ getConditionSummary(signal.id) }}
          </span>
        </div>

        <!-- Condition Groups -->
        <div v-if="signals[signal.id].enabled" class="space-y-4">
          <template v-for="(group, index) in signals[signal.id].groups" :key="group.id">
            <!-- OR Divider -->
            <div v-if="index > 0" class="flex items-center justify-center py-2">
              <div class="flex-1 border-t border-white/[0.04]"></div>
              <span class="px-4 py-1 rounded-full text-[10px] font-semibold text-amber-400/80 uppercase mx-4 tracking-widest" style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.15);">
                OR
              </span>
              <div class="flex-1 border-t border-white/[0.04]"></div>
            </div>

            <!-- Condition Group -->
            <ConditionGroup
              :group="group"
              :groupIndex="index"
              :variables="variables"
              :inputs="inputs"
              :maxConditions="Infinity"
              @update:group="updateGroup(signal.id, index, $event)"
              @delete="deleteGroup(signal.id, index)"
              @create-input="$emit('create-input', $event)"
            />
          </template>

          <!-- Add Group Button -->
          <button
            @click="addGroup(signal.id)"
            class="w-full py-3 px-4 border border-dashed border-white/[0.08] rounded-xl text-xs text-white/30 hover:text-white/70 hover:border-indigo-500/30 hover:bg-indigo-500/[0.03] transition-all flex items-center justify-center gap-2"
          >
            <i class="fas fa-plus text-[10px]"></i>
            Add Condition Group (OR)
          </button>

          <!-- Empty State -->
          <div v-if="signals[signal.id].groups.length === 0" class="text-center py-8">
            <div class="w-16 h-16 bg-dark-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <i :class="['fas text-2xl', getSignalIcon(signal.id), getSignalColorClass(signal.id)]"></i>
            </div>
            <p class="text-dark-400 mb-2">No {{ signal.label }} conditions set</p>
            <p class="text-xs text-dark-500">Click the button above to add a condition group</p>
          </div>
        </div>

        <!-- Disabled State -->
        <div v-else class="text-center py-12">
          <div class="w-16 h-16 bg-dark-800 rounded-2xl flex items-center justify-center mx-auto mb-4 opacity-50">
            <i :class="['fas text-2xl', getSignalIcon(signal.id), 'text-dark-500']"></i>
          </div>
          <p class="text-dark-500 mb-2">{{ signal.label }} signal is disabled</p>
          <p class="text-xs text-dark-600">Toggle the switch above to set conditions</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ConditionGroup from './ConditionGroup.vue'
import { SignalList, createConditionGroup, deepClone } from '../../utils/condition-types.js'

const props = defineProps({
  signals: {
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

const emit = defineEmits(['update:signals', 'create-input'])

const signalList = SignalList
const activeSignal = ref('longEntry')


function getSignalIcon(signalId) {
  const icons = {
    longEntry: 'fa-arrow-trend-up',
    longExit: 'fa-arrow-right-from-bracket',
    shortEntry: 'fa-arrow-trend-down',
    shortExit: 'fa-arrow-right-from-bracket',
  }
  return icons[signalId] || 'fa-signal'
}

function getSignalColorClass(signalId) {
  const colors = {
    longEntry: 'text-green-400',
    longExit: 'text-red-400',
    shortEntry: 'text-red-400',
    shortExit: 'text-green-400',
  }
  return colors[signalId] || 'text-white'
}

function getConditionCount(signalId) {
  const signal = props.signals[signalId]
  if (!signal || !signal.enabled) return 0
  return signal.groups.reduce((sum, g) => sum + g.conditions.length, 0)
}

function getConditionSummary(signalId) {
  const signal = props.signals[signalId]
  if (!signal || !signal.enabled) return ''
  
  const groupCount = signal.groups.length
  const condCount = getConditionCount(signalId)
  
  if (groupCount === 0) return 'No conditions set'
  return `${groupCount} group(s), ${condCount} condition(s)`
}

function toggleSignalEnabled(signalId) {
  const updated = deepClone(props.signals)
  updated[signalId].enabled = !updated[signalId].enabled
  emit('update:signals', updated)
}

function addGroup(signalId) {
  const updated = deepClone(props.signals)
  const newGroup = createConditionGroup()
  updated[signalId].groups.push(newGroup)
  emit('update:signals', updated)
}

function updateGroup(signalId, index, updatedGroup) {
  const updated = deepClone(props.signals)
  updated[signalId].groups[index] = updatedGroup
  emit('update:signals', updated)
}

function deleteGroup(signalId, index) {
  const updated = deepClone(props.signals)
  updated[signalId].groups.splice(index, 1)
  emit('update:signals', updated)
}



</script>

<style scoped>
.signal-condition-builder {
  scrollbar-width: thin;
  scrollbar-color: #334155 transparent;
}

.signal-condition-builder::-webkit-scrollbar {
  width: 6px;
}

.signal-condition-builder::-webkit-scrollbar-track {
  background: transparent;
}

.signal-condition-builder::-webkit-scrollbar-thumb {
  background-color: #334155;
  border-radius: 3px;
}
</style>
