<template>
  <div class="operand-selector" ref="selectorRef">
    <!-- Display Mode (always visible, click to open edit panel) -->
    <div 
      @click="startEditing"
      class="value-display-wrapper cursor-pointer hover:ring-2 hover:ring-accent-500/50 rounded transition-all"
      :class="{ 'ring-2 ring-indigo-500/50': isEditing }"
      ref="triggerRef"
      :title="modelValue.type === 'empty' || !modelValue.type ? 'Click to select: Function / Price / Variable / Constant' : 'Click to modify value or switch type'"
    >
      <ValueDisplay :value="modelValue" :variables="variables" />
    </div>

    <!-- Edit Mode (teleported to body to escape any parent overflow/backdrop-filter clipping) -->
    <Teleport to="body">
    <div 
      v-if="isEditing"
      ref="editPanelRef"
      class="edit-panel border rounded-xl p-3 shadow-xl w-[calc(100vw-16px)] sm:min-w-[300px] sm:w-auto"
      style="background: rgba(20, 24, 40, 0.96); border-color: rgba(255,255,255,0.08); backdrop-filter: blur(20px);"
      :style="panelStyle"
    >
      <!-- Header with type selector -->
      <div class="flex items-center justify-between mb-3 pb-2 border-b border-dark-700">
        <span class="text-xs text-dark-400 font-medium">Select value type</span>
        <button 
          @click="stopEditing" 
          class="text-dark-400 hover:text-white transition-colors"
        >
          <i class="fas fa-check"></i>
        </button>
      </div>

      <!-- Type Tabs -->
      <div class="flex gap-1 mb-3">
        <button
          @click="changeType('indicator')"
          :class="[
            'flex-1 px-2 py-2 sm:py-1.5 text-xs rounded transition-colors min-h-[36px]',
            modelValue.type === 'indicator' 
              ? 'bg-amber-500/20 text-amber-400 ring-1 ring-amber-500/50' 
              : 'bg-dark-700 text-dark-400 hover:text-white'
          ]"
        >
          <i class="fas fa-chart-line mr-1"></i>Function
        </button>
        <button
          @click="changeType('price')"
          :class="[
            'flex-1 px-2 py-2 sm:py-1.5 text-xs rounded transition-colors min-h-[36px]',
            modelValue.type === 'price' 
              ? 'bg-blue-500/20 text-blue-400 ring-1 ring-blue-500/50' 
              : 'bg-dark-700 text-dark-400 hover:text-white'
          ]"
        >
          <i class="fas fa-tag mr-1"></i>Price
        </button>
        <button
          v-if="variables.length > 0"
          @click="changeType('variable')"
          :class="[
            'flex-1 px-2 py-2 sm:py-1.5 text-xs rounded transition-colors min-h-[36px]',
            modelValue.type === 'variable' 
              ? 'bg-purple-500/20 text-purple-400 ring-1 ring-purple-500/50' 
              : 'bg-dark-700 text-dark-400 hover:text-white'
          ]"
        >
          <i class="fas fa-cube mr-1"></i>Variable
        </button>
        <button
          v-if="allowConstant"
          @click="changeType('constant')"
          :class="[
            'flex-1 px-2 py-2 sm:py-1.5 text-xs rounded transition-colors min-h-[36px]',
            modelValue.type === 'constant' 
              ? 'bg-cyan-500/20 text-cyan-400 ring-1 ring-cyan-500/50' 
              : 'bg-dark-700 text-dark-400 hover:text-white'
          ]"
        >
          <i class="fas fa-hashtag mr-1"></i>Constant
        </button>
        <button
          v-if="compatibleInputs.length > 0"
          @click="changeType('input')"
          :class="[
            'flex-1 px-2 py-2 sm:py-1.5 text-xs rounded transition-colors min-h-[36px]',
            modelValue.type === 'input' 
              ? 'bg-teal-500/20 text-teal-400 ring-1 ring-teal-500/50' 
              : 'bg-dark-700 text-dark-400 hover:text-white'
          ]"
        >
          <i class="fas fa-sliders-h mr-1"></i>Input
        </button>
      </div>

      <!-- Empty state hint -->
      <div v-if="modelValue.type === 'empty' || !modelValue.type" class="text-center py-3">
        <div class="text-xs text-white/30 mb-1">
          <i class="fas fa-arrow-up text-[10px] mr-1"></i>
          Please select a value type
        </div>
        <div class="text-[11px] text-white/20">
          Function: Use technical indicators like RSI, SMA<br>
          Price: Use OHLCV market data<br>
          Constant: Enter a numeric value directly<br>
          <span v-if="compatibleInputs.length > 0">Input: Use a strategy input parameter</span>
        </div>
      </div>

      <!-- Indicator Configuration -->
      <div v-else-if="modelValue.type === 'indicator'" class="space-y-3">
        <!-- Indicator Selection -->
        <div>
          <label class="block text-xs text-dark-400 mb-1">Select indicator</label>
          <select
            :value="modelValue.indicator"
            @change="changeIndicator($event.target.value)"
            class="w-full bg-dark-700 border border-dark-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
          >
            <optgroup v-for="cat in indicatorCategories" :key="cat.id" :label="cat.label">
              <option
                v-for="ind in getIndicatorsByCategory(cat.id)"
                :key="ind.id"
                :value="ind.id"
              >
                {{ ind.label }} - {{ ind.description }}
              </option>
            </optgroup>
          </select>
        </div>

        <!-- Function Preview -->
        <div v-if="currentIndicator" class="bg-dark-900 rounded p-2">
          <div class="text-xs text-dark-400 mb-1">Function preview</div>
          <div class="font-mono text-sm">
            <span class="text-amber-400">{{ currentIndicator.label }}</span>
            <span class="text-dark-400">(</span>
            <span v-for="(param, idx) in currentIndicator.params" :key="param.id">
              <span v-if="idx > 0" class="text-dark-500">, </span>
              <span :class="getParamColor(param.type)">{{ param.label }}</span>
            </span>
            <span class="text-dark-400">)</span>
            <span v-if="currentIndicatorOutputs.length > 1" class="text-green-400 ml-1">
              → {{ currentIndicatorOutputs.length }} outputs
            </span>
          </div>
        </div>

        <!-- Output Selector (for multi-output indicators) -->
        <div v-if="currentIndicatorOutputs.length > 1" class="mt-2">
          <label class="block text-xs text-dark-400 mb-1">Select output</label>
          <div class="flex flex-wrap gap-1">
            <button
              v-for="(output, idx) in currentIndicatorOutputs"
              :key="output.id"
              @click="changeOutputIndex(idx)"
              :class="[
                'px-2.5 py-1.5 text-xs rounded transition-colors border',
                (modelValue.outputIndex ?? 0) === idx
                  ? 'bg-green-500/20 text-green-400 border-green-500/50 ring-1 ring-green-500/30'
                  : 'bg-dark-700 text-dark-400 border-dark-600 hover:text-white hover:border-dark-500'
              ]"
            >
              {{ output.label }}
            </button>
          </div>
        </div>

        <!-- Parameter Configuration -->
        <div v-if="currentIndicator" class="space-y-3">
          <div class="text-xs text-dark-400 font-medium">Parameter settings</div>
          <div v-for="param in currentIndicator.params" :key="param.id" class="param-row">
            <div class="flex items-center justify-between mb-1">
              <label class="text-xs text-dark-400">{{ param.label }}</label>
              
              <!-- Type toggle for number params -->
              <div v-if="param.type === 'int' || param.type === 'float'" class="flex gap-1">
                <button
                  @click="setParamType(param.id, 'constant', param)"
                  :class="[
                    'px-2 py-0.5 text-xs rounded transition-colors',
                    !isParamVariable(param.id) && !isParamInput(param.id)
                      ? 'bg-cyan-500/20 text-cyan-400'
                      : 'bg-dark-700 text-dark-500 hover:text-dark-300'
                  ]"
                >
                  Constant
                </button>
                <button
                  v-if="variables.length > 0"
                  @click="setParamType(param.id, 'variable', param)"
                  :class="[
                    'px-2 py-0.5 text-xs rounded transition-colors',
                    isParamVariable(param.id) && !isParamInput(param.id)
                      ? 'bg-purple-500/20 text-purple-400'
                      : 'bg-dark-700 text-dark-500 hover:text-dark-300'
                  ]"
                >
                  Variable
                </button>
                <button
                  v-if="getCompatibleInputsForParam(param.type).length > 0"
                  @click="setParamType(param.id, 'input', param)"
                  :class="[
                    'px-2 py-0.5 text-xs rounded transition-colors',
                    isParamInput(param.id)
                      ? 'bg-teal-500/20 text-teal-400'
                      : 'bg-dark-700 text-dark-500 hover:text-dark-300'
                  ]"
                >
                  Input
                </button>
              </div>
            </div>
            
            <!-- Source Parameter -->
            <template v-if="param.type === 'source'">
              <div class="flex items-center justify-between mb-1">
                <div class="flex gap-1">
                  <button
                    @click="setParamType(param.id, 'price', param)"
                    :class="[
                      'px-2 py-0.5 text-xs rounded transition-colors',
                      !isParamVariable(param.id)
                        ? 'bg-blue-500/20 text-blue-400'
                        : 'bg-dark-700 text-dark-500 hover:text-dark-300'
                    ]"
                  >
                    Price
                  </button>
                  <button
                    v-if="variables.length > 0"
                    @click="setParamType(param.id, 'variable', param)"
                    :class="[
                      'px-2 py-0.5 text-xs rounded transition-colors',
                      isParamVariable(param.id)
                        ? 'bg-purple-500/20 text-purple-400'
                        : 'bg-dark-700 text-dark-500 hover:text-dark-300'
                    ]"
                  >
                    Variable
                  </button>
                </div>
              </div>
              <!-- Price source mode -->
              <select
                v-if="!isParamVariable(param.id)"
                :value="getParamSourceValue(param.id, param.default)"
                @change="updateParam(param.id, $event.target.value)"
                class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1.5 text-sm text-white focus:outline-none focus:border-accent-500"
              >
                <option v-for="src in priceSources" :key="src.id" :value="src.id">
                  {{ src.label }}
                </option>
              </select>
              <!-- Variable mode -->
              <select
                v-else
                :value="getParamVariableId(param.id)"
                @change="updateParamVariable(param.id, $event.target.value)"
                class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1.5 text-sm text-white focus:outline-none focus:border-accent-500"
              >
                <option value="" disabled>Select variable...</option>
                <option v-for="v in variables" :key="v.id" :value="v.id">
                  {{ v.name }}
                </option>
              </select>
            </template>
            
            <!-- Number Parameter - Constant Mode -->
            <template v-else-if="(param.type === 'int' || param.type === 'float') && !isParamVariable(param.id)">
              <!-- Quick-create input form (expanded) -->
              <div v-if="quickCreateParam === param.id" class="space-y-2 bg-dark-900 rounded-lg p-2.5 border border-accent-500/30">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-accent-400 font-medium">
                    <i class="fas fa-sliders-h mr-1"></i>Create adjustable input
                  </span>
                  <button @click="quickCreateParam = null" class="text-dark-400 hover:text-white text-xs">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <div class="grid grid-cols-2 gap-2">
                  <div class="col-span-2">
                    <label class="block text-xs text-dark-500 mb-0.5">Name <span class="text-white/20">(letters, digits, underscores)</span></label>
                    <input
                      :value="quickCreateForm.name"
                      @input="quickCreateForm.name = $event.target.value.replace(/[^a-zA-Z0-9_]/g, '')"
                      type="text"
                      class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500 font-mono"
                      placeholder="myParam"
                    />
                  </div>
                  <div>
                    <label class="block text-xs text-dark-500 mb-0.5">Default</label>
                    <input
                      v-model.number="quickCreateForm.default"
                      type="number"
                      :step="param.type === 'float' ? 0.1 : 1"
                      class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
                    />
                  </div>
                  <div>
                    <label class="block text-xs text-dark-500 mb-0.5">Type</label>
                    <div class="px-2 py-1 bg-dark-700 border border-dark-600 rounded text-xs text-dark-400">
                      {{ param.type === 'float' ? 'Float' : 'Integer' }}
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs text-dark-500 mb-0.5">Min</label>
                    <input
                      v-model.number="quickCreateForm.min"
                      type="number"
                      :step="param.type === 'float' ? 0.1 : 1"
                      placeholder="None"
                      class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
                    />
                  </div>
                  <div>
                    <label class="block text-xs text-dark-500 mb-0.5">Max</label>
                    <input
                      v-model.number="quickCreateForm.max"
                      type="number"
                      :step="param.type === 'float' ? 0.1 : 1"
                      placeholder="None"
                      class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
                    />
                  </div>
                </div>
                <div class="flex items-center justify-between pt-1">
                  <span class="text-xs text-dark-500 font-mono truncate max-w-[180px]" :title="quickCreatePreview(param)">
                    {{ quickCreatePreview(param) }}
                  </span>
                  <button
                    @click="confirmQuickCreate(param)"
                    class="px-3 py-1 bg-accent-600 hover:bg-accent-500 text-white text-xs rounded transition-colors"
                  >
                    <i class="fas fa-check mr-1"></i>Create
                  </button>
                </div>
              </div>
              <!-- Normal constant input + quick-create button -->
              <div v-else class="space-y-1.5">
                <div class="flex items-center gap-2">
                  <input
                    type="number"
                    :value="getParamConstantValue(param.id, param.default)"
                    @input="updateParam(param.id, parseNumber($event.target.value, param.type))"
                    :min="param.min"
                    :max="param.max"
                    :step="param.type === 'float' ? 0.1 : 1"
                    class="flex-1 bg-dark-700 border border-dark-600 rounded px-2 py-1.5 text-sm text-white focus:outline-none focus:border-accent-500"
                  />
                  <button
                    @click="openQuickCreate(param)"
                    class="px-2 py-1.5 bg-dark-600 hover:bg-dark-500 text-dark-400 hover:text-white rounded text-xs transition-colors flex items-center gap-1"
                    title="Create adjustable input (TradingView input)"
                  >
                    <i class="fas fa-sliders-h"></i>
                  </button>
                </div>
                <button
                  @click="openQuickCreate(param)"
                  class="w-full text-left text-[11px] text-white/25 hover:text-indigo-400/70 transition-colors flex items-center gap-1.5 py-0.5"
                >
                  <i class="fas fa-wand-magic-sparkles text-[9px]"></i>
                  <span>Click <i class="fas fa-sliders-h text-[8px] mx-0.5 text-white/40"></i> to create a strategy input, allowing users to adjust this value in TradingView</span>
                </button>
              </div>
            </template>
            
            <!-- Number Parameter - Input Mode (select from strategy params) -->
            <template v-else-if="(param.type === 'int' || param.type === 'float') && isParamInput(param.id)">
              <div class="space-y-1.5">
                <select
                  :value="getParamInputId(param.id)"
                  @change="updateParamInput(param.id, $event.target.value)"
                  class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1.5 text-sm text-white focus:outline-none focus:border-accent-500"
                >
                  <option value="" disabled>Select strategy input...</option>
                  <option v-for="inp in getCompatibleInputsForParam(param.type)" :key="inp.id" :value="inp.id">
                    {{ inp._varName || inp.name }} ({{ inp.type }}, default: {{ inp.default }})
                  </option>
                </select>
                <div class="text-[11px] text-white/25">
                  <i class="fas fa-info-circle mr-1"></i>
                  Users can adjust this input value in TradingView
                </div>
              </div>
            </template>
            
            <!-- Number Parameter - Variable Mode -->
            <template v-else-if="(param.type === 'int' || param.type === 'float') && isParamVariable(param.id)">
              <select
                :value="getParamVariableId(param.id)"
                @change="updateParamVariable(param.id, $event.target.value)"
                class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1.5 text-sm text-white focus:outline-none focus:border-accent-500"
              >
                <option value="" disabled>Select variable...</option>
                <option v-for="v in variables" :key="v.id" :value="v.id">
                  {{ v.name }}
                </option>
              </select>
              <div v-if="getParamVariableId(param.id)" class="mt-1 text-[11px] text-white/25">
                <i class="fas fa-info-circle mr-1"></i>
                Using a variable enables nested function composition
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Price Configuration -->
      <div v-else-if="modelValue.type === 'price'" class="space-y-3">
        <div>
          <label class="block text-xs text-dark-400 mb-1">Select price source</label>
          <select
            :value="modelValue.source"
            @change="changePriceSource($event.target.value)"
            class="w-full bg-dark-700 border border-dark-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
          >
            <option v-for="src in priceSources" :key="src.id" :value="src.id">
              {{ src.label }}
            </option>
          </select>
        </div>
        
        <!-- Preview -->
        <div class="bg-dark-900 rounded p-2">
          <div class="text-xs text-dark-400 mb-1">PineScript</div>
          <code class="text-blue-400 text-sm">{{ getPriceSource(modelValue.source)?.pinescript }}</code>
        </div>
      </div>

      <!-- Variable Configuration -->
      <div v-else-if="modelValue.type === 'variable'" class="space-y-3">
        <div>
          <label class="block text-xs text-dark-400 mb-1">Select variable</label>
          <select
            :value="modelValue.variableId"
            @change="changeVariable($event.target.value)"
            class="w-full bg-dark-700 border border-dark-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
          >
            <option v-for="v in variables" :key="v.id" :value="v.id">
              {{ v.name }}
            </option>
          </select>
        </div>
        
        <!-- Variable Info -->
        <div v-if="selectedVariable" class="bg-dark-900 rounded p-2 text-xs">
          <div class="text-dark-400 mb-1">Variable definition</div>
          <div class="font-mono">
            <span class="text-purple-400">{{ selectedVariable.name }}</span>
            <span class="text-dark-500"> = </span>
            <span class="text-amber-400">{{ getIndicator(selectedVariable.indicator)?.label }}</span>
            <span class="text-dark-400">(...)</span>
          </div>
        </div>
      </div>

      <!-- Constant Configuration -->
      <div v-else-if="modelValue.type === 'constant'" class="space-y-3">
        <!-- Quick-create input form for constant -->
        <div v-if="quickCreateConstant" class="space-y-2 bg-dark-900 rounded-lg p-2.5 border border-accent-500/30">
          <div class="flex items-center justify-between">
            <span class="text-xs text-accent-400 font-medium">
              <i class="fas fa-sliders-h mr-1"></i>Create adjustable input
            </span>
            <button @click="quickCreateConstant = false" class="text-dark-400 hover:text-white text-xs">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div class="col-span-2">
              <label class="block text-xs text-dark-500 mb-0.5">Name <span class="text-white/20">(letters, digits, underscores)</span></label>
              <input
                :value="constantInputForm.name"
                @input="constantInputForm.name = $event.target.value.replace(/[^a-zA-Z0-9_]/g, '')"
                type="text"
                class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500 font-mono"
                placeholder="threshold"
              />
            </div>
            <div>
              <label class="block text-xs text-dark-500 mb-0.5">Default</label>
              <input
                v-model.number="constantInputForm.default"
                type="number"
                step="any"
                class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
              />
            </div>
            <div>
              <label class="block text-xs text-dark-500 mb-0.5">Type</label>
              <select
                v-model="constantInputForm.type"
                class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
              >
                <option value="int">Integer</option>
                <option value="float">Float</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-dark-500 mb-0.5">Min</label>
              <input
                v-model.number="constantInputForm.min"
                type="number"
                step="any"
                placeholder="None"
                class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
              />
            </div>
            <div>
              <label class="block text-xs text-dark-500 mb-0.5">Max</label>
              <input
                v-model.number="constantInputForm.max"
                type="number"
                step="any"
                placeholder="None"
                class="w-full bg-dark-700 border border-dark-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent-500"
              />
            </div>
          </div>
          <div class="flex items-center justify-end pt-1">
            <button
              @click="confirmConstantInput"
              class="px-3 py-1 bg-accent-600 hover:bg-accent-500 text-white text-xs rounded transition-colors"
            >
              <i class="fas fa-check mr-1"></i>Create &amp; replace
            </button>
          </div>
        </div>
        
        <!-- Normal constant input -->
        <div v-else>
          <label class="block text-xs text-dark-400 mb-1">Enter value</label>
          <div class="flex items-center gap-2">
            <input
              type="number"
              :value="modelValue.value"
              @input="changeConstant(parseFloat($event.target.value))"
              step="any"
              class="flex-1 bg-dark-700 border border-dark-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
              placeholder="Enter value..."
              autofocus
            />
            <button
              @click="openConstantInput"
              class="px-2 py-2 bg-dark-600 hover:bg-dark-500 text-dark-400 hover:text-white rounded text-xs transition-colors"
              title="Create adjustable input (TradingView input)"
            >
              <i class="fas fa-sliders-h"></i>
            </button>
          </div>
        </div>
        
        <div class="text-xs text-dark-500">
          <i class="fas fa-info-circle mr-1"></i>
          Common values: 30 (RSI oversold), 70 (RSI overbought), 0 (MACD zero line)
        </div>
        
        <button
          v-if="!quickCreateConstant"
          @click="openConstantInput"
          class="w-full text-left text-[11px] text-white/25 hover:text-indigo-400/70 transition-colors flex items-center gap-1.5 py-0.5"
        >
          <i class="fas fa-wand-magic-sparkles text-[9px]"></i>
          <span>Click <i class="fas fa-sliders-h text-[8px] mx-0.5 text-white/40"></i> to create a strategy input, allowing users to adjust this constant in TradingView</span>
        </button>
      </div>

      <!-- Input Reference Configuration (select from existing inputs) -->
      <div v-else-if="modelValue.type === 'input'" class="space-y-3">
        <div>
          <label class="block text-xs text-dark-400 mb-1">Select strategy input</label>
          <select
            :value="modelValue.inputId"
            @change="selectInput($event.target.value)"
            class="w-full bg-dark-700 border border-dark-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-500"
          >
            <option v-for="inp in compatibleInputs" :key="inp.id" :value="inp.id">
              {{ inp._varName || inp.name }} ({{ inp.type }}, default: {{ inp.default }})
            </option>
          </select>
        </div>
        
        <!-- Current linked input display -->
        <div class="flex items-center gap-2">
          <span class="flex-1 px-3 py-2 rounded-lg text-sm font-mono text-teal-300 flex items-center gap-1.5" style="background: rgba(20,184,166,0.08); border: 1px solid rgba(20,184,166,0.15);">
            <i class="fas fa-sliders-h text-xs"></i>
            {{ modelValue.inputName || 'Input' }}
          </span>
          <button
            @click="changeConstant(modelValue.value ?? 0)"
            class="px-2 py-2 bg-dark-600 hover:bg-dark-500 text-dark-400 hover:text-red-400 rounded text-xs transition-colors"
            title="Unlink and revert to constant"
          >
            <i class="fas fa-unlink"></i>
          </button>
        </div>
        
        <div class="text-xs text-white/30">
          <i class="fas fa-info-circle mr-1"></i>
          Linked to a strategy input. Users can adjust this value in TradingView.
        </div>
      </div>
    </div>

    <!-- Overlay to close edit panel -->
    <div 
      v-if="isEditing" 
      class="fixed inset-0 z-[9998]" 
      @click="stopEditing"
    ></div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, reactive } from 'vue'
