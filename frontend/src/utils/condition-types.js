/**
 * Condition Types and Data Model for Form-Based Strategy Builder
 * 
 * This module defines the data structures and helper functions for building
 * trading strategy conditions using AND/OR logic composition.
 */

// ============================================================================
// Operator Definitions
// ============================================================================

export const ComparisonOperators = {
  LT: { id: 'lt', label: '<', pinescript: '<' },
  GT: { id: 'gt', label: '>', pinescript: '>' },
  LTE: { id: 'lte', label: '≤', pinescript: '<=' },
  GTE: { id: 'gte', label: '≥', pinescript: '>=' },
  EQ: { id: 'eq', label: '=', pinescript: '==' },
  NEQ: { id: 'neq', label: '≠', pinescript: '!=' },
  CROSSOVER: { id: 'crossover', label: 'Crossover', pinescript: 'ta.crossover' },
  CROSSUNDER: { id: 'crossunder', label: 'Crossunder', pinescript: 'ta.crossunder' },
  CROSS: { id: 'cross', label: 'Cross', pinescript: 'ta.cross' },
}

export const OperatorList = Object.values(ComparisonOperators)

// ============================================================================
// Operand Types
// ============================================================================

export const OperandTypes = {
  INDICATOR: 'indicator',
  PRICE: 'price',
  VARIABLE: 'variable',
  CONSTANT: 'constant',
}

// ============================================================================
// Price Data Sources
// ============================================================================

export const PriceSources = [
  { id: 'close', label: 'Close', pinescript: 'close' },
  { id: 'open', label: 'Open', pinescript: 'open' },
  { id: 'high', label: 'High', pinescript: 'high' },
  { id: 'low', label: 'Low', pinescript: 'low' },
  { id: 'hl2', label: '(H+L)/2', pinescript: 'hl2' },
  { id: 'hlc3', label: '(H+L+C)/3', pinescript: 'hlc3' },
  { id: 'hlcc4', label: '(H+L+C+C)/4', pinescript: 'hlcc4' },
  { id: 'ohlc4', label: '(O+H+L+C)/4', pinescript: 'ohlc4' },
  { id: 'volume', label: 'Volume', pinescript: 'volume' },
]

// ============================================================================
// Built-in Indicators
// ============================================================================

