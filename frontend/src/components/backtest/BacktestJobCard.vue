<template>
  <div class="rounded-xl p-3 transition-all" :style="cardStyle">
    <!-- Header: status icon + strategy name + timeframe + mode -->
    <div class="flex items-center gap-2 mb-1.5">
      <span :class="statusIconClass">
        <i :class="statusIcon"></i>
      </span>
      <span class="text-xs font-medium text-white/80 truncate flex-1">{{ job.strategy_name || 'Strategy' }}</span>
      <span class="text-[10px] text-white/30">{{ job.timeframe }} {{ job.mode === 'magnifier' ? 'mag' : 'std' }}</span>
    </div>

    <!-- Running: progress bar + message -->
    <div v-if="job.status === 'running'" class="mt-2">
      <div class="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
        <div class="h-full bg-accent-500 rounded-full transition-all duration-500" :style="{ width: `${job.progress}%` }"></div>
      </div>
      <div class="flex items-center justify-between mt-1">
        <span class="text-[10px] text-white/30">{{ job.progress_message }}</span>
        <span class="text-[10px] text-accent-400 font-medium">{{ job.progress }}%</span>
      </div>
    </div>

    <!-- Pending -->
    <div v-else-if="job.status === 'pending'" class="mt-2">
      <div class="h-1.5 bg-white/[0.06] rounded-full"></div>
      <span class="text-[10px] text-white/25 mt-1 block">Queued...</span>
    </div>

    <!-- Completed: summary + view button -->
    <div v-else-if="job.status === 'completed'" class="mt-2">
      <div class="flex items-center gap-3 text-[10px]">
        <span :class="job.total_return > 0 ? 'text-green-400' : 'text-red-400'">
          {{ job.total_return > 0 ? '+' : '' }}{{ job.total_return?.toFixed(2) }}%
        </span>
        <span class="text-white/30">Sharpe {{ job.sharpe_ratio?.toFixed(2) ?? '—' }}</span>
        <span class="text-white/30">{{ job.total_trades }} trades</span>
      </div>
      <button @click="$emit('view-result', job)" class="view-results-btn mt-2 w-full py-1.5 text-[10px] font-medium text-accent-400 bg-accent-500/10 hover:bg-accent-500/20 rounded-lg transition-colors">
        View Results
      </button>
    </div>

    <!-- Failed -->
    <div v-else-if="job.status === 'failed'" class="mt-2">
      <span class="text-[10px] text-red-400/70 line-clamp-2">{{ job.error_message || 'Unknown error' }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  job: {
    type: Object,
    required: true,
  },
})

defineEmits(['view-result'])

const statusIcon = computed(() => {
  switch (props.job.status) {
    case 'pending':   return 'fas fa-clock'
    case 'running':   return 'fas fa-spinner fa-spin'
    case 'completed': return 'fas fa-check-circle'
    case 'failed':    return 'fas fa-exclamation-circle'
    default:          return 'fas fa-question-circle'
  }
})

const statusIconClass = computed(() => {
  const base = 'text-xs flex-shrink-0'
  switch (props.job.status) {
    case 'pending':   return `${base} text-white/25`
    case 'running':   return `${base} text-accent-400`
    case 'completed': return `${base} text-green-400`
    case 'failed':    return `${base} text-red-400`
    default:          return `${base} text-white/25`
  }
})

const cardStyle = computed(() => {
  switch (props.job.status) {
    case 'pending':
      return {
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.04)',
      }
    case 'running':
      return {
        background: 'rgba(59,130,246,0.06)',
        border: '1px solid rgba(59,130,246,0.12)',
      }
    case 'completed':
      return {
        background: 'rgba(34,197,94,0.05)',
        border: '1px solid rgba(34,197,94,0.10)',
      }
    case 'failed':
      return {
        background: 'rgba(239,68,68,0.05)',
        border: '1px solid rgba(239,68,68,0.10)',
      }
    default:
      return {
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.04)',
      }
  }
})
</script>
