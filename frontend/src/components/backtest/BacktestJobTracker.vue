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
              {{ job.strategy_name || 'Strategy' }} &middot; {{ job.timeframe }}
            </div>
            <div class="text-[10px] text-white/30 mt-0.5">
              <template v-if="job.status === 'running'">
                {{ job.progress }}% — {{ job.progress_message }}
              </template>
              <template v-else-if="job.status === 'completed'">
                <span :class="(job.total_return || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'">
                  {{ (job.total_return || 0) >= 0 ? '+' : '' }}{{ (job.total_return || 0).toFixed(2) }}%
                </span>
                &middot; {{ job.total_trades }} trades
              </template>
              <template v-else-if="job.status === 'failed'">
                <span class="text-red-400">{{ job.error || 'Failed' }}</span>
              </template>
              <template v-else>
                {{ job.status }}
              </template>
            </div>
            <!-- Progress bar for running jobs -->
            <div v-if="job.status === 'running'" class="mt-1.5 h-1 bg-white/[0.06] rounded-full overflow-hidden">
              <div class="h-full bg-accent-500 rounded-full transition-all duration-500" :style="{ width: `${job.progress}%` }"></div>
            </div>
          </div>
        </div>

        <div v-if="job.status === 'completed'" class="flex-shrink-0 ml-2">
          <button
            class="view-results-btn text-[10px] text-accent-400 hover:text-accent-300 px-2 py-1 rounded bg-accent-500/10 hover:bg-accent-500/20 transition-all"
            @click.stop="viewResult(job)"
          >
            View
          </button>
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { submitBacktest as apiSubmitBacktest, getBacktest, listBacktests } from '../../api/index.js'

const router = useRouter()
const emit = defineEmits(['view-result'])

const jobs = ref([])

// Load previous backtests from API on mount
onMounted(async () => {
  try {
    const history = await listBacktests()
    for (const item of history) {
      // Don't duplicate if already in the list (from a submit)
      if (jobs.value.some(j => j.id === item.id)) continue
      jobs.value.push(reactive({
        id: item.id,
        status: item.status,
        progress: item.progress || (item.status === 'completed' ? 100 : 0),
        progress_message: item.progress_message || '',
        timeframe: item.timeframe,
        start_date: item.start_date,
        end_date: item.end_date,
        strategy_name: item.strategy_name || '',
        total_return: item.total_return,
        sharpe_ratio: item.sharpe_ratio,
        total_trades: item.total_trades,
        error: item.error_message,
        result: null, // Don't load full result — fetched on demand via result page
      }))
    }
    // Resume polling for any active jobs
    for (const job of jobs.value) {
      if (job.status === 'running' || job.status === 'pending') {
        pollJob(job)
      }
    }
  } catch (e) {
    console.error('Failed to load backtest history:', e)
  }
})

// Submit a new backtest and start polling
async function submitBacktest(config) {
  try {
    const response = await apiSubmitBacktest(config)
    // Use reactive() so poll mutations trigger re-render
    const job = reactive({
      id: response.id,
      status: response.status || 'pending',
      progress: 0,
      progress_message: 'Queued',
      timeframe: config.timeframe,
      start_date: config.start_date,
      end_date: config.end_date,
      strategy_name: '',
      total_return: null,
      sharpe_ratio: null,
      total_trades: null,
      error: null,
      result: null,
    })
    // Prepend to list (newest first)
    jobs.value.unshift(job)
    // Poll in background (don't await — let UI update immediately)
    pollJob(job)
  } catch (e) {
    console.error('Failed to submit backtest:', e)
  }
}

async function pollJob(job) {
  const POLL_INTERVAL = 2000
  const MAX_POLLS = 300 // ~10 min max

  for (let i = 0; i < MAX_POLLS; i++) {
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL))

    try {
      const data = await getBacktest(job.id)
      job.status = data.status
      job.progress = data.progress || 0
      job.progress_message = data.progress_message || ''
      job.strategy_name = data.strategy_name || ''

      if (data.status === 'completed') {
        job.total_return = data.total_return
        job.sharpe_ratio = data.sharpe_ratio
        job.total_trades = data.total_trades
        job.result = data.result_json || null
        return
      }
      if (data.status === 'failed') {
        job.error = data.error_message || 'Backtest failed'
        return
      }
    } catch (e) {
      console.error('Poll error:', e)
    }
  }
}

function viewResult(job) {
  if (job.status === 'completed' && job.id) {
    router.push({ name: 'result', params: { id: job.id } })
  }
}

// Expose for parent (BacktestApp) to call
defineExpose({ submitBacktest })
</script>
