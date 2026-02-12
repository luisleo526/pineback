"""
Code generator — walks the AST and emits a vectorized Python ``_compute``
function, then ``exec()``s it to produce a ``TransformedStrategy``.

Key translations:
  - PineScript price builtins  -> prefixed DataFrame columns (``_close``, etc.)
  - ``ta.*`` calls             -> pass-through (our ``ta`` namespace)
  - Implicit-arg indicators    -> inject ``_high, _low, _close, _volume``
  - ``and`` / ``or`` / ``not`` -> ``&`` / ``|`` / ``~`` with parenthesization
  - ``math.*``                 -> ``np.*``
  - ``nz(x)``                 -> ``x.fillna(0)``
  - Signal conditions          -> mapped via ``if`` block analysis
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from .ast_nodes import (
    Assignment, BinOp, Expr, FuncCall, Ident, IfBlock, InputDecl,
    Literal, Program, PropertyAccess, StrategyAction, StrategyDecl,
    Subscript, UnaryOp,
)
from ..strategy import (
    FloatInput, IntInput, BoolInput, StringInput,
    InputParam, TransformedStrategy,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Implicit-argument injection tables
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ta.* functions that PineScript calls with fewer args than the Python
# implementation needs.  Format:  pine_name -> list of prefixed args to
# *prepend* before the user-provided args.
_IMPLICIT_PREPEND: Dict[str, List[str]] = {
    "atr":        ["_high", "_low", "_close"],
    "dmi":        ["_high", "_low", "_close"],
    "supertrend": ["_high", "_low", "_close"],
    "sar":        ["_high", "_low"],
    "wpr":        ["_high", "_low", "_close"],
}

# ta.* functions where volume must be injected after source arg
# Format: pine_name -> (position_after_which_to_insert, args_to_insert)
_IMPLICIT_INSERT: Dict[str, Tuple[int, List[str]]] = {
    "mfi":  (1, ["_high", "_low", "_close", "_volume"]),
    "vwma": (1, ["_volume"]),
}

# Property-style volume indicators: ta.obv -> ta.obv(_close, _volume)
_PROPERTY_INDICATORS: Dict[str, str] = {
    "obv":     "ta.obv(_close, _volume)",
    "accdist": "ta.accdist(_high, _low, _close, _volume)",
    "pvt":     "ta.pvt(_close, _volume)",
    "wad":     "ta.wad(_high, _low, _close)",
    "vwap":    "ta.vwap(_high, _low, _close, _volume)",
}

# KC / KCW need implicit HLC injected after source
_KC_INDICATORS: Dict[str, Tuple[int, List[str]]] = {
    "kc":  (1, ["_high", "_low", "_close"]),
    "kcw": (1, ["_high", "_low", "_close"]),
}

# math.* -> numpy translation
_MATH_MAP: Dict[str, str] = {
    "abs":   "np.abs",
    "sqrt":  "np.sqrt",
    "log":   "np.log",
    "log10": "np.log10",
    "ceil":  "np.ceil",
    "floor": "np.floor",
    "round": "np.round",
    "max":   "np.maximum",
    "min":   "np.minimum",
    "pow":   "np.power",
}

# PineScript price builtins -> Python variable names
_PRICE_BUILTINS: Dict[str, str] = {
    "close":  "_close",
    "open":   "_open",
    "high":   "_high",
    "low":    "_low",
    "volume": "_volume",
    "hl2":    "_hl2",
    "hlc3":   "_hlc3",
    "hlcc4":  "_hlcc4",
    "ohlc4":  "_ohlc4",
}

# PineScript ``ta.range`` collides with Python builtin — rename in ta.py
_TA_RENAME: Dict[str, str] = {
    "range": "range_indicator",
}


class CodeGenError(Exception):
    pass


class CodeGenerator:
    """
    Walk a ``Program`` AST and produce a ``TransformedStrategy``.

    Usage::

        strategy = CodeGenerator(ast, source=pine_code).generate()
    """

    def __init__(self, ast: Program, source: str = ""):
        self._ast = ast
        self._source = source
        self._lines: List[str] = []
        self._indent = 1              # inside def _compute(...)
        self._inputs: Dict[str, InputParam] = {}
        self._max_period = 0          # for warmup auto-detection
        self._signal_map: Dict[str, str] = {}  # condition_name -> signal_type
        self._fast_mode = False       # True when emitting _compute_fast

    # ── public API ────────────────────────────────────────────

    def generate(self) -> TransformedStrategy:
        self._analyze_signals()
        python_src = self._emit_compute()
        python_fast_src = self._emit_compute_fast()

        # exec() the generated code
        from ..ta import ta, ta_fast  # local import to avoid circular
        import pandas as pd
        import numpy as np

        env: Dict[str, Any] = {"ta": ta, "pd": pd, "np": np}
        exec(python_src, env)
        compute_fn = env["_compute"]

        env_fast: Dict[str, Any] = {"ta": ta_fast, "np": np}
        exec(python_fast_src, env_fast)
        compute_fast_fn = env_fast["_compute_fast"]

        # Extract settings from strategy declaration
        settings = self._extract_settings()

        return TransformedStrategy(
            name=self._ast.strategy_decl.name if self._ast.strategy_decl else "Unnamed",
            inputs=self._inputs,
            compute=compute_fn,
            compute_fast=compute_fast_fn,
            warmup=max(self._max_period * 3, 50),
            pinescript=self._source,
            python_source=python_src,
            python_fast_source=python_fast_src,
            settings=settings,
        )

    # ── signal analysis ──────────────────────────────────────

    def _analyze_signals(self) -> None:
        """
        Analyze ``if`` blocks to map condition names to signal types.

        E.g. if ``longEntryCondition`` block contains
        ``strategy.entry("多單", strategy.long)``, then
        ``longEntryCondition`` maps to ``long_entries``.
        """
        for block in self._ast.if_blocks:
            for action in block.body:
                signal = self._classify_action(action)
                if signal:
                    self._signal_map[block.condition_name] = signal

    def _classify_action(self, action: StrategyAction) -> Optional[str]:
        """Determine which of the 4 signals this action corresponds to."""
        if action.action == "entry":
            # Check direction arg: strategy.long or strategy.short
            if len(action.args) >= 2:
                direction = self._expr_to_str(action.args[1])
                if "long" in direction:
                    return "long_entries"
                if "short" in direction:
                    return "short_entries"
            return "long_entries"  # default

        if action.action == "close":
            # Determine by label: "多單" -> long, "空單" -> short
            if action.args:
                label = self._expr_to_str(action.args[0])
                if "空" in label or "short" in label.lower():
                    return "short_exits"
            return "long_exits"

        if action.action == "exit":
            # strategy.exit is for TP/SL — doesn't map to a signal directly
            return None

        return None

    # ── code emission ────────────────────────────────────────

    def _emit_compute(self) -> str:
        """Generate the full ``_compute`` function source."""
        self._lines = []
        self._indent = 0

        self._emit("def _compute(_df, _p):")
        self._indent = 1

        # Preamble: extract OHLCV columns + derived prices
        self._emit("_close = _df['close']")
        self._emit("_open = _df['open']")
        self._emit("_high = _df['high']")
        self._emit("_low = _df['low']")
        self._emit("_volume = _df['volume']")
        self._emit("_hl2 = (_high + _low) / 2")
        self._emit("_hlc3 = (_high + _low + _close) / 3")
        self._emit("_hlcc4 = (_high + _low + _close + _close) / 4")
        self._emit("_ohlc4 = (_open + _high + _low + _close) / 4")
        self._emit("")

        # Inputs
        if self._ast.inputs:
            self._emit("# --- inputs ---")
            for inp in self._ast.inputs:
                self._emit_input(inp)
            self._emit("")

        # Assignments (indicators, variables, signal conditions)
        if self._ast.assignments:
            self._emit("# --- indicators / variables / signals ---")
            for assign in self._ast.assignments:
                self._emit_assignment(assign)
            self._emit("")

        # Build return signals from signal_map
        self._emit("# --- return signals ---")
        self._emit_signal_return()

        return "\n".join(self._lines)

    def _emit_compute_fast(self) -> str:
        """Generate ``_compute_fast`` — numpy-only, returns 4 bools.

        Uses ``ta`` (bound to ``ta_fast`` at exec-time) instead of pandas.
        Input is 5 raw numpy arrays; output is 4 booleans (last-bar signals).
        """
        self._lines = []
        self._indent = 0
        self._fast_mode = True

        self._emit("def _compute_fast(_open, _high, _low, _close, _volume, _p):")
        self._indent = 1

        # Derived prices (numpy arithmetic — same as pandas)
        self._emit("_hl2 = (_high + _low) / 2.0")
        self._emit("_hlc3 = (_high + _low + _close) / 3.0")
        self._emit("_hlcc4 = (_high + _low + _close + _close) / 4.0")
        self._emit("_ohlc4 = (_open + _high + _low + _close) / 4.0")
        self._emit("")

        # Inputs
        if self._ast.inputs:
            self._emit("# --- inputs ---")
            for inp in self._ast.inputs:
                self._emit(f"{inp.var_name} = _p['{inp.var_name}']")
            self._emit("")

        # Assignments (identical logic — ta_fast has the same method names)
        if self._ast.assignments:
            self._emit("# --- indicators / variables / signals ---")
            for assign in self._ast.assignments:
                self._emit_assignment(assign)
            self._emit("")

        # Build return: extract last-bar boolean from each signal array
        self._emit("# --- return signals (last-bar bools) ---")
        self._emit_signal_return_fast()

        self._fast_mode = False
        return "\n".join(self._lines)

    def _emit_signal_return_fast(self) -> None:
        """Emit return of 4 booleans — last element of each signal array."""
        signals = {
            "long_entries": None,
            "long_exits": None,
            "short_entries": None,
            "short_exits": None,
        }
        for cond_name, signal_type in self._signal_map.items():
            if signal_type in signals:
                signals[signal_type] = cond_name

        parts = []
        for sig_name, cond_var in signals.items():
            if cond_var:
                # Extract last element; handle NaN → False
                parts.append(
                    f"(bool({cond_var}[-1]) if not np.isnan({cond_var}[-1]) else False)"
                    f" if hasattr({cond_var}, '__len__') else bool({cond_var})"
                )
            else:
                parts.append("False")

        self._emit("return (")
        for i, part in enumerate(parts):
            comma = "," if i < len(parts) - 1 else ","
            self._emit(f"    {part}{comma}")
        self._emit(")")

    def _emit(self, line: str) -> None:
        prefix = "    " * self._indent
        self._lines.append(prefix + line)

    # ── input emission ───────────────────────────────────────

    def _emit_input(self, inp: InputDecl) -> None:
        """Emit input extraction + register InputParam."""
        self._emit(f"{inp.var_name} = _p['{inp.var_name}']")

        # Register in inputs dict
        if inp.input_type == "int":
            self._inputs[inp.var_name] = IntInput(
                default=int(inp.default), title=inp.title,
                minval=inp.kwargs.get("minval"),
                maxval=inp.kwargs.get("maxval"),
                step=inp.kwargs.get("step", 1),
            )
        elif inp.input_type == "float":
            self._inputs[inp.var_name] = FloatInput(
                default=float(inp.default), title=inp.title,
                minval=inp.kwargs.get("minval"),
                maxval=inp.kwargs.get("maxval"),
                step=inp.kwargs.get("step", 0.1),
            )
        elif inp.input_type == "bool":
            self._inputs[inp.var_name] = BoolInput(
                default=bool(inp.default), title=inp.title,
            )
        elif inp.input_type in ("string", "source"):
            self._inputs[inp.var_name] = StringInput(
                default=str(inp.default), title=inp.title,
            )

    # ── assignment emission ──────────────────────────────────

    def _emit_assignment(self, assign: Assignment) -> None:
        rhs = self._expr_to_python(assign.expr)

        if len(assign.targets) == 1:
            self._emit(f"{assign.targets[0]} = {rhs}")
        else:
            # Tuple destructuring
            lhs = ", ".join(assign.targets)
            self._emit(f"{lhs} = {rhs}")

    # ── signal return ────────────────────────────────────────

    def _emit_signal_return(self) -> None:
        """Emit the 4-tuple return, mapping condition names to signal positions."""
        signals = {
            "long_entries": None,
            "long_exits": None,
            "short_entries": None,
            "short_exits": None,
        }

        for cond_name, signal_type in self._signal_map.items():
            if signal_type in signals:
                signals[signal_type] = cond_name

        parts = []
        for sig_name, cond_var in signals.items():
            if cond_var:
                parts.append(f"{cond_var}.fillna(False)")
            else:
                parts.append("pd.Series(False, index=_df.index)")

        self._emit("return (")
        for i, part in enumerate(parts):
            comma = "," if i < len(parts) - 1 else ","
            self._emit(f"    {part}{comma}")
        self._emit(")")

    # ── expression -> Python string ──────────────────────────

    def _expr_to_python(self, expr: Expr) -> str:
        """Recursively convert an AST expression to Python source."""

        if isinstance(expr, Literal):
            return self._literal_to_python(expr)

        if isinstance(expr, Ident):
            return self._ident_to_python(expr.name)

        if isinstance(expr, BinOp):
            left = self._expr_to_python(expr.left)
            right = self._expr_to_python(expr.right)
            if expr.op == "and":
                return f"({left}) & ({right})"
            if expr.op == "or":
                return f"({left}) | ({right})"
            return f"({left} {expr.op} {right})"

        if isinstance(expr, UnaryOp):
            operand = self._expr_to_python(expr.operand)
            if expr.op == "not":
                return f"~({operand})"
            return f"({expr.op}{operand})"

        if isinstance(expr, FuncCall):
            return self._func_call_to_python(expr)

        if isinstance(expr, Subscript):
            inner = self._expr_to_python(expr.expr)
            return f"({inner})[{expr.index}]"

        if isinstance(expr, PropertyAccess):
            return self._property_to_python(expr)

        return "np.nan"

    def _literal_to_python(self, lit: Literal) -> str:
        if lit.value is None:
            return "np.nan"
        if isinstance(lit.value, bool):
            return "True" if lit.value else "False"
        if isinstance(lit.value, str):
            return repr(lit.value)
        return str(lit.value)

    def _ident_to_python(self, name: str) -> str:
        """Translate an identifier, mapping price builtins."""
        if name in _PRICE_BUILTINS:
            return _PRICE_BUILTINS[name]
        if name.startswith("strategy."):
            return repr(name)  # keep as string literal
        return name

    def _property_to_python(self, prop: PropertyAccess) -> str:
        """Handle ``ta.obv``, ``strategy.long``, etc."""
        if prop.namespace == "ta" and prop.name in _PROPERTY_INDICATORS:
            return _PROPERTY_INDICATORS[prop.name]
        if prop.namespace == "strategy":
            return repr(f"strategy.{prop.name}")
        return f"{prop.namespace}.{prop.name}"

    def _func_call_to_python(self, call: FuncCall) -> str:
        """Translate a function call expression."""

        # --- nz() ---
        if call.namespace is None and call.name == "nz":
            if call.args:
                inner = self._expr_to_python(call.args[0])
                replacement = "0" if len(call.args) < 2 else self._expr_to_python(call.args[1])
                if self._fast_mode:
                    return f"ta.nz({inner}, {replacement})"
                return f"({inner}).fillna({replacement})"
            return "np.nan"

        # --- math.* ---
        if call.namespace == "math":
            np_func = _MATH_MAP.get(call.name)
            if np_func:
                args_str = ", ".join(self._expr_to_python(a) for a in call.args)
                return f"{np_func}({args_str})"
            return f"np.{call.name}({', '.join(self._expr_to_python(a) for a in call.args)})"

        # --- ta.* ---
        if call.namespace == "ta":
            return self._ta_call_to_python(call)

        # --- input.* (shouldn't appear in expressions, but handle gracefully) ---
        if call.namespace == "input":
            return "np.nan"

        # --- other function calls ---
        args_str = ", ".join(self._expr_to_python(a) for a in call.args)
        if call.namespace:
            return f"{call.namespace}.{call.name}({args_str})"
        return f"{call.name}({args_str})"

    def _ta_call_to_python(self, call: FuncCall) -> str:
        """Translate ``ta.*`` call with implicit arg injection."""
        func_name = call.name
        python_name = _TA_RENAME.get(func_name, func_name)

        # Convert args to Python
        user_args = [self._expr_to_python(a) for a in call.args]

        # Track periods for warmup detection
        self._track_period(call)

        # Prepend implicit args
        if func_name in _IMPLICIT_PREPEND:
            prefix = _IMPLICIT_PREPEND[func_name]
            all_args = prefix + user_args
        elif func_name in _IMPLICIT_INSERT:
            pos, to_insert = _IMPLICIT_INSERT[func_name]
            all_args = user_args[:pos] + to_insert + user_args[pos:]
        elif func_name in _KC_INDICATORS:
            pos, to_insert = _KC_INDICATORS[func_name]
            all_args = user_args[:pos] + to_insert + user_args[pos:]
        else:
            all_args = user_args

        # Handle kwargs
        kwarg_parts = []
        for k, v in call.kwargs.items():
            kwarg_parts.append(f"{k}={self._expr_to_python(v)}")

        all_parts = all_args + kwarg_parts
        return f"ta.{python_name}({', '.join(all_parts)})"

    def _track_period(self, call: FuncCall) -> None:
        """Track the maximum numeric period argument for warmup estimation."""
        for arg in call.args:
            if isinstance(arg, Literal) and isinstance(arg.value, (int, float)):
                val = int(arg.value)
                if 1 <= val <= 1000:
                    self._max_period = max(self._max_period, val)
            if isinstance(arg, Ident):
                # Try to resolve from inputs
                if arg.name in self._inputs:
                    inp = self._inputs[arg.name]
                    if isinstance(inp, (IntInput, FloatInput)):
                        self._max_period = max(self._max_period, int(inp.default))

    # ── settings extraction ──────────────────────────────────

    def _extract_settings(self) -> Dict[str, Any]:
        """Extract strategy settings from the declaration kwargs."""
        settings: Dict[str, Any] = {}
        if not self._ast.strategy_decl:
            return settings

        kw = self._ast.strategy_decl.kwargs
        if "initial_capital" in kw:
            settings["initial_capital"] = float(kw["initial_capital"])
        if "commission_value" in kw:
            settings["commission_value"] = float(kw["commission_value"])
        if "slippage" in kw:
            settings["slippage"] = float(kw["slippage"])
        if "default_qty_value" in kw:
            settings["default_qty_value"] = float(kw["default_qty_value"])
        if "default_qty_type" in kw:
            settings["default_qty_type"] = kw["default_qty_type"]
        if "pyramiding" in kw:
            settings["pyramiding"] = int(kw["pyramiding"])
        if "currency" in kw:
            settings["currency"] = kw["currency"]

        return settings

    # ── utility ──────────────────────────────────────────────

    def _expr_to_str(self, expr: Expr) -> str:
        """Quick string representation of an expression (for label matching)."""
        if isinstance(expr, Literal):
            return str(expr.value) if expr.value is not None else "na"
        if isinstance(expr, Ident):
            return expr.name
        if isinstance(expr, PropertyAccess):
            return f"{expr.namespace}.{expr.name}"
        return self._expr_to_python(expr)
