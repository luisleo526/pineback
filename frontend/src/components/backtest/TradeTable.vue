<template>
  <div>
    <!-- Header with pagination -->
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-white">List of Trades ({{ trades.length }})</h3>
      <div class="flex items-center gap-2">
        <button
          @click="page > 1 && page--"
          :disabled="page <= 1"
          class="px-2.5 py-1 text-xs rounded-lg transition-colors"
          :class="page <= 1 ? 'text-white/15 cursor-not-allowed' : 'text-white/50 hover:text-white hover:bg-white/[0.06]'"
        >
          Prev
        </button>
        <span class="text-xs text-white/30">{{ page }} / {{ totalPages }}</span>
        <button
          @click="page < totalPages && page++"
          :disabled="page >= totalPages"
          class="px-2.5 py-1 text-xs rounded-lg transition-colors"
          :class="page >= totalPages ? 'text-white/15 cursor-not-allowed' : 'text-white/50 hover:text-white hover:bg-white/[0.06]'"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Table header -->
    <div class="grid grid-cols-7 gap-2 px-3 py-2 text-[10px] text-white/30 uppercase tracking-wider border-b border-white/[0.04]">
      <div>#</div>
      <div>Type</div>
      <div>Date/Time</div>
      <div>Price</div>
      <div>Qty</div>
      <div>Profit</div>
      <div>Cum. Profit</div>
    </div>

    <!-- Trade rows -->
    <div v-for="(trade, idx) in paginatedTrades" :key="trade.trade_id ?? idx">
      <!-- Entry row -->
      <div class="grid grid-cols-7 gap-2 px-3 py-2 text-xs text-white/70">
        <div class="text-white/40">{{ (page - 1) * perPage + idx + 1 }}</div>
        <div>
          <span class="inline-flex items-center gap-1">
            <span
              class="inline-block w-1.5 h-1.5 rounded-full"
              :class="trade.direction === 'Long' || trade.direction === 'long' ? 'bg-green-400' : 'bg-orange-400'"
            ></span>
            Entry {{ trade.direction }}
          </span>
        </div>
        <div>{{ fmtDate(trade.entry_time) }}</div>
        <div>{{ trade.entry_price?.toFixed(2) ?? '—' }}</div>
        <div>{{ trade.size?.toFixed(2) ?? '—' }}</div>
        <div></div>
        <div></div>
      </div>

      <!-- Exit row (if closed) -->
      <div
        v-if="trade.exit_time"
        class="grid grid-cols-7 gap-2 px-3 py-2 text-xs text-white/70"
        :class="trade.pnl > 0 ? 'bg-green-500/[0.04]' : 'bg-red-500/[0.04]'"
      >
        <div></div>
        <div>
          <span class="inline-flex items-center gap-1">
            <span
              class="inline-block w-1.5 h-1.5 rounded-full"
              :class="trade.pnl > 0 ? 'bg-green-400' : 'bg-red-400'"
            ></span>
            Exit {{ trade.direction }}
          </span>
        </div>
        <div>{{ fmtDate(trade.exit_time) }}</div>
        <div>{{ trade.exit_price?.toFixed(2) ?? '—' }}</div>
        <div>{{ trade.size?.toFixed(2) ?? '—' }}</div>
        <div :class="pnlColorClass(trade.pnl)">
          {{ fmtPnl(trade.pnl) }}
          <span class="text-white/30">({{ fmtPct(trade.return_pct) }})</span>
        </div>
        <div :class="pnlColorClass(cumProfit(idx))">
          {{ fmtPnl(cumProfit(idx)) }}
        </div>
      </div>

      <div class="border-b border-white/[0.02]"></div>
    </div>

    <!-- Empty state -->
    <div v-if="!trades.length" class="py-8 text-center text-xs text-white/20">
      No trades to display
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { formatDate, formatPnl, formatPct, pnlColor } from '../../utils/formatters'

const props = defineProps({
  trades: { type: Array, default: () => [] },
})

const perPage = 20
const page = ref(1)

const totalPages = computed(() => Math.max(1, Math.ceil(props.trades.length / perPage)))

const paginatedTrades = computed(() => {
  const start = (page.value - 1) * perPage
  return props.trades.slice(start, start + perPage)
})

// Running cumulative profit up to and including the trade at `idx` in the current page
function cumProfit(pageIdx) {
  const globalIdx = (page.value - 1) * perPage + pageIdx
  let sum = 0
  for (let i = 0; i <= globalIdx; i++) {
    sum += props.trades[i]?.pnl ?? 0
  }
  return sum
}

// Wrapper formatters
function fmtDate(v) { return formatDate(v) }
function fmtPnl(v) { return formatPnl(v) }
function fmtPct(v) { return formatPct(v) }
function pnlColorClass(v) { return pnlColor(v) }
</script>