import ValueDisplay from './ValueDisplay.vue'
import {
  Indicators,
  IndicatorList,
  IndicatorCategories,
  PriceSources,
  getIndicator,
  getPriceSource,
  isMultiOutput,
  getIndicatorOutputs,
  getDefaultOutputIndex,
} from '../../utils/condition-types.js'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
  variables: {
    type: Array,
    default: () => [],
  },
  inputs: {
    type: Array,
    default: () => [],
  },
  allowConstant: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue', 'create-input'])

// Refs
const selectorRef = ref(null)
const triggerRef = ref(null)

// Quick-create input form state
const quickCreateParam = ref(null)
const quickCreateForm = ref({ name: '', default: 14, min: null, max: null })

// Quick-create for constant operand
const quickCreateConstant = ref(false)
const constantInputForm = ref({ name: 'threshold', type: 'float', default: 0, min: null, max: null })

/**
 * Generate a unique name that doesn't conflict with existing inputs or variables.
 */
function uniqueName(baseName) {
  const existingNames = new Set([
    ...props.inputs.map(i => i._varName || toCamelCase(i.name)),
    ...props.inputs.map(i => i.name),
    ...props.variables.map(v => v.name),
  ])
  if (!existingNames.has(baseName)) return baseName
  for (let i = 2; i < 100; i++) {
    const candidate = `${baseName}${i}`
    if (!existingNames.has(candidate)) return candidate
  }
  return baseName + '_' + Date.now().toString(36).slice(-3)
}

