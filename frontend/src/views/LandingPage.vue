<template>
  <div class="min-h-screen bg-dark-950 text-white antialiased">
    <!-- Ambient glow effects -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <div class="absolute -top-40 -left-40 w-[600px] h-[600px] bg-accent-500/[0.07] rounded-full blur-[120px]"></div>
      <div class="absolute top-1/3 -right-40 w-[500px] h-[500px] bg-accent-400/[0.05] rounded-full blur-[100px]"></div>
      <div class="absolute bottom-0 left-1/3 w-[400px] h-[400px] bg-accent-600/[0.04] rounded-full blur-[80px]"></div>
    </div>

    <!-- Navigation -->
    <nav class="relative z-20 border-b border-white/5">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-accent-500 flex items-center justify-center">
            <svg class="w-4.5 h-4.5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
            </svg>
          </div>
          <span class="text-sm font-semibold tracking-wide">PINEBACK</span>
        </div>
        <div class="flex items-center gap-6">
          <!-- UI Scale control -->
          <div class="flex items-center rounded-lg overflow-hidden border border-white/[0.06]">
            <button
              @click="scaleDown"
              class="px-2 py-1.5 text-[10px] font-bold leading-none text-dark-300 hover:text-white hover:bg-white/[0.06] transition-colors"
              title="Zoom out"
            >A-</button>
            <button
              @dblclick="resetScale"
              class="px-1.5 py-1.5 text-[10px] text-white/40 leading-none cursor-default min-w-[36px] text-center"
              title="Double-click to reset"
            >{{ Math.round(scale * 100) }}%</button>
            <button
              @click="scaleUp"
              class="px-2 py-1.5 text-[10px] font-bold leading-none text-dark-300 hover:text-white hover:bg-white/[0.06] transition-colors"
              title="Zoom in"
            >A+</button>
          </div>

          <a :href="githubUrl" target="_blank" class="text-dark-300 hover:text-white transition-colors text-sm">GitHub</a>
          <router-link to="/app" class="px-4 py-1.5 text-sm font-medium rounded-md bg-accent-500 hover:bg-accent-600 transition-colors">
            Launch App
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative z-10 pt-24 pb-32">
      <div class="max-w-7xl mx-auto px-6">
        <div class="max-w-3xl mx-auto text-center">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-500/10 border border-accent-500/20 text-accent-400 text-xs font-medium mb-8">
            <span class="w-1.5 h-1.5 rounded-full bg-accent-400 animate-pulse"></span>
            Full-Stack Interview Project
          </div>
          <h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] mb-6">
            <span class="bg-gradient-to-r from-accent-400 to-accent-600 bg-clip-text text-transparent">PineBack</span>
          </h1>
          <p class="text-lg sm:text-xl text-dark-300 max-w-2xl mx-auto mb-4 leading-relaxed">
            A production-grade backtesting platform that speaks
            <strong class="text-white">PineScript v6</strong> — the same language used by
            <strong class="text-white">TradingView's global algo-trading community</strong>.
          </p>
          <p class="text-base text-dark-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Build strategies visually, generate TradingView-compatible PineScript, and backtest locally with realistic execution.
            Every script works both here <em>and</em> on TradingView — one strategy, two platforms.
          </p>
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
            <router-link
              to="/app"
              class="group inline-flex items-center gap-2 px-8 py-3.5 bg-accent-500 hover:bg-accent-600 rounded-lg font-semibold transition-all hover:shadow-lg hover:shadow-accent-500/25"
            >
              Launch App
              <svg class="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
            </router-link>
            <a
              :href="githubUrl"
              target="_blank"
              class="inline-flex items-center gap-2 px-8 py-3.5 rounded-lg font-semibold border border-dark-600 hover:border-dark-400 text-dark-200 hover:text-white transition-all"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              View Source
            </a>
          </div>
        </div>

        <!-- Hero visual — mini stat preview -->
        <div class="mt-20 max-w-4xl mx-auto">
          <div class="rounded-2xl border border-white/[0.06] bg-dark-900/60 backdrop-blur-sm p-1 shadow-2xl shadow-black/40">
            <div class="rounded-xl bg-dark-900/80 p-6">
              <div class="grid grid-cols-4 gap-4">
                <div v-for="stat in heroStats" :key="stat.label" class="text-center">
                  <div class="text-2xl sm:text-3xl font-bold" :class="stat.color">{{ stat.value }}</div>
                  <div class="text-xs text-dark-400 mt-1">{{ stat.label }}</div>
                </div>
              </div>
              <div class="mt-6 h-24 rounded-lg bg-dark-800/50 flex items-end px-4 pb-2 gap-[3px] overflow-hidden">
                <div
                  v-for="(h, i) in equityBars"
                  :key="i"
                  class="flex-1 rounded-t-sm transition-all"
                  :class="h > 50 ? 'bg-accent-500/60' : 'bg-accent-500/30'"
                  :style="{ height: h + '%' }"
                ></div>
              </div>
              <div class="flex justify-between text-[10px] text-dark-500 mt-1.5 px-4">
                <span>Jan 2020</span>
                <span>Equity Curve (sample)</span>
                <span>Dec 2024</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Grid -->
    <section class="relative z-10 py-24 bg-dark-900/40">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">What It Does</h2>
          <p class="text-dark-300 max-w-xl mx-auto">From strategy creation to performance analysis — everything in one platform.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="group rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm p-6 hover:border-accent-500/30 hover:bg-dark-800/50 transition-all duration-300"
          >
            <div class="w-10 h-10 rounded-lg bg-accent-500/10 flex items-center justify-center text-accent-400 mb-4 group-hover:bg-accent-500/20 transition-colors">
              <span v-html="feature.icon" class="w-5 h-5"></span>
            </div>
            <h3 class="text-lg font-semibold mb-2">{{ feature.title }}</h3>
            <p class="text-sm text-dark-300 leading-relaxed mb-3">{{ feature.description }}</p>
            <div class="text-xs text-accent-400/80 flex items-center gap-1.5">
              <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              <span>{{ feature.useCase }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Key Assumptions -->
    <section class="relative z-10 py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">Design Decisions</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Key assumptions and scope boundaries that shaped this project.</p>
        </div>
        <div class="max-w-3xl mx-auto space-y-4">
          <div
            v-for="assumption in assumptions"
            :key="assumption.title"
            class="rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm p-5 flex gap-4"
          >
            <div class="w-8 h-8 rounded-lg bg-dark-700/60 flex items-center justify-center text-accent-400 shrink-0 mt-0.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg>
            </div>
            <div>
              <h4 class="font-semibold text-sm mb-1">{{ assumption.title }}</h4>
              <p class="text-xs text-dark-400 leading-relaxed">{{ assumption.detail }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Magnifier Mode — Intra-Bar Detection -->
    <section class="relative z-10 py-24 bg-dark-900/40">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">Deep Dive: Magnifier Mode</h2>
          <p class="text-dark-300 max-w-2xl mx-auto">
            Standard backtests fill at bar close — missing what happens <em>inside</em> each candle.
            Magnifier mode resamples higher-timeframe signals to 1-minute bars,
            detecting realistic intra-bar entry and exit points.
          </p>
        </div>

        <div class="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">

          <!-- LEFT: Standard Mode -->
          <div class="rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm p-6">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-2 h-2 rounded-full bg-dark-400"></div>
              <span class="text-xs font-semibold uppercase tracking-wider text-dark-300">Standard Mode</span>
              <span class="ml-auto text-[10px] text-dark-500 font-mono">fill @ bar close</span>
            </div>
            <!-- Conceptual SVG chart -->
            <svg viewBox="0 0 400 200" class="w-full" xmlns="http://www.w3.org/2000/svg">
              <!-- grid -->
              <line v-for="y in [40, 80, 120, 160]" :key="'sg'+y" x1="30" :y1="y" x2="380" :y2="y" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
              <line x1="30" y1="180" x2="380" y2="180" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
              <!-- price axis labels -->
              <text x="8" y="44" fill="rgba(255,255,255,0.2)" font-size="9" font-family="monospace">460</text>
              <text x="8" y="84" fill="rgba(255,255,255,0.2)" font-size="9" font-family="monospace">450</text>
              <text x="8" y="124" fill="rgba(255,255,255,0.2)" font-size="9" font-family="monospace">440</text>
              <text x="8" y="164" fill="rgba(255,255,255,0.2)" font-size="9" font-family="monospace">430</text>

              <!-- 5 daily candles (wide) -->
              <!-- Candle 1: bearish -->
              <line x1="80" y1="50" x2="80" y2="140" stroke="rgba(239,68,68,0.6)" stroke-width="1"/>
              <rect x="65" y="70" width="30" height="50" rx="2" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.7)" stroke-width="1"/>
              <!-- Candle 2: bullish -->
              <line x1="150" y1="60" x2="150" y2="150" stroke="rgba(34,197,94,0.6)" stroke-width="1"/>
              <rect x="135" y="90" width="30" height="40" rx="2" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.7)" stroke-width="1"/>
              <!-- Candle 3: bullish (signal bar) -->
              <line x1="220" y1="45" x2="220" y2="120" stroke="rgba(34,197,94,0.6)" stroke-width="1"/>
              <rect x="205" y="60" width="30" height="40" rx="2" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.7)" stroke-width="1"/>
              <!-- Candle 4: bearish -->
              <line x1="290" y1="55" x2="290" y2="135" stroke="rgba(239,68,68,0.6)" stroke-width="1"/>
              <rect x="275" y="65" width="30" height="50" rx="2" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.7)" stroke-width="1"/>
              <!-- Candle 5: bearish -->
              <line x1="355" y1="70" x2="355" y2="160" stroke="rgba(239,68,68,0.6)" stroke-width="1"/>
              <rect x="340" y="85" width="30" height="55" rx="2" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.7)" stroke-width="1"/>

              <!-- Entry marker at bar 3 CLOSE (bottom of body = 100) -->
              <circle cx="220" cy="60" r="5" fill="#6366f1" stroke="#818cf8" stroke-width="1.5"/>
              <text x="220" y="52" text-anchor="middle" fill="#a5b4fc" font-size="9" font-weight="600">LE</text>

              <!-- Exit marker at bar 5 CLOSE -->
              <circle cx="355" cy="140" r="5" fill="#f59e0b" stroke="#fbbf24" stroke-width="1.5"/>
              <text x="355" y="158" text-anchor="middle" fill="#fcd34d" font-size="9" font-weight="600">LX</text>

              <!-- Dashed line connecting entry to exit -->
              <line x1="220" y1="60" x2="355" y2="140" stroke="rgba(99,102,241,0.3)" stroke-width="1" stroke-dasharray="4 3"/>

              <!-- Label: fills happen at close -->
              <rect x="110" y="168" width="180" height="18" rx="4" fill="rgba(255,255,255,0.04)"/>
              <text x="200" y="180" text-anchor="middle" fill="rgba(255,255,255,0.35)" font-size="9" font-family="monospace">Entry &amp; exit at bar close only</text>
            </svg>

            <div class="mt-4 space-y-2">
              <div class="flex items-center gap-2 text-[11px]">
                <span class="w-3 h-3 rounded-full bg-indigo-500/40 border border-indigo-400 shrink-0"></span>
                <span class="text-dark-300">Entry fills at the <span class="text-white font-medium">close</span> of the signal bar</span>
              </div>
              <div class="flex items-center gap-2 text-[11px]">
                <span class="w-3 h-3 rounded-full bg-amber-500/40 border border-amber-400 shrink-0"></span>
                <span class="text-dark-300">Exit fills at the <span class="text-white font-medium">close</span> of the exit bar</span>
              </div>
              <div class="flex items-center gap-2 text-[11px]">
                <span class="text-red-400">&#x2717;</span>
                <span class="text-dark-400">Misses price action within candles — fills can be unrealistic</span>
              </div>
            </div>
          </div>

          <!-- RIGHT: Magnifier Mode -->
          <div class="rounded-xl border border-accent-500/20 bg-accent-500/[0.03] backdrop-blur-sm p-6">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-2 h-2 rounded-full bg-accent-400 animate-pulse"></div>
              <span class="text-xs font-semibold uppercase tracking-wider text-accent-300">Magnifier Mode</span>
              <span class="ml-auto text-[10px] text-accent-500/70 font-mono">fill @ 1m intra-bar</span>
            </div>
            <!-- Conceptual SVG chart — zoomed into single daily bar, showing 1m candles -->
            <svg viewBox="0 0 400 200" class="w-full" xmlns="http://www.w3.org/2000/svg">
              <!-- grid -->
              <line v-for="y in [40, 80, 120, 160]" :key="'mg'+y" x1="30" :y1="y" x2="380" :y2="y" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
              <line x1="30" y1="180" x2="380" y2="180" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
              <!-- price axis labels -->
              <text x="8" y="44" fill="rgba(255,255,255,0.2)" font-size="9" font-family="monospace">460</text>
              <text x="8" y="84" fill="rgba(255,255,255,0.2)" font-size="9" font-family="monospace">455</text>
              <text x="8" y="124" fill="rgba(255,255,255,0.2)" font-size="9" font-family="monospace">450</text>
              <text x="8" y="164" fill="rgba(255,255,255,0.2)" font-size="9" font-family="monospace">445</text>

              <!-- Daily bar outline (ghost) -->
              <rect x="40" y="42" width="340" height="130" rx="4" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="6 4"/>
              <text x="210" y="36" text-anchor="middle" fill="rgba(255,255,255,0.15)" font-size="8" font-family="monospace">-- single daily bar, zoomed in --</text>

              <!-- 1m candles inside (20 mini-candles showing price path) -->
              <!-- Open ~120, drop to 150, recover to 60, dip, close ~85 -->
              <!-- Group 1: opening dip -->
              <rect x="48" y="115" width="6" height="12" rx="1" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.5)" stroke-width="0.5"/>
              <rect x="58" y="122" width="6" height="10" rx="1" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.5)" stroke-width="0.5"/>
              <rect x="68" y="130" width="6" height="14" rx="1" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.5)" stroke-width="0.5"/>
              <rect x="78" y="140" width="6" height="10" rx="1" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.5)" stroke-width="0.5"/>
              <rect x="88" y="145" width="6" height="8" rx="1" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.5)" stroke-width="0.5"/>

              <!-- ENTRY here: price crosses signal threshold -->
              <rect x="98" y="142" width="6" height="10" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>

              <!-- Group 2: recovery rally -->
              <rect x="108" y="132" width="6" height="12" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>
              <rect x="118" y="118" width="6" height="16" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>
              <rect x="128" y="102" width="6" height="18" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>
              <rect x="138" y="88" width="6" height="16" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>
              <rect x="148" y="76" width="6" height="14" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>
              <rect x="158" y="65" width="6" height="13" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>
              <rect x="168" y="56" width="6" height="11" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>
              <rect x="178" y="50" width="6" height="9" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>

              <!-- Peak & pullback -->
              <rect x="188" y="48" width="6" height="10" rx="1" fill="rgba(34,197,94,0.5)" stroke="rgba(34,197,94,0.6)" stroke-width="0.5"/>
              <rect x="198" y="52" width="6" height="8" rx="1" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.5)" stroke-width="0.5"/>
              <rect x="208" y="58" width="6" height="10" rx="1" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.5)" stroke-width="0.5"/>
              <rect x="218" y="65" width="6" height="12" rx="1" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.5)" stroke-width="0.5"/>

              <!-- EXIT here: profit target hit -->
              <rect x="228" y="70" width="6" height="10" rx="1" fill="rgba(239,68,68,0.5)" stroke="rgba(239,68,68,0.5)" stroke-width="0.5"/>

              <!-- Remaining bars after exit -->
              <rect x="238" y="76" width="6" height="12" rx="1" fill="rgba(239,68,68,0.4)" stroke="rgba(239,68,68,0.35)" stroke-width="0.5"/>
              <rect x="248" y="82" width="6" height="10" rx="1" fill="rgba(34,197,94,0.35)" stroke="rgba(34,197,94,0.35)" stroke-width="0.5"/>
              <rect x="258" y="78" width="6" height="8" rx="1" fill="rgba(34,197,94,0.35)" stroke="rgba(34,197,94,0.35)" stroke-width="0.5"/>
              <rect x="268" y="74" width="6" height="10" rx="1" fill="rgba(34,197,94,0.35)" stroke="rgba(34,197,94,0.35)" stroke-width="0.5"/>

              <!-- More closing bars -->
              <rect x="278" y="78" width="6" height="8" rx="1" fill="rgba(239,68,68,0.35)" stroke="rgba(239,68,68,0.35)" stroke-width="0.5"/>
              <rect x="288" y="82" width="6" height="10" rx="1" fill="rgba(239,68,68,0.35)" stroke="rgba(239,68,68,0.35)" stroke-width="0.5"/>
              <rect x="298" y="78" width="6" height="12" rx="1" fill="rgba(34,197,94,0.35)" stroke="rgba(34,197,94,0.35)" stroke-width="0.5"/>
              <rect x="308" y="72" width="6" height="9" rx="1" fill="rgba(34,197,94,0.35)" stroke="rgba(34,197,94,0.35)" stroke-width="0.5"/>
              <rect x="318" y="75" width="6" height="7" rx="1" fill="rgba(239,68,68,0.35)" stroke="rgba(239,68,68,0.35)" stroke-width="0.5"/>
              <rect x="328" y="80" width="6" height="8" rx="1" fill="rgba(239,68,68,0.35)" stroke="rgba(239,68,68,0.35)" stroke-width="0.5"/>
              <rect x="338" y="84" width="6" height="6" rx="1" fill="rgba(34,197,94,0.35)" stroke="rgba(34,197,94,0.35)" stroke-width="0.5"/>
              <rect x="348" y="80" width="6" height="8" rx="1" fill="rgba(34,197,94,0.35)" stroke="rgba(34,197,94,0.35)" stroke-width="0.5"/>
              <rect x="358" y="83" width="6" height="7" rx="1" fill="rgba(239,68,68,0.35)" stroke="rgba(239,68,68,0.35)" stroke-width="0.5"/>
              <rect x="368" y="86" width="6" height="6" rx="1" fill="rgba(239,68,68,0.35)" stroke="rgba(239,68,68,0.35)" stroke-width="0.5"/>

              <!-- Entry marker -->
              <circle cx="101" cy="142" r="5" fill="#6366f1" stroke="#818cf8" stroke-width="1.5"/>
              <text x="101" y="162" text-anchor="middle" fill="#a5b4fc" font-size="9" font-weight="600">LE</text>

              <!-- Exit marker -->
              <circle cx="231" cy="70" r="5" fill="#f59e0b" stroke="#fbbf24" stroke-width="1.5"/>
              <text x="231" y="62" text-anchor="middle" fill="#fcd34d" font-size="9" font-weight="600">LX</text>

              <!-- Profit region shading -->
              <rect x="98" y="70" width="136" height="72" rx="3" fill="rgba(34,197,94,0.06)" stroke="rgba(34,197,94,0.15)" stroke-width="0.5" stroke-dasharray="3 2"/>

              <!-- Dashed line connecting entry to exit -->
              <line x1="101" y1="142" x2="231" y2="70" stroke="rgba(99,102,241,0.4)" stroke-width="1" stroke-dasharray="4 3"/>

              <!-- Label: intra-bar fills -->
              <rect x="100" y="168" width="200" height="18" rx="4" fill="rgba(139,92,246,0.08)"/>
              <text x="200" y="180" text-anchor="middle" fill="rgba(167,139,250,0.6)" font-size="9" font-family="monospace">Intra-bar entry &amp; exit on 1m bars</text>
            </svg>

            <div class="mt-4 space-y-2">
              <div class="flex items-center gap-2 text-[11px]">
                <span class="w-3 h-3 rounded-full bg-indigo-500/40 border border-indigo-400 shrink-0"></span>
                <span class="text-dark-300">Entry at the <span class="text-accent-400 font-medium">exact 1m bar</span> where signal triggers</span>
              </div>
              <div class="flex items-center gap-2 text-[11px]">
                <span class="w-3 h-3 rounded-full bg-amber-500/40 border border-amber-400 shrink-0"></span>
                <span class="text-dark-300">Exit at the <span class="text-accent-400 font-medium">exact 1m bar</span> where condition is met</span>
              </div>
              <div class="flex items-center gap-2 text-[11px]">
                <span class="text-green-400">&#x2713;</span>
                <span class="text-dark-300">Captures <span class="text-white font-medium">intra-bar price path</span> — realistic limit/stop fills</span>
              </div>
            </div>
          </div>

        </div>

        <!-- How it works callout -->
        <div class="max-w-5xl mx-auto mt-8 rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm p-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-lg bg-accent-500/10 flex items-center justify-center shrink-0 mt-0.5">
              <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607zM13.5 10.5h-6" /></svg>
            </div>
            <div>
              <h4 class="text-sm font-semibold mb-2">How Magnifier Mode Works</h4>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-[11px] text-dark-300">
                <div class="flex gap-2">
                  <span class="text-accent-400 font-bold shrink-0">1.</span>
                  <span>Strategy signals are computed on the <span class="text-white">higher timeframe</span> (e.g. daily bars) — same as standard mode.</span>
                </div>
                <div class="flex gap-2">
                  <span class="text-accent-400 font-bold shrink-0">2.</span>
                  <span>When a signal fires, the engine <span class="text-white">zooms into 1-minute bars</span> within that candle to find the precise fill point.</span>
                </div>
                <div class="flex gap-2">
                  <span class="text-accent-400 font-bold shrink-0">3.</span>
                  <span>Result: fills reflect <span class="text-white">actual intra-bar prices</span>, not just the bar's close — critical for stop-loss and limit orders.</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Metrics -->
    <section class="relative z-10 py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">What You Get Back</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Every backtest produces 16 risk-adjusted performance metrics — from basic returns to trade-level statistics.</p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <div
            v-for="metric in metrics"
            :key="metric.name"
            class="rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm p-5 text-center"
          >
            <div class="text-xl sm:text-2xl font-bold mb-1" :class="metric.color || 'text-white'">{{ metric.sample }}</div>
            <div class="text-xs text-dark-400 font-medium uppercase tracking-wider">{{ metric.name }}</div>
            <div class="text-[11px] text-dark-500 mt-1">{{ metric.formula }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Architecture & Tech Stack -->
    <section class="relative z-10 py-24 bg-dark-900/40">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">How It's Built</h2>
          <p class="text-dark-300 max-w-xl mx-auto">System architecture and technology choices — from browser to database.</p>
        </div>

        <!-- Visual Architecture Diagram -->
        <div class="max-w-5xl mx-auto">
          <!-- Top row: Frontend -->
          <div class="rounded-xl border border-blue-500/20 bg-blue-500/[0.04] p-5 mb-3">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-2 h-2 rounded-full bg-blue-400"></div>
              <span class="text-xs font-semibold uppercase tracking-wider text-blue-300">Frontend — Vue 3 + Vite + Tailwind</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div class="rounded-lg bg-dark-800/60 border border-white/[0.04] p-3 text-center">
                <div class="text-lg mb-1">🎨</div>
                <div class="text-[11px] font-medium text-white/80">Strategy Builder</div>
                <div class="text-[10px] text-dark-400 mt-0.5">No-code visual editor<br>40+ indicators, AND/OR logic</div>
              </div>
              <div class="rounded-lg bg-dark-800/60 border border-white/[0.04] p-3 text-center">
                <div class="text-lg mb-1">📝</div>
                <div class="text-[11px] font-medium text-white/80">PineScript Preview</div>
                <div class="text-[10px] text-dark-400 mt-0.5">Real-time code generation<br>from visual conditions</div>
              </div>
              <div class="rounded-lg bg-dark-800/60 border border-white/[0.04] p-3 text-center">
                <div class="text-lg mb-1">📊</div>
                <div class="text-[11px] font-medium text-white/80">Result Dashboard</div>
                <div class="text-[10px] text-dark-400 mt-0.5">OHLCV chart + markers<br>Stats, equity, trade table</div>
              </div>
              <div class="rounded-lg bg-dark-800/60 border border-white/[0.04] p-3 text-center">
                <div class="text-lg mb-1">🔄</div>
                <div class="text-[11px] font-medium text-white/80">Job Tracker</div>
                <div class="text-[10px] text-dark-400 mt-0.5">Progress polling (2s)<br>Multiple concurrent jobs</div>
              </div>
              <div class="rounded-lg bg-dark-800/60 border border-rose-500/15 p-3 text-center">
                <div class="text-lg mb-1">🎙️</div>
                <div class="text-[11px] font-medium text-white/80">Voice AI Agent</div>
                <div class="text-[10px] text-dark-400 mt-0.5">OpenAI Realtime WebRTC<br>In-browser function calling</div>
              </div>
            </div>
          </div>

          <!-- Arrow down -->
          <div class="flex justify-center py-1">
            <div class="flex flex-col items-center">
              <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3" /></svg>
              <span class="text-[9px] text-dark-500 font-mono mt-0.5">POST /api/backtests</span>
            </div>
          </div>

          <!-- Middle row: Backend -->
          <div class="rounded-xl border border-green-500/20 bg-green-500/[0.04] p-5 mb-3">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-2 h-2 rounded-full bg-green-400"></div>
              <span class="text-xs font-semibold uppercase tracking-wider text-green-300">Backend — FastAPI + Python</span>
            </div>

            <!-- API Layer -->
            <div class="rounded-lg bg-dark-800/60 border border-white/[0.04] p-4 mb-3">
              <div class="text-[11px] font-medium text-white/80 mb-2">REST API Layer</div>
              <div class="flex flex-wrap gap-2 text-[10px] font-mono">
                <span class="px-2 py-1 rounded bg-dark-700 text-green-300">POST /api/backtests</span>
                <span class="px-2 py-1 rounded bg-dark-700 text-green-300">GET /api/backtests/{id}</span>
                <span class="px-2 py-1 rounded bg-dark-700 text-dark-300">GET /api/strategies</span>
                <span class="px-2 py-1 rounded bg-dark-700 text-dark-300">POST /api/compile</span>
                <span class="px-2 py-1 rounded bg-dark-700 text-dark-300">GET /api/symbols</span>
              </div>
            </div>

            <!-- Two columns: Compiler + Backtester -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <!-- PineScript Compiler -->
              <div class="rounded-lg bg-dark-800/60 border border-purple-500/10 p-4">
                <div class="flex items-center gap-2 mb-3">
                  <div class="text-sm">🔧</div>
                  <div class="text-[11px] font-medium text-purple-300">PineScript v6 Compiler</div>
                </div>
                <div class="flex items-center gap-1.5 text-[10px] font-mono">
                  <span class="px-2 py-1 rounded bg-purple-500/10 text-purple-300">Tokenizer</span>
                  <span class="text-dark-500">→</span>
                  <span class="px-2 py-1 rounded bg-purple-500/10 text-purple-300">Parser</span>
                  <span class="text-dark-500">→</span>
                  <span class="px-2 py-1 rounded bg-purple-500/10 text-purple-300">AST</span>
                  <span class="text-dark-500">→</span>
                  <span class="px-2 py-1 rounded bg-purple-500/10 text-purple-300">Codegen</span>
                </div>
                <div class="text-[10px] text-dark-400 mt-2">Outputs: 4-signal model (long entry/exit, short entry/exit)</div>
              </div>

              <!-- Background Task + Backtester -->
              <div class="rounded-lg bg-dark-800/60 border border-amber-500/10 p-4">
                <div class="flex items-center gap-2 mb-3">
                  <div class="text-sm">⚡</div>
                  <div class="text-[11px] font-medium text-amber-300">Background Task Runner</div>
                </div>
                <div class="space-y-1.5 text-[10px]">
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                    <span class="text-dark-300">Load 1m OHLCV from TimescaleDB</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                    <span class="text-dark-300">Resample to target timeframe</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                    <span class="text-dark-300">Execute signals (standard or magnifier)</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                    <span class="text-dark-300">vectorbt Portfolio.from_signals()</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                    <span class="text-dark-300">Extract metrics, charts, trades</span>
                  </div>
                </div>
                <div class="text-[10px] text-dark-500 mt-2">Progress: 0→100% reported to DB in real-time</div>
              </div>
            </div>
          </div>

          <!-- Arrow down -->
          <div class="flex justify-center py-1">
            <div class="flex flex-col items-center">
              <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3" /></svg>
              <span class="text-[9px] text-dark-500 font-mono mt-0.5">PgBouncer (connection pool)</span>
            </div>
          </div>

          <!-- Bottom row: Database -->
          <div class="rounded-xl border border-orange-500/20 bg-orange-500/[0.04] p-5 mb-6">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-2 h-2 rounded-full bg-orange-400"></div>
              <span class="text-xs font-semibold uppercase tracking-wider text-orange-300">Database — TimescaleDB (PostgreSQL 16)</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="rounded-lg bg-dark-800/60 border border-white/[0.04] p-3">
                <div class="text-[11px] font-medium text-white/80 mb-1">ohlcv (hypertable)</div>
                <div class="text-[10px] text-dark-400">SPY 1-minute candles, 2008-2021<br>~1.4M rows, 7-day chunk intervals<br>Compressed after 30 days</div>
              </div>
              <div class="rounded-lg bg-dark-800/60 border border-white/[0.04] p-3">
                <div class="text-[11px] font-medium text-white/80 mb-1">backtests (job table)</div>
                <div class="text-[10px] text-dark-400">Strategy name, PineScript source<br>Status + progress tracking (0-100%)<br>Full result JSON (charts, trades, stats)</div>
              </div>
            </div>
          </div>

          <!-- Result flow -->
          <div class="rounded-xl border border-white/[0.06] bg-dark-800/30 p-5">
            <h4 class="font-semibold mb-4 text-sm">Backtest Result Includes</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
              <div class="rounded-lg bg-dark-700/50 p-3">
                <div class="text-lg mb-1">📈</div>
                <div class="text-[11px] font-medium text-white/70">OHLCV Bars</div>
                <div class="text-[10px] text-dark-400">Candlestick + volume</div>
              </div>
              <div class="rounded-lg bg-dark-700/50 p-3">
                <div class="text-lg mb-1">🎯</div>
                <div class="text-[11px] font-medium text-white/70">Trade Markers</div>
                <div class="text-[10px] text-dark-400">Entry/exit on chart</div>
              </div>
              <div class="rounded-lg bg-dark-700/50 p-3">
                <div class="text-lg mb-1">📋</div>
                <div class="text-[11px] font-medium text-white/70">Performance</div>
                <div class="text-[10px] text-dark-400">CAGR, Sharpe, DD, etc.</div>
              </div>
              <div class="rounded-lg bg-dark-700/50 p-3">
                <div class="text-lg mb-1">📊</div>
                <div class="text-[11px] font-medium text-white/70">Trade Log</div>
                <div class="text-[10px] text-dark-400">Every entry/exit + PnL</div>
              </div>
            </div>
          </div>

          <!-- Voice AI Agent — WebRTC Flow -->
          <div class="rounded-xl border border-rose-500/20 bg-rose-500/[0.04] p-5 mt-6">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-2 h-2 rounded-full bg-rose-400"></div>
              <span class="text-xs font-semibold uppercase tracking-wider text-rose-300">Voice AI Agent — OpenAI Realtime via WebRTC</span>
            </div>

            <div class="flex flex-col md:flex-row items-stretch gap-3">
              <!-- Browser side -->
              <div class="flex-1 rounded-lg bg-dark-800/60 border border-white/[0.04] p-4">
                <div class="flex items-center gap-2 mb-2">
                  <div class="text-sm">🎙️</div>
                  <div class="text-[11px] font-medium text-rose-300">Result Page (Browser)</div>
                </div>
                <div class="space-y-1.5 text-[10px]">
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                    <span class="text-dark-300">User clicks mic → WebRTC peer connection</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                    <span class="text-dark-300">Microphone audio streamed to OpenAI</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                    <span class="text-dark-300">AI voice response played via &lt;audio&gt;</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                    <span class="text-white/70 font-medium">Function calls resolved from local data</span>
                  </div>
                </div>
              </div>

              <!-- Connection arrows -->
              <div class="flex md:flex-col items-center justify-center gap-1 py-2 md:py-0 md:px-2">
                <div class="flex flex-col items-center gap-0.5">
                  <svg class="w-5 h-5 text-rose-400 rotate-90 md:rotate-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
                  <span class="text-[8px] text-dark-500 font-mono">audio + data</span>
                </div>
                <div class="flex flex-col items-center gap-0.5">
                  <svg class="w-5 h-5 text-rose-400 -rotate-90 md:rotate-180" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
                  <span class="text-[8px] text-dark-500 font-mono">voice + fn calls</span>
                </div>
              </div>

              <!-- OpenAI side -->
              <div class="flex-1 rounded-lg bg-dark-800/60 border border-white/[0.04] p-4">
                <div class="flex items-center gap-2 mb-2">
                  <div class="text-sm">🤖</div>
                  <div class="text-[11px] font-medium text-rose-300">OpenAI Realtime API</div>
                </div>
                <div class="space-y-1.5 text-[10px]">
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                    <span class="text-dark-300">gpt-4o-mini-realtime-preview model</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                    <span class="text-dark-300">Voice activity detection (VAD)</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                    <span class="text-dark-300">3 tools: metrics, trades, strategy info</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                    <span class="text-dark-300">Streaming voice response</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- SDP proxy note -->
            <div class="mt-3 flex items-center gap-2 rounded-lg bg-dark-800/40 border border-white/[0.03] px-4 py-2.5">
              <span class="text-[10px] text-dark-400">
                <span class="text-green-400 font-medium">FastAPI</span> proxies the initial SDP handshake (keeps API key server-side).
                After session creation, all communication flows <span class="text-rose-300 font-medium">directly between the browser and OpenAI</span> — the backend is not in the hot path.
              </span>
            </div>
          </div>
        </div>

        <!-- Tech Stack (merged into Architecture) -->
        <div class="max-w-5xl mx-auto mt-12">
          <h3 class="text-xl font-bold text-center mb-6">Tech Stack</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div
              v-for="stack in techStack"
              :key="stack.category"
              class="rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm p-6"
            >
              <div class="flex items-center gap-2 mb-5">
                <div class="w-2 h-2 rounded-full" :class="stack.dot"></div>
                <h3 class="font-semibold text-sm uppercase tracking-wider text-dark-200">{{ stack.category }}</h3>
              </div>
              <div class="space-y-3">
                <div v-for="tech in stack.items" :key="tech.name" class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-md bg-dark-700/60 flex items-center justify-center text-xs font-bold text-dark-300 shrink-0">
                    {{ tech.abbr }}
                  </div>
                  <div>
                    <div class="text-sm font-medium">{{ tech.name }}</div>
                    <div class="text-[11px] text-dark-400">{{ tech.role }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI Workflow -->
    <section class="relative z-10 py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">How It Was Built</h2>
          <p class="text-dark-300 max-w-xl mx-auto">AI-assisted development process and timeline.</p>
        </div>
        <div class="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-5">
          <div
            v-for="item in aiWorkflow"
            :key="item.title"
            class="rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm p-6 text-center"
          >
            <div class="w-12 h-12 rounded-xl bg-accent-500/10 flex items-center justify-center mx-auto mb-4 text-2xl">
              {{ item.emoji }}
            </div>
            <h4 class="font-semibold mb-2">{{ item.title }}</h4>
            <p class="text-xs text-dark-400 leading-relaxed">{{ item.description }}</p>
          </div>
        </div>
        <div class="mt-10 max-w-4xl mx-auto rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm p-6">
          <h4 class="font-semibold text-sm mb-4">Development Timeline</h4>
          <div class="flex items-center gap-3 overflow-x-auto pb-2">
            <div v-for="(phase, i) in devPhases" :key="i" class="flex items-center gap-3 shrink-0">
              <div class="text-center">
                <div class="text-xs font-mono text-accent-400">{{ phase.label }}</div>
                <div class="text-[10px] text-dark-500 mt-0.5">{{ phase.detail }}</div>
              </div>
              <svg v-if="i < devPhases.length - 1" class="w-4 h-4 text-dark-600 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How to Run -->
    <section class="relative z-10 py-24 bg-dark-900/40">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">Try It Yourself</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Clone, run, and verify — everything is reproducible in minutes.</p>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Local Dev -->
          <div class="rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm overflow-hidden">
            <div class="flex items-center gap-2 px-5 py-3 border-b border-white/[0.06] bg-dark-800/60">
              <div class="w-2.5 h-2.5 rounded-full bg-red-500/60"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/60"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-green-500/60"></div>
              <span class="text-xs text-dark-400 ml-2 font-mono">Local Development</span>
            </div>
            <pre class="p-5 text-sm font-mono text-dark-200 leading-relaxed overflow-x-auto"><span class="text-dark-500"># Clone & setup</span>
<span class="text-accent-400">git</span> clone {{ githubUrl }}.git
<span class="text-accent-400">cd</span> pineback

<span class="text-dark-500"># Start TimescaleDB + PgBouncer</span>
<span class="text-accent-400">cd</span> server/docker && docker compose up -d && cd ../..

<span class="text-dark-500"># Install deps & ingest SPY data</span>
<span class="text-accent-400">pip</span> install -r server/requirements.txt
<span class="text-accent-400">python</span> -m server.ingest

<span class="text-dark-500"># Start backend</span>
<span class="text-accent-400">uvicorn</span> server.main:app --reload --port 8000

<span class="text-dark-500"># Frontend (new terminal)</span>
<span class="text-accent-400">cd</span> frontend && npm install && npm run dev

<span class="text-dark-500"># Voice AI (optional — set before starting backend)</span>
<span class="text-accent-400">export</span> OPENAI_API_KEY="sk-..."</pre>
          </div>

          <!-- Docker / Cloud -->
          <div class="rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm overflow-hidden">
            <div class="flex items-center gap-2 px-5 py-3 border-b border-white/[0.06] bg-dark-800/60">
              <div class="w-2.5 h-2.5 rounded-full bg-red-500/60"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/60"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-green-500/60"></div>
              <span class="text-xs text-dark-400 ml-2 font-mono">Production (Docker) / Cloud (Terraform)</span>
            </div>
            <pre class="p-5 text-sm font-mono text-dark-200 leading-relaxed overflow-x-auto"><span class="text-dark-500"># Docker — full stack on localhost</span>
<span class="text-accent-400">docker</span> compose -f docker-compose.prod.yml up -d --build
<span class="text-accent-400">docker</span> compose -f docker-compose.prod.yml exec \
  app python -m server.ingest
<span class="text-accent-400">open</span> http://localhost

<span class="text-dark-500"># Cloud — one-command AWS deploy</span>
<span class="text-accent-400">cd</span> infra
<span class="text-accent-400">cp</span> terraform.tfvars.example terraform.tfvars
<span class="text-dark-500"># Edit: key_pair, repo_url, domain, openai_api_key</span>
<span class="text-accent-400">terraform</span> init && terraform apply
<span class="text-dark-500"># Auto: Docker build, data ingest, SSL setup</span>
<span class="text-dark-500"># Output: https://your-domain.example.com</span></pre>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer CTA -->
    <section class="relative z-10 py-24">
      <div class="max-w-7xl mx-auto px-6 text-center">
        <h2 class="text-3xl sm:text-4xl font-bold mb-4">See It in Action</h2>
        <p class="text-dark-300 mb-10 max-w-lg mx-auto">Build a strategy, run a backtest, and explore the results — all in your browser, no setup required.</p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <router-link
            to="/app"
            class="group inline-flex items-center gap-2 px-8 py-3.5 bg-accent-500 hover:bg-accent-600 rounded-lg font-semibold transition-all hover:shadow-lg hover:shadow-accent-500/25"
          >
            Launch App
            <svg class="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </router-link>
          <a
            :href="githubUrl"
            target="_blank"
            class="inline-flex items-center gap-2 px-8 py-3.5 rounded-lg font-semibold border border-dark-600 hover:border-dark-400 text-dark-200 hover:text-white transition-all"
          >
            View on GitHub
          </a>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="relative z-10 border-t border-white/[0.06] py-8">
      <div class="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="text-xs text-dark-500">PineBack &middot; Built as an interview project &middot; 2025-2026</div>
        <div class="flex items-center gap-4 text-xs text-dark-500">
          <a :href="githubUrl" target="_blank" class="hover:text-dark-300 transition-colors">GitHub</a>
          <span>&middot;</span>
          <span>Python + Vue + TimescaleDB</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUIScale } from '../composables/useUIScale.js'

const { scale, scaleUp, scaleDown, resetScale } = useUIScale()
const githubUrl = 'https://github.com/luisleo526/pineback'

// Hero stat previews
const heroStats = [
  { label: 'CAGR', value: '+18.4%', color: 'text-green-400' },
  { label: 'Sharpe Ratio', value: '2.15', color: 'text-accent-400' },
  { label: 'Max Drawdown', value: '12.5%', color: 'text-red-400' },
  { label: 'Win Rate', value: '57.1%', color: 'text-green-400' },
]

// Simulated equity curve bars
const equityBars = ref(
  Array.from({ length: 60 }, (_, i) => {
    const base = 20 + (i / 60) * 55
    const noise = Math.sin(i * 0.5) * 12 + Math.cos(i * 0.3) * 8
    return Math.max(5, Math.min(98, base + noise))
  })
)

// Features
const features = [
  {
    title: 'No-Code Strategy Builder',
    description: 'Visual drag-and-drop interface for building trading strategies. Select indicators, set conditions, and configure entry/exit logic without writing code.',
    useCase: 'Non-technical users can create strategies in minutes',
    icon: '<svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" /></svg>',
  },
  {
    title: 'PineScript v6 Compiler',
    description: 'Full tokenizer → parser → AST → codegen pipeline that compiles PineScript v6 into vectorized Python functions for high-performance execution.',
    useCase: 'Import strategies directly from TradingView',
    icon: '<svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" /></svg>',
  },
  {
    title: 'Standard + Magnifier Modes',
    description: 'Standard mode uses bar-close fills. Magnifier mode resamples to 1-min candles for realistic intra-bar execution on higher timeframes.',
    useCase: 'Compare idealized vs realistic backtest results',
    icon: '<svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" /></svg>',
  },
  {
    title: 'TradingView-Style Charts',
    description: 'Interactive OHLCV candlestick charts, equity curves, and drawdown visualizations powered by lightweight-charts with crosshairs and zoom.',
    useCase: 'Visually inspect trades and market context',
    icon: '<svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>',
  },
  {
    title: 'Real-Time Progress Tracking',
    description: 'Live polling shows backtest status, progress percentage, and intermediate results while the engine processes your strategy.',
    useCase: 'Monitor long-running backtests without page refresh',
    icon: '<svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>',
  },
  {
    title: '12 Strategy Templates',
    description: 'Pre-built templates including SMA crossover, RSI mean reversion, MACD momentum, Bollinger breakout, and more — ready to run or customize.',
    useCase: 'Quick-start backtesting without building from scratch',
    icon: '<svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>',
  },
  {
    title: 'Voice AI Agent',
    description: 'Discuss backtest results with an AI analyst via voice. Powered by OpenAI Realtime API over WebRTC — the agent uses function calling to fetch metrics and trades, resolved entirely in the browser from local data.',
    useCase: 'Get instant spoken insights on strategy performance',
    icon: '<svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" /></svg>',
  },
]

// Metrics — must match the 4×4 grid in StatsCards.vue
const metrics = [
  // Row 1
  { name: 'Net Profit', sample: '+$1,842', formula: 'Final value - Initial capital', color: 'text-green-400' },
  { name: 'CAGR', sample: '+18.4%', formula: 'Compound annual growth rate', color: 'text-green-400' },
  { name: 'Ann. Volatility', sample: '14.2%', formula: 'Std dev of returns \u00D7 \u221A252', color: 'text-white' },
  { name: 'Max Drawdown', sample: '12.5%', formula: 'Largest peak-to-trough', color: 'text-red-400' },
  // Row 2
  { name: 'Sharpe Ratio', sample: '2.15', formula: '(Return - Rf) / Volatility', color: 'text-accent-400' },
  { name: 'Sortino Ratio', sample: '3.20', formula: 'Return / Downside deviation', color: 'text-accent-400' },
  { name: 'Profit Factor', sample: '1.85', formula: 'Gross profit / Gross loss', color: 'text-green-400' },
  { name: 'Expectancy', sample: '$106.75', formula: 'Avg win \u00D7 WR - Avg loss \u00D7 LR', color: 'text-green-400' },
  // Row 3
  { name: 'Total Trades', sample: '28', formula: 'Round-trip count', color: 'text-white' },
  { name: 'Win Rate', sample: '57.1%', formula: 'Winning trades / Total', color: 'text-green-400' },
  { name: 'Best Trade', sample: '+8.3%', formula: 'Highest single return', color: 'text-green-400' },
  { name: 'Worst Trade', sample: '-4.1%', formula: 'Lowest single return', color: 'text-red-400' },
  // Row 4
  { name: 'Avg Winning Trade', sample: '+3.2%', formula: 'Mean return of winners', color: 'text-green-400' },
  { name: 'Avg Losing Trade', sample: '-1.8%', formula: 'Mean return of losers', color: 'text-red-400' },
  { name: 'Avg Win Duration', sample: '3d 4h', formula: 'Mean holding period (wins)', color: 'text-white/70' },
  { name: 'Avg Loss Duration', sample: '1d 12h', formula: 'Mean holding period (losses)', color: 'text-white/70' },
]

// Tech stack
const techStack = [
  {
    category: 'Backend',
    dot: 'bg-green-400',
    items: [
      { name: 'Python 3.11', abbr: 'Py', role: 'Runtime' },
      { name: 'FastAPI', abbr: 'FA', role: 'Async REST framework' },
      { name: 'SQLAlchemy 2.0', abbr: 'SA', role: 'ORM + migrations' },
      { name: 'vectorbt', abbr: 'vbt', role: 'Vectorized backtest engine' },
      { name: 'TimescaleDB', abbr: 'TS', role: 'Time-series hypertables' },
      { name: 'PgBouncer', abbr: 'PB', role: 'Connection pooling' },
    ],
  },
  {
    category: 'Frontend',
    dot: 'bg-blue-400',
    items: [
      { name: 'Vue 3', abbr: 'V3', role: 'Composition API SPA' },
      { name: 'Vite', abbr: 'Vi', role: 'Build tool + HMR' },
      { name: 'Tailwind CSS', abbr: 'TW', role: 'Utility-first styling' },
      { name: 'lightweight-charts', abbr: 'LC', role: 'TradingView charting' },
    ],
  },
  {
    category: 'Infrastructure',
    dot: 'bg-amber-400',
    items: [
      { name: 'Docker Compose', abbr: 'DC', role: 'Container orchestration' },
      { name: 'Terraform', abbr: 'TF', role: 'IaC provisioning' },
      { name: 'AWS EC2', abbr: 'EC', role: 'Compute instance' },
      { name: 'nginx', abbr: 'nx', role: 'Reverse proxy + TLS' },
      { name: "Let's Encrypt", abbr: 'LE', role: 'Free TLS certificates' },
    ],
  },
]

// Assumptions
const assumptions = [
  { title: 'PineScript v6 — TradingView Compatible', detail: 'PineBack adopts PineScript v6 because TradingView has the largest global algo-trading community. Strategies generated here are valid PineScript — you can paste them directly into TradingView and they will work. One strategy, two platforms.' },
  { title: 'SPY Only (by default)', detail: 'SPY 1-minute OHLCV data sourced from Kaggle (kaggle.com/datasets/rockinbrock/spy-1-minute-data). The architecture supports multiple symbols via the DataSource protocol, but SPY is the default for the interview demo.' },
  { title: 'Stateless Strategies', detail: 'Strategies are pure functions of price data — no portfolio state carryover between bars. This matches the PineScript execution model and simplifies the compiler.' },
  { title: 'Configurable Commission & Slippage', detail: 'Default: 0.1% commission, 0.05% slippage per trade. Both are configurable in the backtest config panel to model different broker scenarios.' },
  { title: 'Magnifier vs Standard Mode', detail: 'Standard mode fills at bar close. Magnifier mode resamples higher-TF signals to 1-min candles for realistic intra-bar execution — critical for accurate limit/stop orders.' },
  { title: 'Voice AI requires OPENAI_API_KEY', detail: 'The Voice AI Agent on the result page uses OpenAI\'s Realtime API (gpt-4o-mini-realtime-preview) over WebRTC. Set the OPENAI_API_KEY environment variable before starting the backend. Without it, all other features work normally.' },
]

// AI Workflow
const aiWorkflow = [
  { emoji: '\uD83E\uDDE0', title: 'Cursor IDE + Claude', description: 'AI-powered development using Cursor IDE with Claude as the coding assistant for rapid prototyping and iteration.' },
  { emoji: '\uD83D\uDCDA', title: 'Custom Skills', description: 'Domain-specific skill files for PineScript compilation, vectorbt backtesting, TimescaleDB schemas, and frontend patterns.' },
  { emoji: '\uD83D\uDD04', title: 'Incremental Commits', description: '24+ atomic commits with clear messages. Each commit builds on the last — traceable development history.' },
]

const devPhases = [
  { label: 'Phase 1', detail: 'DB + Ingestion' },
  { label: 'Phase 2', detail: 'API + Engine' },
  { label: 'Phase 3', detail: 'Pine Compiler' },
  { label: 'Phase 4', detail: 'Frontend UI' },
  { label: 'Phase 5', detail: 'Strategy Builder' },
  { label: 'Phase 6', detail: 'Deploy + Polish' },
]

</script>
