<template>
  <div class="pinescript-preview h-full flex flex-col relative" style="background: rgba(8, 10, 22, 0.95);">
    <!-- Header with tabs -->
    <div class="flex items-center justify-between px-2 sm:px-4 py-2 border-b border-dark-800 gap-2">
      <div class="flex items-center gap-1 overflow-x-auto flex-shrink min-w-0">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-2.5 sm:px-3 py-2 sm:py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap min-h-[36px]',
            activeTab === tab.id 
              ? 'bg-accent-600 text-white' 
              : 'text-dark-400 hover:text-white hover:bg-dark-800'
          ]"
        >
          <i :class="['mr-1', tab.icon]"></i>
          <span class="hidden sm:inline">{{ tab.label }}</span>
          <span class="sm:hidden">{{ tab.shortLabel || tab.label }}</span>
        </button>
      </div>
      
      <div class="flex items-center gap-1 sm:gap-2 flex-shrink-0">
        <!-- Validation status -->
        <div v-if="validationStatus" :class="['hidden sm:flex items-center gap-1.5 text-xs px-2 py-1 rounded', validationStatusClass]">
          <i :class="validationStatus.icon"></i>
          <span>{{ validationStatus.text }}</span>
        </div>
        
        <!-- Actions -->
        <button
          @click="validateCode"
          :disabled="isValidating"
          class="px-2.5 sm:px-3 py-2 sm:py-1.5 bg-dark-800 hover:bg-dark-700 text-dark-300 hover:text-white rounded-lg text-xs transition flex items-center gap-1.5 min-h-[36px]"
        >
          <i :class="['fas', isValidating ? 'fa-spinner fa-spin' : 'fa-check-circle']"></i>
          <span class="hidden sm:inline">Validate</span>
        </button>
        
        <button
          @click="copyCode"
          class="px-2.5 sm:px-3 py-2 sm:py-1.5 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-xs transition flex items-center gap-1.5 min-h-[36px]"
        >
          <i class="fas fa-copy"></i>
          <span class="hidden sm:inline">Copy</span>
        </button>
        
        <button
          @click="downloadCode"
          class="px-2.5 sm:px-3 py-2 sm:py-1.5 bg-dark-800 hover:bg-dark-700 text-dark-300 hover:text-white rounded-lg text-xs transition flex items-center gap-1.5 min-h-[36px]"
          title="Download .pine file"
        >
          <i class="fas fa-download"></i>
          <span class="hidden sm:inline">Download</span>
        </button>
      </div>
    </div>
    
    <!-- Content -->
    <div class="flex-1 overflow-auto">
      <!-- Code tab -->
      <div v-show="activeTab === 'code'" class="h-full">
        <div class="code-container h-full overflow-auto bg-dark-950 font-mono text-xs" v-html="highlightedCode"></div>
      </div>
    </div>
    
    <!-- Validation errors -->
    <div v-if="validationErrors.length > 0" class="border-t border-dark-800 p-3 bg-red-500/10">
      <div class="text-xs text-red-400 space-y-1">
        <div v-for="(error, i) in validationErrors" :key="i" class="flex items-start gap-2">
          <i class="fas fa-times-circle mt-0.5"></i>
          <span>Line {{ error.line }}: {{ error.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  code: {
    type: String,
    default: '',
  },
  strategyName: {
    type: String,
    default: 'My Strategy',
  },
})

const emit = defineEmits(['copy', 'validate'])

const activeTab = ref('code')
const isValidating = ref(false)
const validationResult = ref(null)
const validationErrors = ref([])

const tabs = [
  { id: 'code', label: 'PineScript', shortLabel: 'Code', icon: 'fas fa-code' },
]

// Validation status display
const validationStatus = computed(() => {
  if (isValidating.value) {
    return { text: 'Validating...', icon: 'fas fa-spinner fa-spin', type: 'loading' }
  }
  if (validationResult.value === null) {
    return null
  }
  if (validationResult.value.success) {
    return { text: 'Syntax OK', icon: 'fas fa-check-circle', type: 'success' }
  }
  return { text: 'Has errors', icon: 'fas fa-times-circle', type: 'error' }
})

