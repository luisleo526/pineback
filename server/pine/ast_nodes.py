"""
AST node types for the PineScript compiler.

These dataclasses represent the parsed structure of builder-generated
PineScript. The parser produces a ``Program`` tree; the code generator
walks it to emit vectorized Python.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Expression nodes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Literal:
    """Number, string, bool, or ``na``."""
    value: Any                    # int | float | str | bool | None (na)


@dataclass
class Ident:
    """Simple identifier (variable name, price source, etc.)."""
    name: str


@dataclass
class BinOp:
    """Binary operation: ``left op right``."""
    left: Expr
    op: str                       # +, -, *, /, %, >, <, >=, <=, ==, !=, and, or
    right: Expr


@dataclass
class UnaryOp:
    """Unary operation: ``op operand`` (e.g. ``-x``, ``not cond``)."""
    op: str                       # "-", "+", "not"
    operand: Expr


@dataclass
class FuncCall:
    """Function call: ``[namespace.]name(args, key=val, ...)``."""
    namespace: Optional[str]      # "ta", "math", "strategy", "input", or None
    name: str
    args: List[Expr] = field(default_factory=list)
    kwargs: Dict[str, Expr] = field(default_factory=dict)


@dataclass
class Subscript:
    """Index access: ``expr[index]`` (e.g. ``ta.macd(...)[0]``)."""
    expr: Expr
    index: int


@dataclass
class PropertyAccess:
    """Property access without parens: ``namespace.name`` (e.g. ``ta.obv``)."""
    namespace: str
    name: str


# Union of all expression types
Expr = Union[Literal, Ident, BinOp, UnaryOp, FuncCall, Subscript, PropertyAccess]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Top-level statement nodes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class StrategyDecl:
    """``strategy("name", overlay=true, initial_capital=10000, ...)``."""
    name: str
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InputDecl:
    """``varName = input.int(default, "title", minval=..., ...)``."""
    var_name: str
    input_type: str               # "int", "float", "bool", "string", "source"
    default: Any
    title: str
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Assignment:
    """
    Generic assignment: ``name = expr`` or ``[a, b, c] = expr``.

    Covers indicator calls, variable assignments, and signal assignments.
    """
    targets: List[str]            # single-element for simple, multi for tuple
    expr: Expr


@dataclass
class StrategyAction:
    """``strategy.entry(...)``, ``strategy.close(...)``, ``strategy.exit(...)``."""
    action: str                   # "entry", "close", "exit"
    args: List[Expr] = field(default_factory=list)
    kwargs: Dict[str, Expr] = field(default_factory=dict)


@dataclass
class IfBlock:
    """``if conditionName\\n    strategy.*(...)``."""
    condition_name: str           # the identifier used as condition
    body: List[StrategyAction] = field(default_factory=list)


@dataclass
class Program:
    """Root AST node — a complete parsed PineScript strategy."""
    version: int = 6
    strategy_decl: Optional[StrategyDecl] = None
    inputs: List[InputDecl] = field(default_factory=list)
    assignments: List[Assignment] = field(default_factory=list)
    if_blocks: List[IfBlock] = field(default_factory=list)