function openConstantInput() {
  constantInputForm.value = {
    name: uniqueName('threshold'),
    type: Number.isInteger(props.modelValue.value) ? 'int' : 'float',
    default: props.modelValue.value ?? 0,
    min: null,
    max: null,
  }
  quickCreateConstant.value = true
  nextTick(() => repositionPanel())
}

function confirmConstantInput() {
  const f = constantInputForm.value
  const varName = toCamelCase(f.name || 'threshold')
  const inputConfig = {
    id: `input_${Date.now()}`,
    name: f.name || 'threshold',
    type: f.type,
    default: f.default,
    min: (f.min !== null && f.min !== undefined && f.min !== '') ? f.min : undefined,
    max: (f.max !== null && f.max !== undefined && f.max !== '') ? f.max : undefined,
    _varName: varName,  // Store the exact PineScript variable name
  }
  
  // Create the input in the strategy's inputs list
  emit('create-input', inputConfig)
  
  // Replace the constant operand with an input reference
  emit('update:modelValue', {
    type: 'input',
    inputId: inputConfig.id,
    inputName: varName,
    value: f.default,
  })
  
  quickCreateConstant.value = false
}

function openQuickCreate(param) {
  const currentValue = getParamConstantValue(param.id, param.default)
  // Generate a unique name based on param label
  const baseName = toCamelCase(param.label || 'param')
  quickCreateForm.value = {
    name: uniqueName(baseName),
    default: currentValue,
    min: param.min ?? null,
    max: param.max ?? null,
  }
  quickCreateParam.value = param.id
  // Reposition panel after form expands
  nextTick(() => repositionPanel())
}