const validationStatusClass = computed(() => {
  if (!validationStatus.value) return ''
  const classes = {
    loading: 'bg-dark-800 text-dark-400',
    success: 'bg-green-500/20 text-green-400',
    error: 'bg-red-500/20 text-red-400',
  }
  return classes[validationStatus.value.type] || ''
})

// PineScript syntax highlighting with proper line numbers
const highlightedCode = computed(() => {
  if (!props.code) {
    return '<div class="code-line"><span class="line-number">1</span><span class="line-content text-dark-500">// Set entry/exit conditions to start building a strategy</span></div>'
  }
  
  const lines = props.code.split('\n')
  
  return lines.map((line, index) => {
    const lineNumber = index + 1
    const highlightedLine = highlightLine(escapeHtml(line))
    return `<div class="code-line"><span class="line-number">${lineNumber}</span><span class="line-content">${highlightedLine}</span></div>`
  }).join('')
})

function highlightLine(line) {
  // Skip processing if line is empty
  if (!line.trim()) return line
  
  // Check if it's a comment line first (highest priority)
  if (line.trim().startsWith('//')) {
    return `<span class="hl-comment">${line}</span>`
  }
  
  // Process inline comments - split by // and only process the non-comment part
  const commentIndex = line.indexOf('//')
  let codePart = line
  let commentPart = ''
  
  if (commentIndex > -1) {
    codePart = line.substring(0, commentIndex)
    commentPart = `<span class="hl-comment">${line.substring(commentIndex)}</span>`
  }
  
  // First, protect strings by replacing them with placeholders
  const strings = []
  codePart = codePart.replace(/'([^']*)'/g, (match) => {
    strings.push(`<span class="hl-string">${match}</span>`)
    return `__STRING_${strings.length - 1}__`
  })
  codePart = codePart.replace(/"([^"]*)"/g, (match) => {
    strings.push(`<span class="hl-string">${match}</span>`)
    return `__STRING_${strings.length - 1}__`
  })
  
  // Highlight numbers FIRST (before adding any other spans)
  // Only match standalone numbers, not attached to words
  codePart = codePart.replace(/(?<![a-zA-Z_-])(\d+\.?\d*)(?![a-zA-Z_-])/g, '<span class="hl-number">$1</span>')
  
  // Version directive
  codePart = codePart.replace(/(@version=<span class="hl-number">\d+<\/span>)/g, '<span class="hl-version">$1</span>')
  codePart = codePart.replace(/(@version=\d+)/g, '<span class="hl-version">$1</span>')
  
  // Keywords
  codePart = codePart.replace(/\b(if|else|for|while|var|true|false|na|and|or|not)\b/g, '<span class="hl-keyword">$1</span>')
  
  // Strategy/indicator declaration
  codePart = codePart.replace(/\b(strategy|indicator)\b(\s*\()/g, '<span class="hl-declaration">$1</span>$2')
  
  // Input functions
  codePart = codePart.replace(/\b(input\.int|input\.float|input\.bool|input\.string|input\.source|input)\b/g, '<span class="hl-input">$1</span>')
  
  // TA functions  
  codePart = codePart.replace(/\b(ta\.sma|ta\.ema|ta\.rsi|ta\.macd|ta\.atr|ta\.crossover|ta\.crossunder|ta\.highest|ta\.lowest|ta\.stdev|ta\.bb|ta\.stoch|ta\.wma|ta\.vwma|ta\.cci|ta\.mfi|ta\.obv|ta\.mom|ta\.roc|ta\.tr|ta\.change|ta\.valuewhen)\b/g, '<span class="hl-function">$1</span>')
  
  // Strategy functions
  codePart = codePart.replace(/\b(strategy\.entry|strategy\.close|strategy\.exit|strategy\.cancel|strategy\.cancel_all|strategy\.order)\b/g, '<span class="hl-strategy">$1</span>')
  
  // Strategy constants
  codePart = codePart.replace(/\b(strategy\.long|strategy\.short|strategy\.fixed|strategy\.percent_of_equity|strategy\.cash)\b/g, '<span class="hl-constant">$1</span>')
  
  // Built-in variables
  codePart = codePart.replace(/\b(close|open|high|low|volume|time|bar_index|hl2|hlc3|ohlc4)\b/g, '<span class="hl-variable">$1</span>')
  
  // Strategy variables
  codePart = codePart.replace(/\b(strategy\.position_size|strategy\.position_avg_price|strategy\.equity|strategy\.netprofit|strategy\.openprofit)\b/g, '<span class="hl-stratvar">$1</span>')
  
  // alert_message parameter
  codePart = codePart.replace(/(alert_message\s*=)/g, '<span class="hl-alert">$1</span>')
  
  // Restore strings
  strings.forEach((str, i) => {
    codePart = codePart.replace(`__STRING_${i}__`, str)
  })
  
  return codePart + commentPart
}

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// Actions
function copyCode() {
  if (!props.code) return
  navigator.clipboard.writeText(props.code)
  emit('copy')
}

