<template>
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
    <div
      v-for="stat in stats"
      :key="stat.label"
      class="rounded-xl p-3"
      style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.04);"
    >
      <div class="text-[10px] text-white/30 uppercase tracking-wider">{{ stat.label }}</div>
      <div class="text-lg font-semibold mt-1" :class="stat.colorClass">{{ stat.value }}</div>
      <div v-if="stat.subtitle" class="text-[10px] text-white/25 mt-0.5">{{ stat.subtitle }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  formatPct,
  formatDollar,
  formatPnl,
  formatRatio,
  formatInt,
  formatDuration,
  pnlColor,
  sharpeColor,
  winRateColor,
} from '../../utils/formatters'

const props = defineProps({
  result: { type: Object, default: null },
})

const stats = computed(() => {
  const r = props.result
  if (!r) return []

  const netProfit = (r.final_value != null && r.initial_capital != null)
    ? r.final_value - r.initial_capital
    : null

  return [
    // Row 1
    {
      label: 'Net Profit',
      value: formatPnl(netProfit),
      subtitle: formatPct(r.total_return_pct),
      colorClass: pnlColor(netProfit),
    },
    {
      label: 'CAGR',
      value: formatPct(r.annualized_return_pct),
      colorClass: pnlColor(r.annualized_return_pct),
    },
    {
      label: 'Annualized Volatility',
      value: r.annualized_volatility_pct != null ? `${r.annualized_volatility_pct.toFixed(2)}%` : '—',
      colorClass: 'text-white',
    },
    {
      label: 'Max Drawdown',
      value: r.max_drawdown_pct != null ? `${Math.abs(r.max_drawdown_pct).toFixed(2)}%` : '—',
      subtitle: formatDuration(r.max_drawdown_duration),
      colorClass: 'text-red-400',
    },

    // Row 2
    {
      label: 'Sharpe Ratio',
      value: formatRatio(r.sharpe_ratio),
      colorClass: sharpeColor(r.sharpe_ratio),
    },
    {
      label: 'Sortino Ratio',
      value: formatRatio(r.sortino_ratio),
      colorClass: sharpeColor(r.sortino_ratio),
    },
    {
      label: 'Profit Factor',
      value: formatRatio(r.profit_factor),
      colorClass: r.profit_factor != null
        ? (r.profit_factor > 1 ? 'text-green-400' : 'text-red-400')
        : 'text-white/50',
    },
    {
      label: 'Expectancy',
      value: formatPnl(r.expectancy),
      colorClass: pnlColor(r.expectancy),
    },

    // Row 3
    {
      label: 'Total Trades',
      value: formatInt(r.total_trades),
      colorClass: 'text-white',
    },
    {
      label: 'Win Rate',
      value: r.win_rate_pct != null ? `${r.win_rate_pct.toFixed(2)}%` : '—',
      colorClass: winRateColor(r.win_rate_pct),
    },
    {
      label: 'Best Trade',
      value: formatPct(r.best_trade_pct),
      colorClass: 'text-green-400',
    },
    {
      label: 'Worst Trade',
      value: formatPct(r.worst_trade_pct),
      colorClass: 'text-red-400',
    },

    // Row 4
    {
      label: 'Avg Winning Trade',
      value: formatPct(r.avg_winning_trade_pct),
      colorClass: 'text-green-400',
    },
    {
      label: 'Avg Losing Trade',
      value: formatPct(r.avg_losing_trade_pct),
      colorClass: 'text-red-400',
    },
    {
      label: 'Avg Win Duration',
      value: formatDuration(r.avg_winning_duration),
      colorClass: 'text-white/70',
    },
    {
      label: 'Avg Loss Duration',
      value: formatDuration(r.avg_losing_duration),
      colorClass: 'text-white/70',
    },
  ]
})
</script>