function quickCreatePreview(param) {
  const f = quickCreateForm.value
  const name = toCamelCase(f.name || param.label)
  const type = param.type === 'float' ? 'input.float' : 'input.int'
  let code = `${name} = ${type}(${f.default}, "${f.name || param.label}"`
  if (f.min !== null && f.min !== undefined && f.min !== '') code += `, minval=${f.min}`
  if (f.max !== null && f.max !== undefined && f.max !== '') code += `, maxval=${f.max}`
  return code + ')'
}

/**
 * Convert a display name to a valid PineScript variable name.
 * PineScript identifiers: [a-zA-Z_][a-zA-Z0-9_]*
 * Strips non-ASCII chars and ensures the result is valid.
 */
function toCamelCase(str) {
  // Extract only ASCII letters, digits, spaces, underscores
  const ascii = str.replace(/[^a-zA-Z0-9_\s]/g, '').trim()
  
  if (ascii) {
    // camelCase the ASCII parts
    const result = ascii
      .split(/[\s_]+/)
      .filter(Boolean)
      .map((word, index) => {
        if (index === 0) return word.toLowerCase()
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
      })
      .join('')
    
    // Ensure starts with letter or underscore
    if (/^[a-zA-Z_]/.test(result)) return result
    return '_' + result
  }
  
  // No ASCII content -- generate a prefix + timestamp
  return 'param_' + Date.now().toString(36).slice(-4)
}