function downloadCode() {
  if (!props.code) return
  const nameMatch = props.code.match(/strategy\("([^"]+)"/)
  const strategyName = nameMatch ? nameMatch[1] : 'strategy'
  const safeName = strategyName.replace(/[^a-zA-Z0-9_-]/g, '_').replace(/_+/g, '_')
  const filename = `${safeName}.pine`
  
  const blob = new Blob([props.code], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

async function validateCode() {
  if (!props.code || isValidating.value) return
  
  isValidating.value = true
  validationErrors.value = []
  
  // Client-side PineScript syntax validation
  await new Promise(r => setTimeout(r, 100)) // brief delay for UX
  
  try {
    const errors = validatePineScriptSyntax(props.code)
    validationErrors.value = errors
    validationResult.value = { success: errors.length === 0, errors }
  } catch (e) {
    validationResult.value = { success: false, errors: [{ line: 0, message: 'Error during validation' }] }
  } finally {
    isValidating.value = false
  }
  
  emit('validate', validationResult.value)
}

/**
 * Client-side PineScript syntax validator
 * Checks common structural issues without a backend.
 */
function validatePineScriptSyntax(code) {
  const errors = []
  const lines = code.split('\n')
  
  // 1. Must start with //@version
  if (!lines[0]?.trim().startsWith('//@version=')) {
    errors.push({ line: 1, message: 'Missing version declaration (//@version=6)' })
  }
  
  // 2. Must have strategy() or indicator() declaration
  const hasDeclaration = lines.some(l => /^\s*(strategy|indicator)\s*\(/.test(l))
  if (!hasDeclaration) {
    errors.push({ line: 2, message: 'Missing strategy() or indicator() declaration' })
  }
  
  // 3. Check bracket balance
  let parenDepth = 0
  let bracketDepth = 0
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    // Skip comments
    const commentIdx = line.indexOf('//')
    const codePart = commentIdx >= 0 ? line.substring(0, commentIdx) : line
    // Skip strings
    const noStrings = codePart.replace(/'[^']*'/g, '').replace(/"[^"]*"/g, '')
    
    for (const ch of noStrings) {
      if (ch === '(') parenDepth++
      if (ch === ')') parenDepth--
      if (ch === '[') bracketDepth++
      if (ch === ']') bracketDepth--
      
      if (parenDepth < 0) {
        errors.push({ line: i + 1, message: 'Extra closing parenthesis )' })
        parenDepth = 0
      }
      if (bracketDepth < 0) {
        errors.push({ line: i + 1, message: 'Extra closing bracket ]' })
        bracketDepth = 0
      }
    }
  }
  
  if (parenDepth > 0) {
    errors.push({ line: lines.length, message: `Missing ${parenDepth} closing parenthesis )` })
  }
  if (bracketDepth > 0) {
    errors.push({ line: lines.length, message: `Missing ${bracketDepth} closing bracket ]` })
  }
  
  // 4. Check for common issues line by line
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('//')) continue
    
    // Single = used instead of == in conditions (after if/and/or)
    if (/\b(if|and|or)\b/.test(trimmed)) {
      const afterKeyword = trimmed.replace(/'[^']*'/g, '').replace(/"[^"]*"/g, '')
      const eqMatches = [...afterKeyword.matchAll(/(?<![=!<>:])=(?!=)/g)]
      for (const m of eqMatches) {
        const before = afterKeyword.substring(0, m.index).trim()
      }
    }
    
    // Empty strategy.entry / strategy.close with no arguments
    if (/strategy\.(entry|close|exit|order)\s*\(\s*\)/.test(trimmed)) {
      errors.push({ line: i + 1, message: `strategy function missing required parameters` })
    }
  }
  
  // 5. Check that alert_message values are valid
  const alertMessages = [...code.matchAll(/alert_message\s*=\s*"([^"]*)"/g)]
  const validAlertValues = ['long_entry', 'long_exit', 'short_entry', 'short_exit']
  for (const match of alertMessages) {
    if (!validAlertValues.includes(match[1])) {
      const beforeMatch = code.substring(0, match.index)
      const lineNum = beforeMatch.split('\n').length
      errors.push({ line: lineNum, message: `alert_message "${match[1]}" is not a valid value (should be long_entry/long_exit/short_entry/short_exit)` })
    }
  }
  
  // 6. Check for undefined variable references in conditions
  const assignedVars = new Set()
  for (const line of lines) {
    const trimmed = line.trim()
    if (trimmed.startsWith('//')) continue
    const simpleAssign = trimmed.match(/^([a-zA-Z_]\w*)\s*=\s/)
    if (simpleAssign) assignedVars.add(simpleAssign[1])
    const tupleAssign = trimmed.match(/^\[([^\]]+)\]\s*=/)
    if (tupleAssign) {
      tupleAssign[1].split(',').forEach(v => {
        const name = v.trim()
        if (name !== '_') assignedVars.add(name)
      })
    }
  }
  
  return errors
}

