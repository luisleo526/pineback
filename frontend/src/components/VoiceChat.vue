<template>
  <!-- Floating voice chat button + active call panel -->
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
    <!-- Active call panel -->
    <transition name="voice-panel">
      <div
        v-if="state === 'active'"
        class="rounded-2xl border border-white/[0.08] p-4 w-64 flex flex-col items-center gap-3"
        style="background: rgba(14, 17, 32, 0.95); backdrop-filter: blur(20px); box-shadow: 0 16px 48px rgba(0,0,0,0.6);"
      >
        <!-- Status indicator -->
        <div class="flex items-center gap-2">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                  :class="aiSpeaking ? 'bg-accent-500' : 'bg-green-400'"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5"
                  :class="aiSpeaking ? 'bg-accent-500' : 'bg-green-400'"></span>
          </span>
          <span class="text-xs text-white/60">
            {{ aiSpeaking ? 'AI Speaking...' : 'Listening...' }}
          </span>
        </div>

        <!-- Audio visualizer bars -->
        <div class="flex items-end gap-0.5 h-8">
          <div
            v-for="i in 12"
            :key="i"
            class="w-1 rounded-full transition-all duration-150"
            :class="aiSpeaking ? 'bg-accent-500' : 'bg-green-400'"
            :style="{ height: barHeights[i - 1] + 'px', opacity: 0.4 + barHeights[i - 1] / 50 }"
          ></div>
        </div>

        <!-- Transcript snippet -->
        <p v-if="lastTranscript" class="text-[11px] text-white/40 text-center line-clamp-2 w-full">
          {{ lastTranscript }}
        </p>
      </div>
    </transition>

    <!-- Error toast -->
    <transition name="voice-panel">
      <div
        v-if="errorMessage"
        class="rounded-xl border border-red-500/20 px-4 py-2.5 max-w-64"
        style="background: rgba(14, 17, 32, 0.95);"
      >
        <p class="text-xs text-red-400">
          <i class="fas fa-exclamation-circle mr-1"></i>{{ errorMessage }}
        </p>
      </div>
    </transition>

    <!-- Main floating button -->
    <button
      @click="handleClick"
      :disabled="state === 'connecting'"
      :class="[
        'w-14 h-14 rounded-full flex items-center justify-center transition-all shadow-lg',
        state === 'active'
          ? 'bg-red-500 hover:bg-red-600 shadow-red-500/30'
          : state === 'connecting'
            ? 'bg-accent-500/80 cursor-wait shadow-accent-500/30'
            : 'bg-accent-500 hover:bg-accent-600 shadow-accent-500/30 hover:scale-105',
      ]"
      :title="state === 'active' ? 'End conversation' : 'Discuss with AI'"
    >
      <i v-if="state === 'connecting'" class="fas fa-spinner fa-spin text-white text-lg"></i>
      <i v-else-if="state === 'active'" class="fas fa-phone-slash text-white text-lg"></i>
      <i v-else class="fas fa-microphone text-white text-lg"></i>
    </button>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'

const props = defineProps({
  result: { type: Object, required: true },
})

// ── State ────────────────────────────────────────────────────
const state = ref('idle') // 'idle' | 'connecting' | 'active'
const aiSpeaking = ref(false)
const lastTranscript = ref('')
const errorMessage = ref('')

// Audio visualizer bar heights (randomized during active state)
const barHeights = reactive(Array(12).fill(4))
let visualizerInterval = null

// WebRTC references
let pc = null
let dc = null
let localStream = null
let audioElement = null

// Function call accumulation buffer
// Maps call_id -> { name, arguments_str }
const pendingCalls = reactive({})

// ── Click handler ────────────────────────────────────────────
function handleClick() {
  if (state.value === 'active') {
    disconnect()
  } else if (state.value === 'idle') {
    connect()
  }
}