export const Indicators = {
  // ── Trend Indicators ──────────────────────────────────────────────
  sma: {
    id: 'sma', label: 'SMA', category: 'trend', description: 'Simple Moving Average',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.sma(${params.source}, ${params.period})`,
  },
  ema: {
    id: 'ema', label: 'EMA', category: 'trend', description: 'Exponential Moving Average',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.ema(${params.source}, ${params.period})`,
  },
  wma: {
    id: 'wma', label: 'WMA', category: 'trend', description: 'Weighted Moving Average',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.wma(${params.source}, ${params.period})`,
  },
  vwma: {
    id: 'vwma', label: 'VWMA', category: 'trend', description: 'Volume Weighted Moving Average',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.vwma(${params.source}, ${params.period})`,
  },
  hma: {
    id: 'hma', label: 'HMA', category: 'trend', description: 'Hull Moving Average',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 9, min: 1 },
    ],
    pinescript: (params) => `ta.hma(${params.source}, ${params.period})`,
  },
  rma: {
    id: 'rma', label: 'RMA', category: 'trend', description: 'RSI Moving Average',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.rma(${params.source}, ${params.period})`,
  },
  alma: {
    id: 'alma', label: 'ALMA', category: 'trend', description: 'Arnaud Legoux Moving Average',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 9, min: 1 },
      { id: 'offset', label: 'Offset', type: 'float', default: 0.85, min: 0, max: 1 },
      { id: 'sigma', label: 'Sigma', type: 'float', default: 6.0, min: 0.1 },
    ],
    pinescript: (params) => `ta.alma(${params.source}, ${params.period}, ${params.offset}, ${params.sigma})`,
  },
  swma: {
    id: 'swma', label: 'SWMA', category: 'trend', description: 'Symmetric Weighted Moving Average (fixed 4-period)',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
    ],
    pinescript: (params) => `ta.swma(${params.source})`,
  },
  supertrend: {
    id: 'supertrend', label: 'SuperTrend', category: 'trend', description: 'SuperTrend Indicator (2 outputs)',
    params: [
      { id: 'factor', label: 'Factor', type: 'float', default: 3.0, min: 0.1 },
      { id: 'atrPeriod', label: 'ATR Period', type: 'int', default: 10, min: 1 },
    ],
    outputs: [
      { id: 'value', label: 'SuperTrend Value', default: true },
      { id: 'direction', label: 'Direction (1/-1)' },
    ],
    pinescript: (params, outputIndex = 0) => `ta.supertrend(${params.factor}, ${params.atrPeriod})[${outputIndex}]`,
    pineCall: (params) => `ta.supertrend(${params.factor}, ${params.atrPeriod})`,
  },

  // ── Momentum Indicators ───────────────────────────────────────────
  rsi: {
    id: 'rsi', label: 'RSI', category: 'momentum', description: 'Relative Strength Index',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.rsi(${params.source}, ${params.period})`,
  },
  macd: {
    id: 'macd', label: 'MACD', category: 'momentum', description: 'MACD Indicator (3 outputs)',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'fastPeriod', label: 'Fast Period', type: 'int', default: 12, min: 1 },
      { id: 'slowPeriod', label: 'Slow Period', type: 'int', default: 26, min: 1 },
      { id: 'signalPeriod', label: 'Signal Period', type: 'int', default: 9, min: 1 },
    ],
    outputs: [
      { id: 'macdLine', label: 'MACD Line', default: true },
      { id: 'signalLine', label: 'Signal Line' },
      { id: 'histogram', label: 'Histogram' },
    ],
    pinescript: (params, outputIndex = 0) => `ta.macd(${params.source}, ${params.fastPeriod}, ${params.slowPeriod}, ${params.signalPeriod})[${outputIndex}]`,
    pineCall: (params) => `ta.macd(${params.source}, ${params.fastPeriod}, ${params.slowPeriod}, ${params.signalPeriod})`,
  },
  stoch: {
    id: 'stoch', label: 'Stochastic', category: 'momentum', description: 'Stochastic Oscillator (2 outputs: %K, %D)',
    params: [
      { id: 'kPeriod', label: '%K Period', type: 'int', default: 14, min: 1 },
      { id: 'kSmooth', label: '%K Smoothing', type: 'int', default: 1, min: 1 },
      { id: 'dPeriod', label: '%D Period', type: 'int', default: 3, min: 1 },
    ],
    outputs: [
      { id: 'k', label: '%K', default: true },
      { id: 'd', label: '%D' },
    ],
    // %K = sma(stoch(close, high, low, kPeriod), kSmooth), %D = sma(%K, dPeriod)
    // For inline single-output references we generate a helper expression
    pinescript: (params, outputIndex = 0) => {
      const rawK = `ta.stoch(close, high, low, ${params.kPeriod})`
      const smoothedK = params.kSmooth > 1 ? `ta.sma(${rawK}, ${params.kSmooth})` : rawK
      if (outputIndex === 0) return smoothedK
      return `ta.sma(${smoothedK}, ${params.dPeriod})`
    },
    // For tuple destructuring in variable declarations, we generate a helper block
    // (Stochastic doesn't have native tuple return, so we don't use pineCall)
  },
  cci: {
    id: 'cci', label: 'CCI', category: 'momentum', description: 'Commodity Channel Index',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'hlc3' },
      { id: 'period', label: 'Period', type: 'int', default: 20, min: 1 },
    ],
    pinescript: (params) => `ta.cci(${params.source}, ${params.period})`,
  },
  mfi: {
    id: 'mfi', label: 'MFI', category: 'momentum', description: 'Money Flow Index',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'hlc3' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.mfi(${params.source}, ${params.period})`,
  },
  cmo: {
    id: 'cmo', label: 'CMO', category: 'momentum', description: 'Chande Momentum Oscillator',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.cmo(${params.source}, ${params.period})`,
  },
  roc: {
    id: 'roc', label: 'ROC', category: 'momentum', description: 'Rate of Change',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.roc(${params.source}, ${params.period})`,
  },
  tsi: {
    id: 'tsi', label: 'TSI', category: 'momentum', description: 'True Strength Index',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'shortPeriod', label: 'Short Period', type: 'int', default: 13, min: 1 },
      { id: 'longPeriod', label: 'Long Period', type: 'int', default: 25, min: 1 },
    ],
    pinescript: (params) => `ta.tsi(${params.source}, ${params.shortPeriod}, ${params.longPeriod})`,
  },
  mom: {
    id: 'mom', label: 'MOM', category: 'momentum', description: 'Momentum (Price Difference)',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 10, min: 1 },
    ],
    pinescript: (params) => `ta.mom(${params.source}, ${params.period})`,
  },
  wpr: {
    id: 'wpr', label: 'Williams %R', category: 'momentum', description: 'Williams %R Indicator',
    params: [
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.wpr(${params.period})`,
  },
  percentrank: {
    id: 'percentrank', label: 'PercentRank', category: 'momentum', description: 'Percent Rank',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 20, min: 1 },
    ],
    pinescript: (params) => `ta.percentrank(${params.source}, ${params.period})`,
  },

  // ── Volatility Indicators ─────────────────────────────────────────
  atr: {
    id: 'atr', label: 'ATR', category: 'volatility', description: 'Average True Range',
    params: [
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.atr(${params.period})`,
  },
  bb: {
    id: 'bb', label: 'BB', category: 'volatility', description: 'Bollinger Bands (3 outputs)',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 20, min: 1 },
      { id: 'mult', label: 'StdDev Multiplier', type: 'float', default: 2.0, min: 0.1 },
    ],
    outputs: [
      { id: 'middle', label: 'Middle Band', default: true },
      { id: 'upper', label: 'Upper Band' },
      { id: 'lower', label: 'Lower Band' },
    ],
    pinescript: (params, outputIndex = 0) => `ta.bb(${params.source}, ${params.period}, ${params.mult})[${outputIndex}]`,
    pineCall: (params) => `ta.bb(${params.source}, ${params.period}, ${params.mult})`,
  },
  bbw: {
    id: 'bbw', label: 'BBW', category: 'volatility', description: 'Bollinger Bands Width',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 20, min: 1 },
      { id: 'mult', label: 'StdDev Multiplier', type: 'float', default: 2.0, min: 0.1 },
    ],
    pinescript: (params) => `ta.bbw(${params.source}, ${params.period}, ${params.mult})`,
  },
  kc: {
    id: 'kc', label: 'KC', category: 'volatility', description: 'Keltner Channel (3 outputs)',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 20, min: 1 },
      { id: 'mult', label: 'ATR Multiplier', type: 'float', default: 1.5, min: 0.1 },
    ],
    outputs: [
      { id: 'middle', label: 'Middle Band', default: true },
      { id: 'upper', label: 'Upper Band' },
      { id: 'lower', label: 'Lower Band' },
    ],
    pinescript: (params, outputIndex = 0) => `ta.kc(${params.source}, ${params.period}, ${params.mult})[${outputIndex}]`,
    pineCall: (params) => `ta.kc(${params.source}, ${params.period}, ${params.mult})`,
  },
  kcw: {
    id: 'kcw', label: 'KCW', category: 'volatility', description: 'Keltner Channel Width',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 20, min: 1 },
      { id: 'mult', label: 'ATR Multiplier', type: 'float', default: 1.5, min: 0.1 },
    ],
    pinescript: (params) => `ta.kcw(${params.source}, ${params.period}, ${params.mult})`,
  },
  dmi: {
    id: 'dmi', label: 'DMI', category: 'volatility', description: 'Directional Movement Index (3 outputs)',
    params: [
      { id: 'diLength', label: 'DI Period', type: 'int', default: 14, min: 1 },
      { id: 'adxSmoothing', label: 'ADX Smoothing', type: 'int', default: 14, min: 1 },
    ],
    outputs: [
      { id: 'diPlus', label: '+DI', default: true },
      { id: 'diMinus', label: '-DI' },
      { id: 'adx', label: 'ADX' },
    ],
    pinescript: (params, outputIndex = 0) => `ta.dmi(${params.diLength}, ${params.adxSmoothing})[${outputIndex}]`,
    pineCall: (params) => `ta.dmi(${params.diLength}, ${params.adxSmoothing})`,
  },
  stdev: {
    id: 'stdev', label: 'StDev', category: 'volatility', description: 'Standard Deviation',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 20, min: 1 },
    ],
    pinescript: (params) => `ta.stdev(${params.source}, ${params.period})`,
  },
  sar: {
    id: 'sar', label: 'Parabolic SAR', category: 'volatility', description: 'Parabolic Stop and Reverse',
    params: [
      { id: 'start', label: 'Start', type: 'float', default: 0.02, min: 0.001 },
      { id: 'inc', label: 'Increment', type: 'float', default: 0.02, min: 0.001 },
      { id: 'max', label: 'Maximum', type: 'float', default: 0.2, min: 0.01 },
    ],
    pinescript: (params) => `ta.sar(${params.start}, ${params.inc}, ${params.max})`,
  },
  cog: {
    id: 'cog', label: 'COG', category: 'volatility', description: 'Center of Gravity',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 10, min: 1 },
    ],
    pinescript: (params) => `ta.cog(${params.source}, ${params.period})`,
  },

  // ── Volume Indicators ─────────────────────────────────────────────
  obv: {
    id: 'obv', label: 'OBV', category: 'volume', description: 'On Balance Volume',
    params: [],
    pinescript: () => `ta.obv`,
  },
  accdist: {
    id: 'accdist', label: 'A/D', category: 'volume', description: 'Accumulation/Distribution',
    params: [],
    pinescript: () => `ta.accdist`,
  },
  pvt: {
    id: 'pvt', label: 'PVT', category: 'volume', description: 'Price Volume Trend',
    params: [],
    pinescript: () => `ta.pvt`,
  },
  wad: {
    id: 'wad', label: 'WAD', category: 'volume', description: 'Williams Accumulation/Distribution',
    params: [],
    pinescript: () => `ta.wad`,
  },
  vwap: {
    id: 'vwap', label: 'VWAP', category: 'volume', description: 'Volume Weighted Average Price',
    params: [],
    pinescript: () => `ta.vwap`,
  },

  // ── Utility Indicators ────────────────────────────────────────────
  highest: {
    id: 'highest', label: 'Highest', category: 'utility', description: 'Highest Value',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'high' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.highest(${params.source}, ${params.period})`,
  },
  lowest: {
    id: 'lowest', label: 'Lowest', category: 'utility', description: 'Lowest Value',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'low' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.lowest(${params.source}, ${params.period})`,
  },
  change: {
    id: 'change', label: 'Change', category: 'utility', description: 'Price Change',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 1, min: 1 },
    ],
    pinescript: (params) => `ta.change(${params.source}, ${params.period})`,
  },
  median: {
    id: 'median', label: 'Median', category: 'utility', description: 'Median Value',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.median(${params.source}, ${params.period})`,
  },
  range: {
    id: 'range', label: 'Range', category: 'utility', description: 'Range (Highest - Lowest)',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
    ],
    pinescript: (params) => `ta.range(${params.source}, ${params.period})`,
  },
  linreg: {
    id: 'linreg', label: 'LinReg', category: 'utility', description: 'Linear Regression',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 14, min: 1 },
      { id: 'offset', label: 'Offset', type: 'int', default: 0, min: 0 },
    ],
    pinescript: (params) => `ta.linreg(${params.source}, ${params.period}, ${params.offset})`,
  },
  rising: {
    id: 'rising', label: 'Rising', category: 'utility', description: 'Rising (Boolean)',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 3, min: 1 },
    ],
    pinescript: (params) => `ta.rising(${params.source}, ${params.period})`,
  },
  falling: {
    id: 'falling', label: 'Falling', category: 'utility', description: 'Falling (Boolean)',
    params: [
      { id: 'source', label: 'Source', type: 'source', default: 'close' },
      { id: 'period', label: 'Period', type: 'int', default: 3, min: 1 },
    ],
    pinescript: (params) => `ta.falling(${params.source}, ${params.period})`,
  },
}