function confirmQuickCreate(param) {
  const f = quickCreateForm.value
  const varName = toCamelCase(f.name || param.label)
  const inputConfig = {
    id: `input_${Date.now()}`,
    name: f.name || param.label,
    type: param.type,
    default: f.default,
    min: (f.min !== null && f.min !== undefined && f.min !== '') ? f.min : undefined,
    max: (f.max !== null && f.max !== undefined && f.max !== '') ? f.max : undefined,
    _varName: varName,  // Store the exact PineScript variable name
    _linkedParamId: param.id,
  }
  
  emit('create-input', inputConfig)
  
  // Auto-link: update the param to reference this input by its PineScript variable name
  updateParam(param.id, { type: 'input', inputId: inputConfig.id, inputName: varName })
  
  quickCreateParam.value = null
}

// Edit mode state
const isEditing = ref(false)
const panelPosition = reactive({ top: 0, left: 0 })

const editPanelRef = ref(null)

const panelStyle = computed(() => {
  const viewportHeight = typeof window !== 'undefined' ? window.innerHeight : 800
  const top = panelPosition.top
  const maxH = Math.max(200, viewportHeight - top - 12)
  return {
    top: `${top}px`,
    left: `${panelPosition.left}px`,
    maxHeight: `${maxH}px`,
  }
})