// ── Connect ──────────────────────────────────────────────────
async function connect() {
  state.value = 'connecting'
  errorMessage.value = ''

  try {
    // 1. Get microphone
    localStream = await navigator.mediaDevices.getUserMedia({ audio: true })

    // 2. Create peer connection
    pc = new RTCPeerConnection()

    // Audio output
    audioElement = document.createElement('audio')
    audioElement.autoplay = true
    pc.ontrack = (e) => {
      audioElement.srcObject = e.streams[0]
    }

    // Add local mic track
    localStream.getTracks().forEach((track) => pc.addTrack(track, localStream))

    // 3. Data channel for events
    dc = pc.createDataChannel('oai-events')
    dc.addEventListener('open', onDataChannelOpen)
    dc.addEventListener('message', onDataChannelMessage)

    // 4. SDP negotiation
    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    const sdpResp = await fetch('/api/realtime/session', {
      method: 'POST',
      body: offer.sdp,
      headers: { 'Content-Type': 'application/sdp' },
    })

    if (!sdpResp.ok) {
      const errText = await sdpResp.text()
      throw new Error(errText || `HTTP ${sdpResp.status}`)
    }

    const answerSdp = await sdpResp.text()
    await pc.setRemoteDescription({ type: 'answer', sdp: answerSdp })

    state.value = 'active'
    startVisualizer()
  } catch (e) {
    console.error('Voice connect error:', e)
    showError(e.message || 'Failed to connect')
    disconnect()
  }
}

// ── Disconnect ───────────────────────────────────────────────
function disconnect() {
  stopVisualizer()

  if (dc) {
    dc.close()
    dc = null
  }
  if (pc) {
    pc.close()
    pc = null
  }
  if (localStream) {
    localStream.getTracks().forEach((t) => t.stop())
    localStream = null
  }
  if (audioElement) {
    audioElement.srcObject = null
    audioElement = null
  }

  // Clear pending calls
  Object.keys(pendingCalls).forEach((k) => delete pendingCalls[k])

  aiSpeaking.value = false
  lastTranscript.value = ''
  state.value = 'idle'
}

// ── Data channel handlers ────────────────────────────────────
function onDataChannelOpen() {
  // Send an initial greeting prompt so the AI speaks first
  sendEvent({
    type: 'response.create',
    response: {
      instructions: (
        'Greet the user briefly. Tell them you can help analyze their backtest results. ' +
        'Start by calling get_strategy_info and get_performance_summary to understand the context, ' +
        'then give a brief overview of how the strategy performed.'
      ),
    },
  })
}

function onDataChannelMessage(e) {
  let event
  try {
    event = JSON.parse(e.data)
  } catch {
    return
  }

  switch (event.type) {
    // ── Audio activity tracking ──
    case 'output_audio_buffer.speech_started':
      aiSpeaking.value = true
      break
    case 'output_audio_buffer.speech_stopped':
      aiSpeaking.value = false
      break

    // ── Transcription of user speech ──
    case 'conversation.item.input_audio_transcription.completed':
      if (event.transcript) {
        lastTranscript.value = event.transcript
      }
      break

    // ── Function call accumulation ──
    case 'response.function_call_arguments.delta':
      accumulateFunctionCallDelta(event)
      break

    case 'response.function_call_arguments.done':
      handleFunctionCallDone(event)
      break

    // ── Response completion ──
    case 'response.done':
      handleResponseDone(event)
      break

    // ── Errors ──
    case 'error':
      console.error('Realtime API error:', event.error)
      if (event.error?.message) {
        showError(event.error.message)
      }
      break
  }
}

// ── Function call handling ────────────────────────────────────

function accumulateFunctionCallDelta(event) {
  const callId = event.call_id
  if (!callId) return
  if (!pendingCalls[callId]) {
    pendingCalls[callId] = { name: '', arguments_str: '' }
  }
  if (event.delta) {
    pendingCalls[callId].arguments_str += event.delta
  }
}

function handleFunctionCallDone(event) {
  const callId = event.call_id
  const name = event.name || pendingCalls[callId]?.name
  const argsStr = event.arguments || pendingCalls[callId]?.arguments_str || '{}'

  // Clean up pending
  delete pendingCalls[callId]

  let args = {}
  try {
    args = JSON.parse(argsStr)
  } catch {
    args = {}
  }

  // Resolve the function call from local data
  const output = resolveFunction(name, args)

  // Send the function output back
  sendEvent({
    type: 'conversation.item.create',
    item: {
      type: 'function_call_output',
      call_id: callId,
      output: JSON.stringify(output),
    },
  })
}

