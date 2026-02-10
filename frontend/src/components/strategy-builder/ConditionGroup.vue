<template>
  <div class="condition-group glass-card rounded-2xl">
    <!-- Group Header -->
    <div class="flex items-center justify-between px-3 sm:px-4 py-2.5" style="background: rgba(255,255,255,0.02);">
      <div class="flex items-center gap-2 min-w-0">
        <span class="text-[11px] font-semibold text-white/50 uppercase tracking-wider flex-shrink-0">
          Group {{ groupIndex + 1 }}
        </span>
        <span class="text-[11px] text-white/25 truncate">
          {{ group.conditions.length }} condition(s)
        </span>
      </div>
      <button
        @click="$emit('delete')"
        class="w-8 h-8 sm:w-7 sm:h-7 flex items-center justify-center text-white/20 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all flex-shrink-0"
        title="Delete group"
      >
        <i class="fas fa-trash-alt text-[10px]"></i>
      </button>
    </div>

    <!-- Conditions -->
    <div class="p-2.5 sm:p-4 space-y-2">
      <template v-for="(condition, index) in group.conditions" :key="condition.id">
        <!-- AND Divider -->
        <div v-if="index > 0" class="flex items-center justify-center py-1">
          <div class="flex-1 border-t border-white/[0.04]"></div>
          <span class="mx-3 px-2.5 py-0.5 rounded-full text-[10px] font-semibold text-violet-400/80 uppercase tracking-widest" style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.15);">
            AND
          </span>
          <div class="flex-1 border-t border-white/[0.04]"></div>
        </div>

        <!-- Condition Row -->
        <ConditionRow
          :condition="condition"
          :variables="variables"
          :inputs="inputs"
          @update:condition="updateCondition(index, $event)"
          @delete="deleteCondition(index)"
          @create-input="$emit('create-input', $event)"
        />
      </template>

      <!-- Empty State -->
      <div v-if="group.conditions.length === 0" class="text-center py-8 text-white/20">
        <div class="w-12 h-12 mx-auto mb-3 rounded-xl flex items-center justify-center" style="background: rgba(99, 102, 241, 0.06); border: 1px solid rgba(99, 102, 241, 0.1);">
          <i class="fas fa-filter text-indigo-400/50"></i>
        </div>
        <p class="text-xs text-white/30">No conditions yet. Click the button below to add one.</p>
      </div>

      <!-- Add Condition Button -->
      <button
        @click="addCondition"
        class="w-full py-2.5 sm:py-2 px-4 border border-dashed border-white/[0.06] rounded-xl text-xs text-white/30 hover:text-white/70 hover:border-indigo-500/30 hover:bg-indigo-500/[0.03] transition-all flex items-center justify-center gap-2 min-h-[44px] sm:min-h-0"
      >
        <i class="fas fa-plus text-[10px]"></i>
        Add Condition (AND)
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ConditionRow from './ConditionRow.vue'
import { createCondition, deepClone } from '../../utils/condition-types.js'

const props = defineProps({
  group: {
    type: Object,
    required: true,
  },
  groupIndex: {
    type: Number,
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
  maxConditions: {
    type: Number,
    default: Infinity,
  },
})

const emit = defineEmits(['update:group', 'delete', 'create-input'])

function addCondition() {
  if (props.group.conditions.length >= props.maxConditions) return
  const newCondition = createCondition()
  const updatedGroup = deepClone(props.group)
  updatedGroup.conditions.push(newCondition)
  emit('update:group', updatedGroup)
}

function updateCondition(index, updatedCondition) {
  const updatedGroup = deepClone(props.group)
  updatedGroup.conditions[index] = updatedCondition
  emit('update:group', updatedGroup)
}

function deleteCondition(index) {
  const updatedGroup = deepClone(props.group)
  updatedGroup.conditions.splice(index, 1)
  emit('update:group', updatedGroup)
}
</script>

<style scoped>
.condition-group {
  transition: box-shadow 0.2s ease;
}

.condition-group:hover {
  box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.2);
}
</style>
