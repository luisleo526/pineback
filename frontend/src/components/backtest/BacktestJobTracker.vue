<template>
  <div class="p-4">
    <!-- Job list -->
    <div v-if="jobs.length > 0" class="space-y-2">
      <h4 class="text-xs font-medium text-white/40 mb-2">
        <i class="fas fa-history mr-1.5 text-[10px]"></i>
        Recent Jobs
      </h4>

      <div
        v-for="job in jobs"
        :key="job.id"
        class="flex items-center justify-between px-3 py-2.5 rounded-lg border border-white/[0.04] hover:border-white/[0.08] transition-all cursor-pointer"
        style="background: rgba(255,255,255,0.02);"
        @click="viewResult(job)"
      >
        <div class="flex items-center gap-2 min-w-0">
          <!-- Status indicator -->
          <span
            v-if="job.status === 'running' || job.status === 'pending'"
            class="w-2 h-2 rounded-full bg-amber-400 pulse-dot flex-shrink-0"
          ></span>
          <span
            v-else-if="job.status === 'completed'"
            class="w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0"
          ></span>
          <span
            v-else
            class="w-2 h-2 rounded-full bg-red-400 flex-shrink-0"
          ></span>

          <div class="min-w-0">
            <div class="text-xs text-white/70 truncate">
              {{ job.timeframe }} &middot; {{ job.start_date }} &rarr; {{ job.end_date }}
            </div>
            <div class="text-[10px] text-white/30 mt-0.5">
              {{ job.status }}
            </div>
          </div>
        </div>

        <div v-if="job.status === 'completed' && job.result" class="text-xs text-right flex-shrink-0 ml-2">
          <span
            :class="[
              'font-medium',
              (job.result.total_return_pct || 0) >= 0 ? 'text-emerald-400' : 'text-red-400',
            ]"
          >
            {{ (job.result.total_return_pct || 0) >= 0 ? '+' : '' }}{{ (job.result.total_return_pct || 0).toFixed(2) }}%
          </span>
        </div>

        <i
          v-if="job.status === 'running' || job.status === 'pending'"
          class="fas fa-spinner fa-spin text-[10px] text-white/30 ml-2 flex-shrink-0"
        ></i>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="py-6 text-center">
      <i class="fas fa-flask text-2xl text-white/10 mb-2"></i>
      <p class="text-xs text-white/30">No backtests yet</p>
      <p class="text-[10px] text-white/20 mt-1">Configure and run a backtest above</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { submitBacktest as apiSubmitBacktest, getBacktest } from '../../api/index.js'

const emit = defineEmits(['view-result'])

const jobs = ref([])

// Submit a new backtest and start polling
async function submitBacktest(config) {
  let job = null

  try {
    const response = await apiSubmitBacktest(config)
    job = {
      id: response.id,
      status: response.status || 'pending',
      timeframe: config.timeframe,
      start_date: config.start_date,
      end_date: config.end_date,
      result: null,
    }
    // Prepend to list (newest first)
    jobs.value.unshift(job)
  } catch (e) {
    console.error('Failed to submit backtest:', e)
    return
  }

  // Poll for completion
  await pollJob(job)
}

async function pollJob(job) {
  const POLL_INTERVAL = 2500
  const MAX_POLLS = 240 // ~10 min max

  for (let i = 0; i < MAX_POLLS; i++) {
    try {
      const data = await getBacktest(job.id)
      job.status = data.status

      if (data.status === 'completed') {
        job.result = data.result_json || data.result
        return
      }
      if (data.status === 'failed') {
        job.error = data.error_message || 'Backtest failed'
        return
      }
    } catch (e) {
      console.error('Poll error:', e)
    }

    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL))
  }
}

function viewResult(job) {
  if (job.status === 'completed' && job.result) {
    emit('view-result', job.result)
  }
}

// Expose for parent (BacktestApp) to call
defineExpose({ submitBacktest })
</script>
