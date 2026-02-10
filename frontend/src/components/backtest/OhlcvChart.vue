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
let tradeMarkerPrimitive = null
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

/**
 * Series Primitive that draws horizontal arrows at exact price Y-coordinates.
 * Uses Canvas2D via the lightweight-charts plugin API.
 */
class TradeMarkersPrimitive {
  constructor(markers) {
    this._markers = markers  // [{time, price, isLong, isEntry}, ...]
    this._series = null
    this._chart = null
  }

  attached({ chart, series }) {
    this._chart = chart
    this._series = series
  }

  detached() {
    this._chart = null
    this._series = null
  }

  updateAllViews() {}

  paneViews() {
    return [new TradeMarkersRenderer(this._markers, this._series, this._chart)]
  }
}

class TradeMarkersRenderer {
  constructor(markers, series, chart) {
    this._markers = markers
    this._series = series
    this._chart = chart
  }

  zOrder() { return 'top' }

  renderer() {
    const markers = this._markers
    const series = this._series
    const chart = this._chart
    return {
      draw(target) {
        if (!series || !chart) return

        target.useMediaCoordinateSpace(({ context: ctx }) => {
          const timeScale = chart.timeScale()

          for (const m of markers) {
            const x = timeScale.timeToCoordinate(m.time)
            const y = series.priceToCoordinate(m.price)
            if (x === null || y === null) continue

            const color = m.isLong ? '#2962FF' : '#e91e63'
            const size = 6

            ctx.save()
            ctx.fillStyle = color

            // Draw horizontal triangle with tip pointing at the bar center (x)
            const s = size
            ctx.beginPath()
            if (m.isEntry) {
              // ▶ right-pointing, tip at bar
              ctx.moveTo(x - s * 2, y - s * 0.7)
              ctx.lineTo(x,         y)
              ctx.lineTo(x - s * 2, y + s * 0.7)
            } else {
              // ◀ left-pointing, tip at bar
              ctx.moveTo(x + s * 2, y - s * 0.7)
              ctx.lineTo(x,         y)
              ctx.lineTo(x + s * 2, y + s * 0.7)
            }
            ctx.closePath()
            ctx.fill()

            // Label: LE/LX/SE/SX next to the triangle
            const label = (m.isLong ? 'L' : 'S') + (m.isEntry ? 'E' : 'X')
            ctx.font = '9px Inter, sans-serif'
            ctx.fillStyle = color
            ctx.textBaseline = 'middle'
            if (m.isEntry) {
              // Label to the left of the triangle
              ctx.textAlign = 'right'
              ctx.fillText(label, x - s * 2 - 3, y)
            } else {
              // Label to the right of the triangle
              ctx.textAlign = 'left'
              ctx.fillText(label, x + s * 2 + 3, y)
            }

            ctx.restore()
          }
        })
      }
    }
  }
}

function buildPrimitiveMarkers() {
  if (!props.tradeMarkers?.length) return []
  return props.tradeMarkers.map(m => ({
    time: toUnix(m.timestamp),
    price: m.price,
    isLong: m.direction === 'Long' || m.direction === 'long',
    isEntry: !!m.is_entry,
  }))
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

  // Trade markers as canvas primitives at exact Y-axis prices
  if (tradeMarkerPrimitive) {
    candleSeries.detachPrimitive(tradeMarkerPrimitive)
  }
  const primitiveMarkers = buildPrimitiveMarkers()
  if (primitiveMarkers.length) {
    tradeMarkerPrimitive = new TradeMarkersPrimitive(primitiveMarkers)
    candleSeries.attachPrimitive(tradeMarkerPrimitive)
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