// Legacy aliases for backward compatibility with saved strategies
Indicators.macdSignal = {
  id: 'macdSignal',
  label: 'MACD Signal (legacy)',
  category: 'momentum',
  description: 'MACD Signal Line - merged into MACD',
  _legacyOf: 'macd',
  _legacyOutputIndex: 1,
  params: Indicators.macd.params,
  pinescript: (params) => Indicators.macd.pinescript(params, 1),
}
Indicators.bbUpper = {
  id: 'bbUpper',
  label: 'BB Upper (legacy)',
  category: 'volatility',
  description: 'Merged into BB',
  _legacyOf: 'bb',
  _legacyOutputIndex: 1,
  params: Indicators.bb.params,
  pinescript: (params) => Indicators.bb.pinescript(params, 1),
}
Indicators.bbMiddle = {
  id: 'bbMiddle',
  label: 'BB Middle (legacy)',
  category: 'volatility',
  description: 'Merged into BB',
  _legacyOf: 'bb',
  _legacyOutputIndex: 0,
  params: Indicators.bb.params,
  pinescript: (params) => Indicators.bb.pinescript(params, 0),
}
Indicators.bbLower = {
  id: 'bbLower',
  label: 'BB Lower (legacy)',
  category: 'volatility',
  description: 'Merged into BB',
  _legacyOf: 'bb',
  _legacyOutputIndex: 2,
  params: Indicators.bb.params,
  pinescript: (params) => Indicators.bb.pinescript(params, 2),
}