function repositionPanel() {
  if (!triggerRef.value) return
  
  const rect = triggerRef.value.getBoundingClientRect()
  const viewportHeight = window.innerHeight
  const viewportWidth = window.innerWidth
  const isMobile = viewportWidth < 640
  const panelWidth = isMobile ? viewportWidth - 16 : 320
  
  // Measure actual panel height if it exists
  const panelEl = editPanelRef.value
  const panelHeight = panelEl ? panelEl.scrollHeight : 400
  
  // Mobile: center horizontally, position below or above
  let top = rect.bottom + 4
  let left = isMobile ? 8 : rect.left
  
  // If panel would go below viewport, show above trigger
  if (top + panelHeight > viewportHeight) {
    const aboveTop = rect.top - panelHeight - 4
    if (aboveTop >= 8) {
      top = aboveTop
    } else {
      top = Math.max(8, viewportHeight - panelHeight - 12)
    }
  }
  
  // Ensure panel doesn't go off right edge
  if (!isMobile && left + panelWidth > viewportWidth) {
    left = viewportWidth - panelWidth - 8
  }
  
  // Ensure panel doesn't go off left edge
  if (left < 8) {
    left = 8
  }
  
  panelPosition.top = top
  panelPosition.left = left
}

function startEditing() {
  repositionPanel()
  isEditing.value = true
  // Reposition after render to account for actual panel size
  nextTick(() => repositionPanel())
}

