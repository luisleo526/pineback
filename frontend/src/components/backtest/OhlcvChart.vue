<template>
  <div class="ohlcv-chart" ref="root" style="width: 100%; height: 100%; display: flex; flex-direction: column;">
    <div ref="candleContainer" class="candle-pane" style="flex: 3; min-height: 0;"></div>
    <div ref="volumeContainer" class="volume-pane" style="flex: 1; min-height: 0;"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { createChart } from 'lightweight-charts'

const props = defineProps({
  ohlcvBars: { type: Array, default: () => [] },
  tradeMarkers: { type: Array, default: () => [] },
})

const root = ref(null)
const candleContainer = ref(null)
const volumeContainer = ref(null)

let candleChart = null
let volumeChart = null
let candleSeries = null
let volumeSeries = null
let syncing = false
let resizeObserver = null

const CHART_OPTIONS = {
  layout: {
    background: { color: '#080a16' },
    textColor: 'rgba(255,255,255,0.4)',
  },
  grid: {
    vertLines: { color: 'rgba(255,255,255,0.04)' },
    horzLines: { color: 'rgba(255,255,255,0.04)' },
  },
  crosshair: { mode: 0 },
  rightPriceScale: { borderColor: 'rgba(255,255,255,0.06)' },
  timeScale: {
    borderColor: 'rgba(255,255,255,0.06)',
    timeVisible: true,
    secondsVisible: false,
  },
}

function toUnix(ts) {
  return Math.floor(new Date(ts).getTime() / 1000)
}

function buildCandleData() {
  return props.ohlcvBars.map(b => ({
    time: toUnix(b.timestamp),
    open: b.open,
    high: b.high,
    low: b.low,
    close: b.close,
  }))
}

function buildVolumeData() {
  return props.ohlcvBars.map(b => ({
    time: toUnix(b.timestamp),
    value: b.volume,
    color: b.close >= b.open ? 'rgba(34,197,94,0.35)' : 'rgba(239,68,68,0.35)',
  }))
}

function buildMarkers() {
  if (!props.tradeMarkers?.length) return []
  return props.tradeMarkers
    .map(m => {
      const isLong = m.direction === 'Long' || m.direction === 'long'
      const isEntry = m.is_entry
      let position, color, shape, text

      // TradingView style: small triangles, minimal text
      if (isLong && isEntry) {
        position = 'belowBar'; color = '#2962FF'; shape = 'arrowUp'
        text = 'Long'
      } else if (isLong && !isEntry) {
        position = 'aboveBar'; color = '#2962FF'; shape = 'arrowDown'
        text = ''
      } else if (!isLong && isEntry) {
        position = 'aboveBar'; color = '#e91e63'; shape = 'arrowDown'
        text = 'Short'
      } else {
        position = 'belowBar'; color = '#e91e63'; shape = 'arrowUp'
        text = ''
      }
      return {
        time: toUnix(m.timestamp),
        position,
        color,
        shape,
        text,
        size: 1,
      }
    })
    .sort((a, b) => a.time - b.time)
}

function createCharts() {
  destroyCharts()
  if (!candleContainer.value || !volumeContainer.value) return

  candleChart = createChart(candleContainer.value, {
    ...CHART_OPTIONS,
    autoSize: true,
  })

  volumeChart = createChart(volumeContainer.value, {
    ...CHART_OPTIONS,
    autoSize: true,
  })

  candleSeries = candleChart.addCandlestickSeries({
    upColor: '#22c55e',
    downColor: '#ef4444',
    borderUpColor: '#22c55e',
    borderDownColor: '#ef4444',
    wickUpColor: '#22c55e',
    wickDownColor: '#ef4444',
  })

  volumeSeries = volumeChart.addHistogramSeries({
    priceFormat: { type: 'volume' },
    priceScaleId: '',
  })

  // Sync visible range
  candleChart.timeScale().subscribeVisibleLogicalRangeChange(range => {
    if (syncing) return
    syncing = true
    volumeChart.timeScale().setVisibleLogicalRange(range)
    syncing = false
  })

  volumeChart.timeScale().subscribeVisibleLogicalRangeChange(range => {
    if (syncing) return
    syncing = true
    candleChart.timeScale().setVisibleLogicalRange(range)
    syncing = false
  })

  // Sync crosshair
  candleChart.subscribeCrosshairMove(param => {
    if (syncing) return
    syncing = true
    if (param.time) {
      volumeChart.setCrosshairPosition(undefined, param.time, volumeSeries)
    } else {
      volumeChart.clearCrosshairPosition()
    }
    syncing = false
  })

  volumeChart.subscribeCrosshairMove(param => {
    if (syncing) return
    syncing = true
    if (param.time) {
      candleChart.setCrosshairPosition(undefined, param.time, candleSeries)
    } else {
      candleChart.clearCrosshairPosition()
    }
    syncing = false
  })

  setData()
}

function setData() {
  if (!candleSeries || !volumeSeries) return
  const candleData = buildCandleData()
  const volumeData = buildVolumeData()
  if (!candleData.length) return

  candleSeries.setData(candleData)
  volumeSeries.setData(volumeData)

  const markers = buildMarkers()
  if (markers.length) {
    candleSeries.setMarkers(markers)
  }

  candleChart.timeScale().fitContent()
  volumeChart.timeScale().fitContent()
}

function destroyCharts() {
  if (candleChart) {
    candleChart.remove()
    candleChart = null
    candleSeries = null
  }
  if (volumeChart) {
    volumeChart.remove()
    volumeChart = null
    volumeSeries = null
  }
}

onMounted(() => {
  nextTick(() => createCharts())
})

onBeforeUnmount(() => {
  destroyCharts()
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})

watch(
  () => [props.ohlcvBars, props.tradeMarkers],
  () => {
    if (candleSeries) {
      setData()
    } else {
      nextTick(() => createCharts())
    }
  },
  { deep: true }
)
</script>

<style scoped>
.ohlcv-chart {
  position: relative;
}
</style>