// Exclude legacy aliases from the main list shown in UI
export const IndicatorList = Object.values(Indicators).filter(ind => !ind._legacyOf)

export const IndicatorCategories = [
  { id: 'trend', label: 'Trend', icon: 'fa-chart-line' },
  { id: 'momentum', label: 'Momentum', icon: 'fa-tachometer-alt' },
  { id: 'volatility', label: 'Volatility', icon: 'fa-wave-square' },
  { id: 'volume', label: 'Volume', icon: 'fa-chart-bar' },
  { id: 'utility', label: 'Utility', icon: 'fa-tools' },
]

/**
 * Check if an indicator has multiple outputs
 */
export function isMultiOutput(indicatorId) {
  const indicator = Indicators[indicatorId]
  return indicator?.outputs && indicator.outputs.length > 1
}

/**
 * Get the output list for a multi-output indicator
 */
export function getIndicatorOutputs(indicatorId) {
  const indicator = Indicators[indicatorId]
  return indicator?.outputs || []
}

/**
 * Get the default output index for an indicator
 */
export function getDefaultOutputIndex(indicatorId) {
  const outputs = getIndicatorOutputs(indicatorId)
  const defaultOutput = outputs.findIndex(o => o.default)
  return defaultOutput >= 0 ? defaultOutput : 0
}