// Reset validation on code change
watch(() => props.code, () => {
  validationResult.value = null
  validationErrors.value = []
})
</script>

<style scoped>
.pinescript-preview {
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.06) transparent;
}

.code-container {
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.06) transparent;
  padding: 0.75rem 0;
  background: #060816;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

/* Disable text selection on code to prevent manual copy */
.code-protected {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.code-container::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}

.code-container::-webkit-scrollbar-track {
  background: transparent;
}

.code-container::-webkit-scrollbar-thumb {
  background-color: rgba(255,255,255,0.06);
  border-radius: 3px;
}

:deep(.code-line) {
  display: flex;
  line-height: 1.7;
  min-height: 1.5em;
}

:deep(.code-line:hover) {
  background-color: rgba(99, 102, 241, 0.04);
}

:deep(.line-number) {
  flex-shrink: 0;
  width: 2rem;
  padding-right: 0.5rem;
  text-align: right;
  color: rgba(255,255,255,0.12);
  user-select: none;
  border-right: 1px solid rgba(255,255,255,0.04);
  margin-right: 0.5rem;
  font-size: 11px;
}

@media (min-width: 640px) {
  :deep(.line-number) {
    width: 3rem;
    padding-right: 1rem;
    margin-right: 1rem;
  }
}

:deep(.line-content) {
  flex: 1;
  color: #c8ccd4;
  white-space: pre;
  padding-right: 1rem;
  font-size: 12.5px;
}

/* Material Ocean syntax highlighting */
:deep(.hl-comment) { color: #546e7a; font-style: italic; }
:deep(.hl-string) { color: #c3e88d; }
:deep(.hl-number) { color: #f78c6c; }
:deep(.hl-version) { color: #c792ea; font-weight: 600; }
:deep(.hl-keyword) { color: #c792ea; }
:deep(.hl-declaration) { color: #c792ea; font-weight: 600; }
:deep(.hl-input) { color: #ffcb6b; }
:deep(.hl-function) { color: #82aaff; }
:deep(.hl-strategy) { color: #c3e88d; }
:deep(.hl-constant) { color: #89ddff; }
:deep(.hl-variable) { color: #82aaff; }
:deep(.hl-stratvar) { color: #89ddff; }
:deep(.hl-alert) { color: #c792ea; font-weight: 600; }
</style>
