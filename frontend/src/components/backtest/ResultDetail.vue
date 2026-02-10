<template>
  <div class="p-4">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <h2 class="text-sm font-bold text-white flex items-center gap-2">
          <i class="fas fa-chart-area text-accent-500"></i>
          {{ result?.strategy_name ?? 'Backtest Results' }}
        </h2>
        <span v-if="result?.timeframe || result?.mode" class="text-xs text-white/30">
          {{ [result.timeframe, result.mode].filter(Boolean).join(' | ') }}
        </span>
      </div>
      <button
        @click="emit('close')"
        class="text-white/30 hover:text-white p-1 transition-colors"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-4 border-b border-white/[0.04] pb-1">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          activeTab === tab.id
            ? 'text-white bg-white/[0.08]'
            : 'text-white/40 hover:text-white/70',
          'px-3 py-1.5 text-xs rounded-lg transition-all',
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab: Overview -->
    <div v-show="activeTab === 'overview'">
      <StatsCards :result="result" />
      <div class="mt-4 space-y-4">
        <EquityChart :equity-curve="result?.equity_curve ?? []" />
        <DrawdownChart :drawdown-curve="result?.drawdown_curve ?? []" />
      </div>
    </div>

    <!-- Tab: Chart -->
    <div v-show="activeTab === 'chart'">
      <div style="height: 500px;">
        <OhlcvChart
          :ohlcv-bars="result?.ohlcv_bars ?? []"
          :trade-markers="result?.trade_markers ?? []"
        />
      </div>
    </div>

    <!-- Tab: Trades -->
    <div v-show="activeTab === 'trades'">
      <TradeTable :trades="result?.trades ?? []" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StatsCards from './StatsCards.vue'
import EquityChart from './EquityChart.vue'
import DrawdownChart from './DrawdownChart.vue'
import OhlcvChart from './OhlcvChart.vue'
import TradeTable from './TradeTable.vue'

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close'])

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'chart', label: 'Chart' },
  { id: 'trades', label: 'Trades' },
]

const activeTab = ref('overview')
</script>