// ============================================================================
// Signal Types
// ============================================================================

export const SignalTypes = {
  LONG_ENTRY: { id: 'longEntry', label: 'Long Entry', color: 'green', action: 'long_entry' },
  LONG_EXIT: { id: 'longExit', label: 'Long Exit', color: 'red', action: 'long_exit' },
  SHORT_ENTRY: { id: 'shortEntry', label: 'Short Entry', color: 'red', action: 'short_entry' },
  SHORT_EXIT: { id: 'shortExit', label: 'Short Exit', color: 'green', action: 'short_exit' },
}

export const SignalList = Object.values(SignalTypes)

// ============================================================================
// Input Types for TradingView
// ============================================================================

export const InputTypes = {
  INT: { id: 'int', label: 'Integer', pinescript: 'input.int' },
  FLOAT: { id: 'float', label: 'Float', pinescript: 'input.float' },
  BOOL: { id: 'bool', label: 'Boolean', pinescript: 'input.bool' },
  STRING: { id: 'string', label: 'String', pinescript: 'input.string' },
  SOURCE: { id: 'source', label: 'Source', pinescript: 'input.source' },
}

// ============================================================================
// Factory Functions
// ============================================================================

/**
 * Create a new empty strategy
 */
export function createEmptyStrategy() {
  return {
    name: 'My Strategy',
    settings: {
      initialCapital: 10000,
      currency: 'USD',
      orderSize: 100,
      orderType: 'percent',  // 'contracts' | 'percent'
      pyramiding: 0,
      commission: 0,
      commissionType: 'percent',  // 'percent' | 'fixed'
      slippage: 0,
      calcOnEveryTick: false,
      processOrdersOnClose: false,
    },
    signals: {
      longEntry: createEmptySignal(),
      longExit: createEmptySignal(),
      shortEntry: createEmptySignal(),
      shortExit: createEmptySignal(),
    },
    variables: [],
    inputs: [],
  }
}

/**
 * Create an empty signal configuration
 */
