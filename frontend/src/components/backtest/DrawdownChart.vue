<template>
  <div ref="container" class="drawdown-chart" style="height: 200px;"></div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { createChart } from 'lightweight-charts'

const props = defineProps({
  drawdownCurve: { type: Array, default: () => [] },
})

const container = ref(null)
let chart = null
let series = null

const CHART_OPTIONS = {
  layout: {
    background: { color: '#080a16' },
    textColor: 'rgba(255,255,255,0.4)',
  },
  grid: {
    vertLines: { color: 'rgba(255,255,255,0.04)' },
    horzLines: { color: 'rgba(255,255,255,0.04)' },
  },
  rightPriceScale: { borderColor: 'rgba(255,255,255,0.06)' },
  timeScale: {
    borderColor: 'rgba(255,255,255,0.06)',
    timeVisible: true,
    secondsVisible: false,
  },
  crosshair: { mode: 0 },
}

function toUnix(ts) {
  return Math.floor(new Date(ts).getTime() / 1000)
}

function buildData() {
  return props.drawdownCurve.map(p => ({
    time: toUnix(p.timestamp),
    value: p.drawdown_pct,
  }))
}

function createChartInstance() {
  destroyChart()
  if (!container.value) return

  chart = createChart(container.value, {
    ...CHART_OPTIONS,
    autoSize: true,
  })

  series = chart.addAreaSeries({
    lineColor: '#ef4444',
    topColor: 'rgba(239,68,68,0)',
    bottomColor: 'rgba(239,68,68,0.3)',
    lineWidth: 2,
    priceFormat: {
      type: 'custom',
      formatter: v => v.toFixed(2) + '%',
    },
  })

  setData()
}

function setData() {
  if (!series) return
  const data = buildData()
  if (!data.length) return
  series.setData(data)
  chart.timeScale().fitContent()
}

function destroyChart() {
  if (chart) {
    chart.remove()
    chart = null
    series = null
  }
}

onMounted(() => {
  nextTick(() => createChartInstance())
})

onBeforeUnmount(() => {
  destroyChart()
})

watch(
  () => props.drawdownCurve,
  () => {
    if (series) {
      setData()
    } else {
      nextTick(() => createChartInstance())
    }
  },
  { deep: true }
)
</script>

<style scoped>
.drawdown-chart {
  border-radius: 8px;
  overflow: hidden;
}
</style>