function handleResponseDone(event) {
  // Check if the response had function calls that need a follow-up response
  const output = event.response?.output || []
  const hasFunctionCalls = output.some((item) => item.type === 'function_call')
  if (hasFunctionCalls) {
    // Trigger the model to continue after processing function results
    sendEvent({ type: 'response.create' })
  }
}

function resolveFunction(name, args) {
  const r = props.result
  if (!r) return { error: 'No backtest result available' }

  switch (name) {
    case 'get_performance_summary':
      return {
        total_return_pct: r.total_return_pct,
        annualized_return_pct: r.annualized_return_pct,
        annualized_volatility_pct: r.annualized_volatility_pct,
        sharpe_ratio: r.sharpe_ratio,
        sortino_ratio: r.sortino_ratio,
        calmar_ratio: r.calmar_ratio,
        omega_ratio: r.omega_ratio,
        max_drawdown_pct: r.max_drawdown_pct,
        max_drawdown_duration: r.max_drawdown_duration,
        win_rate_pct: r.win_rate_pct,
        profit_factor: r.profit_factor,
        expectancy: r.expectancy,
        total_trades: r.total_trades,
        total_closed_trades: r.total_closed_trades,
        best_trade_pct: r.best_trade_pct,
        worst_trade_pct: r.worst_trade_pct,
        avg_winning_trade_pct: r.avg_winning_trade_pct,
        avg_losing_trade_pct: r.avg_losing_trade_pct,
        avg_winning_duration: r.avg_winning_duration,
        avg_losing_duration: r.avg_losing_duration,
        initial_capital: r.initial_capital,
        final_value: r.final_value,
        total_fees_paid: r.total_fees_paid,
        benchmark_return_pct: r.benchmark_return_pct,
      }

    case 'get_trade_list': {
      const trades = r.trades || []
      const limit = args.limit || 20
      const offset = args.offset || 0
      const slice = trades.slice(offset, offset + limit)
      return {
        total_trades: trades.length,
        offset,
        limit,
        trades: slice.map((t) => ({
          trade_id: t.trade_id,
          direction: t.direction,
          status: t.status,
          entry_time: t.entry_time,
          exit_time: t.exit_time,
          entry_price: t.entry_price,
          exit_price: t.exit_price,
          size: t.size,
          pnl: t.pnl,
          return_pct: t.return_pct,
          duration: t.duration,
        })),
      }
    }

    case 'get_strategy_info':
      return {
        strategy_name: r.strategy_name,
        symbol: r.symbol,
        exchange: r.exchange,
        timeframe: r.timeframe,
        mode: r.mode,
        start_date: r.start_date,
        end_date: r.end_date,
        period: r.period,
        params: r.params,
      }

    default:
      return { error: `Unknown function: ${name}` }
  }
}

// ── Helpers ──────────────────────────────────────────────────
function sendEvent(event) {
  if (dc && dc.readyState === 'open') {
    dc.send(JSON.stringify(event))
  }
}

function showError(msg) {
  errorMessage.value = msg
  setTimeout(() => {
    errorMessage.value = ''
  }, 5000)
}

// ── Visualizer ───────────────────────────────────────────────
function startVisualizer() {
  stopVisualizer()
  visualizerInterval = setInterval(() => {
    for (let i = 0; i < 12; i++) {
      barHeights[i] = aiSpeaking.value
        ? 4 + Math.random() * 28
        : 3 + Math.random() * 6
    }
  }, 120)
}

function stopVisualizer() {
  if (visualizerInterval) {
    clearInterval(visualizerInterval)
    visualizerInterval = null
  }
  for (let i = 0; i < 12; i++) {
    barHeights[i] = 4
  }
}

// ── Cleanup on unmount ───────────────────────────────────────
onUnmounted(() => {
  disconnect()
})
</script>

<style scoped>
.voice-panel-enter-active,
.voice-panel-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.voice-panel-enter-from,
.voice-panel-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}
</style>