export function createEmptySignal() {
  return {
    enabled: true,
    groups: [],
    // Take-profit / Stop-loss (only used for entry signals)
    exitSettings: {
      takeProfitEnabled: false,
      takeProfitMode: 'points',  // 'points' | 'percent'
      takeProfitValue: 100,
      stopLossEnabled: false,
      stopLossMode: 'points',    // 'points' | 'percent'
      stopLossValue: 50,
    },
  }
}

/**
 * Create a new condition group
 */
export function createConditionGroup() {
  return {
    id: `group_${Date.now()}`,
    conditions: [],
  }
}

/**
 * Create a new condition
 */
export function createCondition() {
  return {
    id: `cond_${Date.now()}`,
    left: {
      type: 'empty',
    },
    operator: 'lt',
    right: {
      type: 'empty',
    },
  }
}

/**
 * Create a new custom variable
 */
export function createVariable(type = 'indicator') {
  if (type === 'price') {
    return {
      id: `var_${Date.now()}`,
      name: 'myPrice',
      type: 'price',
      source: 'close',
    }
  }
  if (type === 'expression') {
    return {
      id: `var_${Date.now()}`,
      name: 'myExpr',
      type: 'expression',
      expression: createExprBinary('-',
        createExprLeaf('price', { source: 'close' }),
        createExprLeaf('price', { source: 'open' }),
      ),
    }
  }
  return {
    id: `var_${Date.now()}`,
    name: 'myVariable',
    type: 'indicator',
    indicator: 'sma',
    params: { source: 'close', period: 14 },
  }
}

// Math operators for derived expressions
export const MathOperators = [
  { id: '+', label: '+', description: 'Add' },
  { id: '-', label: '-', description: 'Subtract' },
  { id: '*', label: '×', description: 'Multiply' },
  { id: '/', label: '÷', description: 'Divide' },
]

// ============================================================================
// Math Functions for Expression Builder
// ============================================================================

export const MathFunctions = [
  // 1-argument functions
  { id: 'abs',     label: 'abs',     argCount: 1, category: '1-arg', description: 'Absolute',       pinescript: (args) => `math.abs(${args[0]})` },
  { id: 'sqrt',    label: 'sqrt',    argCount: 1, category: '1-arg', description: 'Square Root',    pinescript: (args) => `math.sqrt(${args[0]})` },
  { id: 'log',     label: 'log',     argCount: 1, category: '1-arg', description: 'Natural Log',    pinescript: (args) => `math.log(${args[0]})` },
  { id: 'log10',   label: 'log10',   argCount: 1, category: '1-arg', description: 'Common Log',     pinescript: (args) => `math.log10(${args[0]})` },
  { id: 'ceil',    label: 'ceil',    argCount: 1, category: '1-arg', description: 'Ceiling',        pinescript: (args) => `math.ceil(${args[0]})` },
  { id: 'floor',   label: 'floor',   argCount: 1, category: '1-arg', description: 'Floor',          pinescript: (args) => `math.floor(${args[0]})` },
  { id: 'round',   label: 'round',   argCount: 1, category: '1-arg', description: 'Round',          pinescript: (args) => `math.round(${args[0]})` },
  { id: 'nz',      label: 'nz',      argCount: 1, category: '1-arg', description: 'NaN to 0',      pinescript: (args) => `nz(${args[0]})` },
  // 2-argument functions
  { id: 'max',     label: 'max',     argCount: 2, category: '2-arg', description: 'Maximum',        pinescript: (args) => `math.max(${args[0]}, ${args[1]})` },
  { id: 'min',     label: 'min',     argCount: 2, category: '2-arg', description: 'Minimum',        pinescript: (args) => `math.min(${args[0]}, ${args[1]})` },
  { id: 'pow',     label: 'pow',     argCount: 2, category: '2-arg', description: 'Power',          pinescript: (args) => `math.pow(${args[0]}, ${args[1]})` },
]

export function getMathFunction(id) {
  return MathFunctions.find(f => f.id === id) || null
}

// ============================================================================
// Expression Tree Node Factories
// ============================================================================

/**
 * Create a leaf expression node
 */