function stopEditing() {
  isEditing.value = false
}

const indicatorCategories = IndicatorCategories
const priceSources = PriceSources

// Filter inputs to only show number types (int/float) for operand usage
// Boolean inputs can't be used as numeric operands
const compatibleInputs = computed(() => {
  return props.inputs.filter(inp => inp.type === 'int' || inp.type === 'float')
})

const currentIndicator = computed(() => {
  if (props.modelValue.type !== 'indicator') return null
  return getIndicator(props.modelValue.indicator)
})

const currentIndicatorOutputs = computed(() => {
  if (!currentIndicator.value) return []
  return currentIndicator.value.outputs || []
})

const selectedVariable = computed(() => {
  if (props.modelValue.type !== 'variable') return null
  return props.variables.find(v => v.id === props.modelValue.variableId)
})

function getIndicatorsByCategory(categoryId) {
  return IndicatorList.filter(ind => ind.category === categoryId)
}

function parseNumber(value, type) {
  const num = type === 'float' ? parseFloat(value) : parseInt(value, 10)
  return isNaN(num) ? 0 : num
}

// Helper functions for param value types
function isParamVariable(paramId) {
  const paramValue = props.modelValue.params?.[paramId]
  return paramValue && typeof paramValue === 'object' && (paramValue.type === 'variable' || paramValue.type === 'input')
}

function isParamInput(paramId) {
  const paramValue = props.modelValue.params?.[paramId]
  return paramValue && typeof paramValue === 'object' && paramValue.type === 'input'
}

function getParamInputName(paramId) {
  const paramValue = props.modelValue.params?.[paramId]
  if (paramValue && typeof paramValue === 'object' && paramValue.type === 'input') {
    return paramValue.inputName || paramValue.inputId || ''
  }
  return ''
}

function getParamConstantValue(paramId, defaultValue) {
  const paramValue = props.modelValue.params?.[paramId]
  if (paramValue === undefined || paramValue === null) return defaultValue
  if (typeof paramValue === 'object') return defaultValue
  return paramValue
}

function getParamSourceValue(paramId, defaultValue) {
  const paramValue = props.modelValue.params?.[paramId]
  if (paramValue === undefined || paramValue === null) return defaultValue
  if (typeof paramValue === 'object') return defaultValue
  return paramValue
}

function getParamVariableId(paramId) {
  const paramValue = props.modelValue.params?.[paramId]
  if (paramValue && typeof paramValue === 'object' && paramValue.type === 'variable') {
    return paramValue.variableId
  }
  return ''
}

