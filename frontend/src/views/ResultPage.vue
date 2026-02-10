<template>
  <div class="min-h-screen flex flex-col" style="background: linear-gradient(180deg, #080a16 0%, #0b0e1c 100%);">
    <!-- Header -->
    <header class="flex items-center justify-between px-5 py-3 border-b border-white/[0.06] flex-shrink-0" style="background: #080a16;">
      <div class="flex items-center gap-3">
        <router-link to="/app" class="flex items-center gap-2 text-white/40 hover:text-white transition-colors">
          <i class="fas fa-arrow-left text-sm"></i>
          <span class="text-xs">Back to Builder</span>
        </router-link>
        <div class="h-5 w-px bg-white/[0.06]"></div>
        <h1 class="text-sm font-semibold text-white flex items-center gap-2">
          <i class="fas fa-chart-area text-accent-500"></i>
          {{ result?.strategy_name ?? 'Backtest Results' }}
        </h1>
        <span v-if="result" class="text-xs text-white/30 hidden sm:inline">
          {{ result.timeframe }} | {{ result.mode }} | {{ result.start_date }} → {{ result.end_date }}
        </span>
      </div>
      <div class="flex items-center gap-2">
        <span v-if="loading" class="text-xs text-white/30">
          <i class="fas fa-spinner fa-spin mr-1"></i> Loading...
        </span>
        <span v-if="result" class="text-xs font-medium" :class="(result.total_return_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'">
          {{ (result.total_return_pct || 0) >= 0 ? '+' : '' }}{{ (result.total_return_pct || 0).toFixed(2) }}%
        </span>
      </div>
    </header>

    <!-- Loading state -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <i class="fas fa-spinner fa-spin text-2xl text-accent-500 mb-3"></i>
        <p class="text-sm text-white/40">Loading backtest results...</p>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <i class="fas fa-exclamation-triangle text-2xl text-red-400 mb-3"></i>
        <p class="text-sm text-red-400 mb-2">{{ error }}</p>
        <router-link to="/app" class="text-xs text-accent-400 hover:text-accent-300">
          ← Back to Strategy Builder
        </router-link>
      </div>
    </div>

    <!-- Result content -->
    <template v-else-if="result">
      <!-- Tabs -->
      <div class="flex items-center gap-1 px-5 pt-3 pb-0 flex-shrink-0">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id
              ? 'text-white bg-white/[0.08] border-b-2 border-accent-500'
              : 'text-white/40 hover:text-white/70 border-b-2 border-transparent',
            'px-4 py-2.5 text-xs font-medium rounded-t-lg transition-all',
          ]"
        >
          <i :class="['mr-1.5', tab.icon]"></i>
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab content (scrollable) -->
      <div class="flex-1 overflow-y-auto">
        <!-- Overview -->
        <div v-show="activeTab === 'overview'" class="p-5 max-w-7xl mx-auto">
          <StatsCards :result="result" />
          <div class="mt-6 grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div class="rounded-xl border border-white/[0.04] bg-dark-800/30 p-4">
              <h3 class="text-xs font-medium text-white/40 uppercase tracking-wider mb-3">Equity Curve</h3>
              <div style="height: 280px;">
                <EquityChart :equity-curve="result.equity_curve ?? []" />
              </div>
            </div>
            <div class="rounded-xl border border-white/[0.04] bg-dark-800/30 p-4">
              <h3 class="text-xs font-medium text-white/40 uppercase tracking-wider mb-3">Drawdown</h3>
              <div style="height: 280px;">
                <DrawdownChart :drawdown-curve="result.drawdown_curve ?? []" />
              </div>
            </div>
          </div>
        </div>

        <!-- Chart -->
        <div v-show="activeTab === 'chart'" class="p-5">
          <div class="rounded-xl border border-white/[0.04] bg-dark-800/30 p-4" style="height: calc(100vh - 160px); min-height: 500px;">
            <OhlcvChart
              :ohlcv-bars="result.ohlcv_bars ?? []"
              :trade-markers="result.trade_markers ?? []"
            />
          </div>
        </div>

        <!-- Trades -->
        <div v-show="activeTab === 'trades'" class="p-5 max-w-7xl mx-auto">
          <TradeTable :trades="result.trades ?? []" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getBacktest } from '../api/index.js'
import StatsCards from '../components/backtest/StatsCards.vue'
import EquityChart from '../components/backtest/EquityChart.vue'
import DrawdownChart from '../components/backtest/DrawdownChart.vue'
import OhlcvChart from '../components/backtest/OhlcvChart.vue'
import TradeTable from '../components/backtest/TradeTable.vue'

const route = useRoute()
const result = ref(null)
const loading = ref(true)
const error = ref(null)
const activeTab = ref('overview')

const tabs = [
  { id: 'overview', label: 'Overview', icon: 'fas fa-chart-pie' },
  { id: 'chart', label: 'Chart', icon: 'fas fa-chart-candlestick' },
  { id: 'trades', label: 'List of Trades', icon: 'fas fa-list' },
]

onMounted(async () => {
  const id = route.params.id
  if (!id) {
    error.value = 'No backtest ID provided'
    loading.value = false
    return
  }

  try {
    const data = await getBacktest(id)
    if (data.status === 'completed' && data.result_json) {
      result.value = data.result_json
    } else if (data.status === 'failed') {
      error.value = data.error_message || 'Backtest failed'
    } else {
      error.value = `Backtest is ${data.status} (${data.progress}%)`
    }
  } catch (e) {
    error.value = e.message || 'Failed to load results'
  } finally {
    loading.value = false
  }
})
</script>
