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
          <span class="text-sm font-semibold tracking-wide">BACKTEST SYSTEM</span>
        </div>
        <div class="flex items-center gap-6">
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
            US Stock
            <span class="bg-gradient-to-r from-accent-400 to-accent-600 bg-clip-text text-transparent"> Backtesting</span>
            <br />System
          </h1>
          <p class="text-lg sm:text-xl text-dark-300 max-w-2xl mx-auto mb-10 leading-relaxed">
            A production-grade quantitative backtesting platform featuring a visual strategy builder,
            PineScript v6 compiler, dual execution engines, and TradingView-style charting.
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
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">Key Features</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Everything you need to define, compile, and backtest quantitative trading strategies.</p>
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

    <!-- Metrics -->
    <section class="relative z-10 py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">Computed Metrics</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Every backtest produces a comprehensive set of risk-adjusted performance metrics.</p>
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

    <!-- Architecture -->
    <section class="relative z-10 py-24 bg-dark-900/40">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">Architecture</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Request lifecycle from browser to database and back.</p>
        </div>

        <!-- Architecture flow diagram -->
        <div class="max-w-5xl mx-auto">
          <div class="flex flex-col items-center gap-3">
            <div v-for="(layer, i) in archLayers" :key="layer.name" class="w-full">
              <div class="rounded-xl border border-white/[0.06] bg-dark-800/40 backdrop-blur-sm p-5 flex items-center gap-5">
                <div class="w-11 h-11 rounded-lg shrink-0 flex items-center justify-center text-lg" :class="layer.bg">
                  {{ layer.emoji }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-0.5">
                    <h4 class="font-semibold text-sm">{{ layer.name }}</h4>
                    <span class="text-[10px] px-2 py-0.5 rounded-full bg-dark-700 text-dark-300 font-mono">{{ layer.tech }}</span>
                  </div>
                  <p class="text-xs text-dark-400 leading-relaxed">{{ layer.desc }}</p>
                </div>
              </div>
              <div v-if="i < archLayers.length - 1" class="flex justify-center py-1">
                <svg class="w-5 h-5 text-dark-600" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3" /></svg>
              </div>
            </div>
          </div>

          <div class="mt-10 rounded-xl border border-white/[0.06] bg-dark-800/30 p-6">
            <h4 class="font-semibold mb-3 text-sm">Request Lifecycle</h4>
            <div class="flex flex-wrap items-center gap-2 text-xs font-mono">
              <span v-for="(step, i) in pipelineSteps" :key="i" class="flex items-center gap-2">
                <span class="px-3 py-1.5 rounded-md bg-dark-700 text-dark-200 whitespace-nowrap">{{ step }}</span>
                <svg v-if="i < pipelineSteps.length - 1" class="w-4 h-4 text-accent-500 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech Stack -->
    <section class="relative z-10 py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">Tech Stack</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Built with modern, production-proven technologies.</p>
        </div>
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
    </section>

    <!-- How to Run -->
    <section class="relative z-10 py-24 bg-dark-900/40">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">How to Run</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Get up and running in minutes with local development or Docker deployment.</p>
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
<span class="text-accent-400">cd</span> backtest-system

<span class="text-dark-500"># Backend</span>
<span class="text-accent-400">cd</span> backend
<span class="text-accent-400">python</span> -m venv .venv && source .venv/bin/activate
<span class="text-accent-400">pip</span> install -r requirements.txt
<span class="text-accent-400">uvicorn</span> app.main:app --reload --port 8000

<span class="text-dark-500"># Frontend (new terminal)</span>
<span class="text-accent-400">cd</span> frontend
<span class="text-accent-400">npm</span> install && npm run dev</pre>
          </div>

          <!-- Docker -->
          <div class="rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm overflow-hidden">
            <div class="flex items-center gap-2 px-5 py-3 border-b border-white/[0.06] bg-dark-800/60">
              <div class="w-2.5 h-2.5 rounded-full bg-red-500/60"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/60"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-green-500/60"></div>
              <span class="text-xs text-dark-400 ml-2 font-mono">Docker Deployment</span>
            </div>
            <pre class="p-5 text-sm font-mono text-dark-200 leading-relaxed overflow-x-auto"><span class="text-dark-500"># Single command — full stack</span>
<span class="text-accent-400">docker</span> compose up --build -d

<span class="text-dark-500"># Services started:</span>
<span class="text-dark-500">#   web        → nginx + Vue SPA     :443</span>
<span class="text-dark-500">#   api        → FastAPI + uvicorn    :8000</span>
<span class="text-dark-500">#   db         → TimescaleDB          :5432</span>
<span class="text-dark-500">#   pgbouncer  → connection pooler    :6432</span>

<span class="text-dark-500"># Ingest market data</span>
<span class="text-accent-400">docker</span> compose exec api python -m app.ingest

<span class="text-dark-500"># Open in browser</span>
<span class="text-accent-400">open</span> https://localhost</pre>
          </div>
        </div>
      </div>
    </section>

    <!-- Key Assumptions -->
    <section class="relative z-10 py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">Key Assumptions</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Design decisions and scope boundaries for this interview project.</p>
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

    <!-- AI Workflow -->
    <section class="relative z-10 py-24 bg-dark-900/40">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">AI-Assisted Development</h2>
          <p class="text-dark-300 max-w-xl mx-auto">How this project was built with modern AI tooling.</p>
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

    <!-- Bonus Features -->
    <section class="relative z-10 py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold mb-4">Bonus Features</h2>
          <p class="text-dark-300 max-w-xl mx-auto">Above and beyond the core requirements.</p>
        </div>
        <div class="max-w-5xl mx-auto rounded-xl border border-white/[0.06] bg-dark-800/30 backdrop-blur-sm overflow-hidden">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-white/[0.06] bg-dark-800/60">
                <th class="text-left px-6 py-3.5 font-semibold text-dark-200 text-xs uppercase tracking-wider">Feature</th>
                <th class="text-left px-6 py-3.5 font-semibold text-dark-200 text-xs uppercase tracking-wider">Description</th>
                <th class="text-left px-6 py-3.5 font-semibold text-dark-200 text-xs uppercase tracking-wider hidden md:table-cell">Use Case</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(bonus, i) in bonusFeatures"
                :key="bonus.name"
                class="border-b border-white/[0.04] last:border-0 hover:bg-dark-700/20 transition-colors"
              >
                <td class="px-6 py-4 font-medium text-accent-400 whitespace-nowrap">{{ bonus.name }}</td>
                <td class="px-6 py-4 text-dark-300">{{ bonus.description }}</td>
                <td class="px-6 py-4 text-dark-400 text-xs hidden md:table-cell">{{ bonus.useCase }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- Footer CTA -->
    <section class="relative z-10 py-24 bg-dark-900/40">
      <div class="max-w-7xl mx-auto px-6 text-center">
        <h2 class="text-3xl sm:text-4xl font-bold mb-4">Ready to Explore?</h2>
        <p class="text-dark-300 mb-10 max-w-lg mx-auto">Launch the app to build a strategy, run a backtest, and view the results — all in your browser.</p>
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
        <div class="text-xs text-dark-500">Built as an interview project &middot; 2025</div>
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

const githubUrl = 'https://github.com/YOUR_USERNAME/backtest-system'

// Hero stat previews
const heroStats = [
  { label: 'CAGR', value: '+18.4%', color: 'text-green-400' },
  { label: 'Sharpe Ratio', value: '2.15', color: 'text-accent-400' },
  { label: 'Max Drawdown', value: '-12.5%', color: 'text-red-400' },
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
]

// Metrics
const metrics = [
  { name: 'CAGR', sample: '+18.4%', formula: 'Compound annual growth rate', color: 'text-green-400' },
  { name: 'Ann. Volatility', sample: '14.2%', formula: 'Std dev of returns \u00D7 \u221A252', color: 'text-white' },
  { name: 'Sharpe Ratio', sample: '2.15', formula: '(Return - Rf) / Volatility', color: 'text-accent-400' },
  { name: 'Sortino Ratio', sample: '3.20', formula: 'Return / Downside deviation', color: 'text-accent-400' },
  { name: 'Calmar Ratio', sample: '1.85', formula: 'CAGR / Max drawdown', color: 'text-accent-400' },
  { name: 'Max Drawdown', sample: '-12.5%', formula: 'Largest peak-to-trough', color: 'text-red-400' },
  { name: 'Profit Factor', sample: '1.85', formula: 'Gross profit / Gross loss', color: 'text-green-400' },
  { name: 'Win Rate', sample: '57.1%', formula: 'Winning trades / Total', color: 'text-green-400' },
  { name: 'Expectancy', sample: '$106.75', formula: 'Avg win \u00D7 WR - Avg loss \u00D7 LR', color: 'text-green-400' },
  { name: 'Total Trades', sample: '28', formula: 'Round-trip count', color: 'text-white' },
  { name: 'Best Trade', sample: '+8.3%', formula: 'Highest single return', color: 'text-green-400' },
  { name: 'Worst Trade', sample: '-4.1%', formula: 'Lowest single return', color: 'text-red-400' },
]

// Architecture layers
const archLayers = [
  { name: 'Browser', tech: 'Vue 3 + Vite', emoji: '\uD83C\uDF10', bg: 'bg-blue-500/15', desc: 'SPA with strategy builder, code editor, TradingView-style charting, and real-time polling.' },
  { name: 'Reverse Proxy', tech: 'nginx', emoji: '\uD83D\uDEE1\uFE0F', bg: 'bg-amber-500/15', desc: 'TLS termination (Let\'s Encrypt), static file serving, API proxying to upstream.' },
  { name: 'API Server', tech: 'FastAPI', emoji: '\u26A1', bg: 'bg-green-500/15', desc: 'Async REST endpoints for submitting strategies, tracking jobs, and returning results.' },
  { name: 'Task Runner', tech: 'BackgroundTasks', emoji: '\u2699\uFE0F', bg: 'bg-purple-500/15', desc: 'PineScript compiler parses strategy into signals; vectorbt executes backtest with market data.' },
  { name: 'Database', tech: 'TimescaleDB', emoji: '\uD83D\uDDC4\uFE0F', bg: 'bg-orange-500/15', desc: 'Hypertable for OHLCV candles with compression. PgBouncer for connection pooling.' },
]

const pipelineSteps = [
  'POST /api/backtests',
  'Validate & Save',
  'Background Task',
  'Compile PineScript',
  'Load OHLCV Data',
  'vectorbt Backtest',
  'Compute Metrics',
  'Store Results',
  'Poll → Render',
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
  { title: 'SPY Only (by default)', detail: 'The system ingests SPY OHLCV data from Yahoo Finance. The architecture supports multiple symbols via the DataSource protocol, but SPY is the default for the interview demo.' },
  { title: 'Stateless Strategies', detail: 'Strategies are pure functions of price data — no portfolio state carryover between bars. This matches the PineScript execution model and simplifies the compiler.' },
  { title: 'Configurable Commission & Slippage', detail: 'Default: 0.1% commission, 0.05% slippage per trade. Both are configurable in the backtest config panel to model different broker scenarios.' },
  { title: 'Magnifier vs Standard Mode', detail: 'Standard mode fills at bar close. Magnifier mode resamples higher-TF signals to 1-min candles for realistic intra-bar execution — critical for accurate limit/stop orders.' },
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

// Bonus Features
const bonusFeatures = [
  { name: 'Visual Strategy Builder', description: 'Drag-and-drop interface for building strategies without code', useCase: 'Non-technical users can create and test strategies' },
  { name: 'PineScript v6 Compiler', description: 'Full 4-stage compiler pipeline: tokenize → parse → AST → codegen', useCase: 'Import existing TradingView strategies' },
  { name: 'Magnifier Mode', description: 'Resample HT signals to 1-min bars for intra-bar execution', useCase: 'Realistic fill simulation for limit/stop orders' },
  { name: 'OHLCV Candlestick Chart', description: 'Interactive TradingView-style chart with buy/sell markers', useCase: 'Visual trade inspection with market context' },
  { name: '12 Strategy Templates', description: 'Pre-built strategies covering major TA categories', useCase: 'Instant backtesting without strategy creation' },
  { name: 'Drawdown Analysis', description: 'Underwater chart + top-N drawdown table with duration', useCase: 'Risk assessment and worst-case scenario analysis' },
  { name: 'Job Progress Tracking', description: 'Real-time status polling with progress percentage', useCase: 'Monitor multi-minute backtests without page refresh' },
  { name: 'IaC Deployment', description: 'Terraform + Docker Compose for reproducible infrastructure', useCase: 'One-command deployment to AWS' },
]
</script>