function getCompatibleInputsForParam(paramType) {
  // For int params, show int inputs; for float params, show int and float inputs
  if (paramType === 'int') {
    return props.inputs.filter(i => i.type === 'int')
  }
  if (paramType === 'float') {
    return props.inputs.filter(i => i.type === 'int' || i.type === 'float')
  }
  return []
}

function getParamInputId(paramId) {
  const paramValue = props.modelValue.params?.[paramId]
  if (paramValue && typeof paramValue === 'object' && paramValue.type === 'input') {
    return paramValue.inputId || ''
  }
  return ''
}

function updateParamInput(paramId, inputId) {
  const inp = props.inputs.find(i => i.id === inputId)
  if (!inp) return
  const varName = inp._varName || toCamelCase(inp.name)
  updateParam(paramId, { type: 'input', inputId: inp.id, inputName: varName })
}

function setParamType(paramId, type, param) {
  if (type === 'constant' || type === 'price') {
    // Switch to constant/price - use default value
    updateParam(paramId, param.default)
  } else if (type === 'variable') {
    // Switch to variable reference
    updateParam(paramId, { 
      type: 'variable', 
      variableId: props.variables[0]?.id || '' 
    })
  } else if (type === 'input') {
    // Switch to input reference - pick first compatible input
    const compatible = getCompatibleInputsForParam(param.type)
    if (compatible.length > 0) {
      const inp = compatible[0]
      const varName = inp._varName || toCamelCase(inp.name)
      updateParam(paramId, { type: 'input', inputId: inp.id, inputName: varName })
    }
  }
}

function updateParamVariable(paramId, variableId) {
  updateParam(paramId, { type: 'variable', variableId })
}

function getParamColor(paramType) {
  switch (paramType) {
    case 'source':
      return 'text-blue-400'
    case 'int':
    case 'float':
      return 'text-cyan-400'
    default:
      return 'text-dark-300'
  }
}

function changeType(newType) {
  let newValue = { type: newType }
  
  switch (newType) {
    case 'indicator':
      newValue = {
        type: 'indicator',
        indicator: 'rsi',
        params: { source: 'close', period: 14 },
      }
      break
    case 'price':
      newValue = {
        type: 'price',
        source: 'close',
      }
      break
    case 'variable':
      newValue = {
        type: 'variable',
        variableId: props.variables[0]?.id || '',
      }
      break
    case 'constant':
      newValue = {
        type: 'constant',
        value: 0,
      }
      break
    case 'input': {
      const first = compatibleInputs.value[0]
      if (first) {
        const varName = first._varName || toCamelCase(first.name)
        newValue = {
          type: 'input',
          inputId: first.id,
          inputName: varName,
          value: first.default,
        }
      }
      break
    }
  }
  
  emit('update:modelValue', newValue)
}

function changeIndicator(indicatorId) {
  const indicator = getIndicator(indicatorId)
  if (!indicator) return
  
  // Build default params
  const params = {}
  indicator.params.forEach(p => {
    params[p.id] = p.default
  })
  
  const newValue = {
    type: 'indicator',
    indicator: indicatorId,
    params,
  }
  
  // Set default output index for multi-output indicators
  if (isMultiOutput(indicatorId)) {
    newValue.outputIndex = getDefaultOutputIndex(indicatorId)
  }
  
  emit('update:modelValue', newValue)
}

function changeOutputIndex(index) {
  emit('update:modelValue', {
    ...props.modelValue,
    outputIndex: index,
  })
}

function updateParam(paramId, value) {
  emit('update:modelValue', {
    ...props.modelValue,
    params: {
      ...props.modelValue.params,
      [paramId]: value,
    },
  })
}

function changePriceSource(source) {
  emit('update:modelValue', {
    type: 'price',
    source,
  })
}

function changeVariable(variableId) {
  emit('update:modelValue', {
    type: 'variable',
    variableId,
  })
}

function selectInput(inputId) {
  const inp = props.inputs.find(i => i.id === inputId)
  if (!inp) return
  const varName = inp._varName || toCamelCase(inp.name)
  emit('update:modelValue', {
    type: 'input',
    inputId: inp.id,
    inputName: varName,
    value: inp.default,
  })
}

function changeConstant(value) {
  emit('update:modelValue', {
    type: 'constant',
    value: isNaN(value) ? 0 : value,
  })
}
</script>

<style scoped>
.operand-selector {
  display: inline-flex;
  position: relative;
}


.edit-panel {
  position: fixed;
  z-index: 9999;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.value-display-wrapper {
  padding: 2px;
}

/* Hide number input spinners */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

/* Scrollbar styling for edit panel */
.edit-panel::-webkit-scrollbar {
  width: 6px;
}

.edit-panel::-webkit-scrollbar-track {
  background: #1e293b;
  border-radius: 3px;
}

.edit-panel::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 3px;
}

.edit-panel::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
</style>