export function createExprLeaf(leafType = 'price', defaults = {}) {
  if (leafType === 'price') return { type: 'price', source: defaults.source || 'close' }
  if (leafType === 'variable') return { type: 'variable', variableId: defaults.variableId || '' }
  if (leafType === 'constant') return { type: 'constant', value: defaults.value ?? 0 }
  if (leafType === 'input') return { type: 'input', inputName: defaults.inputName || '' }
  return { type: 'price', source: 'close' }
}

/**
 * Create a binary expression node: left op right
 */
export function createExprBinary(operator = '-', left = null, right = null) {
  return {
    type: 'binary',
    operator,
    left: left || createExprLeaf('price', { source: 'close' }),
    right: right || createExprLeaf('price', { source: 'open' }),
  }
}

/**
 * Create a unary expression node (negate)
 */
export function createExprUnary(func = 'negate', operand = null) {
  return {
    type: 'unary',
    func,
    operand: operand || createExprLeaf('price', { source: 'close' }),
  }
}

/**
 * Create a function call expression node
 */
export function createExprFunc(name = 'abs', args = null) {
  const fnDef = getMathFunction(name)
  const argCount = fnDef?.argCount || 1
  const defaultArgs = args || Array.from({ length: argCount }, (_, i) =>
    createExprLeaf('price', { source: i === 0 ? 'close' : 'open' })
  )
  return { type: 'func', name, args: defaultArgs }
}

/**
 * Check if an expression node is a leaf (terminal) node
 */
export function isExprLeaf(node) {
  return node && ['price', 'variable', 'constant', 'input'].includes(node.type)
}

/**
 * Convert old flat expression format { left, operator, right }
 * to new tree format { type: 'binary', operator, left, right }.
 * Returns the node unchanged if already in new format.
 */
export function migrateExpression(expr) {
  if (!expr) return createExprBinary()
  // Already in new format
  if (expr.type === 'binary' || expr.type === 'unary' || expr.type === 'func') return expr
  // Old flat format: { left, operator, right }
  if (expr.left && expr.operator && expr.right) {
    return {
      type: 'binary',
      operator: expr.operator,
      left: expr.left,   // leaves are already compatible
      right: expr.right,
    }
  }
  return createExprBinary()
}

/**
 * Create a new strategy input
 */
export function createInput(type = 'int', name = 'myInput', defaultValue = 14) {
  return {
    id: `input_${Date.now()}`,
    name,
    type,
    default: defaultValue,
    min: type === 'int' || type === 'float' ? 1 : undefined,
    max: undefined,
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get indicator by ID
 */
export function getIndicator(id) {
  return Indicators[id] || null
}

/**
 * Get operator by ID
 */
export function getOperator(id) {
  return OperatorList.find(op => op.id === id) || null
}

/**
 * Get price source by ID
 */
export function getPriceSource(id) {
  return PriceSources.find(src => src.id === id) || null
}

/**
 * Check if operator is a crossover type (requires two series)
 */
export function isCrossOperator(operatorId) {
  return operatorId === 'crossover' || operatorId === 'crossunder' || operatorId === 'cross'
}

/**
 * Generate a unique ID
 */
export function generateId(prefix = 'id') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Deep clone an object
 */
export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj))
}

/**
 * Collect all names currently in use across variables and inputs.
 * @param {Array} variables - strategy.variables
 * @param {Array} inputs - strategy.inputs
 * @param {string|null} excludeId - optional ID to exclude (e.g. the item being renamed)
 * @returns {Set<string>} set of names in use
 */
export function collectAllNames(variables = [], inputs = [], excludeId = null) {
  const names = new Set()
  variables.forEach(v => {
    if (v.id !== excludeId && v.name) names.add(v.name)
  })
  inputs.forEach(i => {
    if (i.id !== excludeId && i.name) names.add(i.name)
  })
  return names
}

/**
 * Generate a unique name that doesn't conflict with any existing variable or input names.
 * @param {string} baseName - desired base name
 * @param {Set<string>} existingNames - set of names already in use
 * @returns {string} a unique name
 */
export function generateUniqueName(baseName, existingNames) {
  if (!existingNames.has(baseName)) return baseName
  for (let i = 2; i < 100; i++) {
    const candidate = `${baseName}${i}`
    if (!existingNames.has(candidate)) return candidate
  }
  return baseName + '_' + Date.now().toString(36).slice(-4)
}
