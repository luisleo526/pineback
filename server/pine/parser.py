"""
Recursive-descent parser for builder-generated PineScript.

Produces a ``Program`` AST from the token stream.

The parser processes the **fixed sections** in order:
  1. ``//@version=6`` pragma (skip)
  2. ``strategy(...)`` declaration
  3. ``input.*`` declarations
  4. Assignments (indicators, variables, signal conditions)
  5. ``if`` blocks with ``strategy.*()`` actions
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .tokens import Token, TokenType, TokenizerError
from .ast_nodes import (
    Assignment, BinOp, Expr, FuncCall, Ident, IfBlock, InputDecl,
    Literal, Program, PropertyAccess, StrategyAction, StrategyDecl,
    Subscript, UnaryOp,
)


class ParseError(Exception):
    def __init__(self, message: str, token: Optional[Token] = None):
        line = token.line if token else 0
        super().__init__(f"Line {line}: {message}")
        self.token = token


class Parser:
    """
    Parse a token list into a ``Program`` AST.

    Usage::

        ast = Parser(tokens).parse()
    """

    def __init__(self, tokens: List[Token]):
        self._tokens = tokens
        self._pos = 0

    # ── helpers ───────────────────────────────────────────────

    def _cur(self) -> Token:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return Token(TokenType.EOF, "", 0)

    def _peek(self, offset: int = 0) -> Token:
        idx = self._pos + offset
        if idx < len(self._tokens):
            return self._tokens[idx]
        return Token(TokenType.EOF, "", 0)

    def _advance(self) -> Token:
        tok = self._cur()
        self._pos += 1
        return tok

    def _expect(self, ttype: TokenType, value: Optional[str] = None) -> Token:
        tok = self._cur()
        if tok.type != ttype:
            raise ParseError(
                f"Expected {ttype.name} but got {tok.type.name} ({tok.value!r})", tok
            )
        if value is not None and tok.value != value:
            raise ParseError(
                f"Expected {value!r} but got {tok.value!r}", tok
            )
        return self._advance()

    def _match(self, ttype: TokenType, value: Optional[str] = None) -> Optional[Token]:
        tok = self._cur()
        if tok.type == ttype and (value is None or tok.value == value):
            return self._advance()
        return None

    def _skip_newlines(self) -> None:
        while self._cur().type == TokenType.NEWLINE:
            self._advance()

    def _at_end(self) -> bool:
        return self._cur().type == TokenType.EOF

    # ── public API ────────────────────────────────────────────

    def parse(self) -> Program:
        prog = Program()
        self._skip_newlines()

        # 1. Skip //@version pragma (already stripped as comment by tokenizer,
        #    but handle any remaining version line)
        self._try_skip_version()
        self._skip_newlines()

        # 2. strategy() declaration
        if self._cur().type == TokenType.KEYWORD and self._cur().value == "strategy":
            prog.strategy_decl = self._parse_strategy_decl()
            self._skip_newlines()

        # 3-6. Parse assignments and if-blocks
        while not self._at_end():
            self._skip_newlines()
            if self._at_end():
                break

            # if-block
            if self._cur().type == TokenType.KEYWORD and self._cur().value == "if":
                prog.if_blocks.append(self._parse_if_block())
                continue

            # Assignment: ident = ... or [a, b, c] = ...
            if self._is_assignment_start():
                node = self._parse_assignment_or_input()
                if isinstance(node, InputDecl):
                    prog.inputs.append(node)
                elif isinstance(node, Assignment):
                    prog.assignments.append(node)
                continue

            # Skip unrecognized lines
            self._skip_to_next_line()

        return prog

    # ── version pragma ───────────────────────────────────────

    def _try_skip_version(self) -> None:
        """Skip any leftover version pragma tokens."""
        # //@version=6 is normally a comment and stripped,
        # but if it somehow appears as tokens, skip the line.
        pass

    # ── strategy() declaration ───────────────────────────────

    def _parse_strategy_decl(self) -> StrategyDecl:
        self._expect(TokenType.KEYWORD, "strategy")
        self._expect(TokenType.LPAREN)

        # First arg: strategy name (string)
        name_tok = self._expect(TokenType.STRING)
        name = name_tok.value

        kwargs: Dict[str, Any] = {}
        while self._match(TokenType.COMMA):
            # key = value
            key_tok = self._cur()
            if key_tok.type not in (TokenType.IDENT, TokenType.KEYWORD):
                break
            key = self._advance().value
            self._expect(TokenType.ASSIGN)
            val = self._parse_literal_value()
            kwargs[key] = val

        self._expect(TokenType.RPAREN)
        self._skip_newlines()
        return StrategyDecl(name=name, kwargs=kwargs)

    def _parse_literal_value(self) -> Any:
        """Parse a literal value (number, string, bool, ident for constants)."""
        tok = self._cur()

        if tok.type == TokenType.NUMBER:
            self._advance()
            return float(tok.value) if "." in tok.value else int(tok.value)

        if tok.type == TokenType.STRING:
            self._advance()
            return tok.value

        if tok.type == TokenType.KEYWORD:
            if tok.value == "true":
                self._advance()
                return True
            if tok.value == "false":
                self._advance()
                return False

        # Could be a dotted constant like strategy.percent_of_equity
        if tok.type in (TokenType.IDENT, TokenType.KEYWORD):
            parts = [self._advance().value]
            while self._match(TokenType.DOT):
                parts.append(self._advance().value)
            return ".".join(parts)

        raise ParseError(f"Expected literal value, got {tok.type.name}", tok)

    # ── assignment / input detection ─────────────────────────

    def _is_assignment_start(self) -> bool:
        """Check if current position starts an assignment."""
        tok = self._cur()
        # [a, b, c] = ...
        if tok.type == TokenType.LBRACKET:
            return True
        # ident = ... (but not ident(...) which would be a call)
        if tok.type == TokenType.IDENT:
            # Look ahead for = sign (possibly after newlines)
            j = self._pos + 1
            while j < len(self._tokens) and self._tokens[j].type == TokenType.NEWLINE:
                j += 1
            if j < len(self._tokens) and self._tokens[j].type == TokenType.ASSIGN:
                return True
        return False

    def _parse_assignment_or_input(self):
        """Parse an assignment.  Returns InputDecl or Assignment."""
        # Tuple assignment: [a, b, c] = expr
        if self._cur().type == TokenType.LBRACKET:
            targets = self._parse_tuple_targets()
            self._expect(TokenType.ASSIGN)
            expr = self._parse_expr()
            self._skip_newlines()
            return Assignment(targets=targets, expr=expr)

        # Single assignment: name = expr
        name_tok = self._expect(TokenType.IDENT)
        name = name_tok.value
        self._expect(TokenType.ASSIGN)

        # Check if RHS is input.*()
        if (self._cur().type == TokenType.IDENT and self._cur().value == "input"
                and self._peek(1).type == TokenType.DOT):
            inp = self._parse_input_decl(name)
            self._skip_newlines()
            return inp

        expr = self._parse_expr()
        self._skip_newlines()
        return Assignment(targets=[name], expr=expr)

    def _parse_tuple_targets(self) -> List[str]:
        """Parse ``[a, b, c]``."""
        self._expect(TokenType.LBRACKET)
        targets = [self._expect(TokenType.IDENT).value]
        while self._match(TokenType.COMMA):
            targets.append(self._expect(TokenType.IDENT).value)
        self._expect(TokenType.RBRACKET)
        return targets

    # ── input declarations ───────────────────────────────────

    def _parse_input_decl(self, var_name: str) -> InputDecl:
        """Parse ``input.int(default, "title", key=val, ...)``."""
        self._expect(TokenType.IDENT, "input")
        self._expect(TokenType.DOT)
        type_tok = self._expect(TokenType.IDENT)
        input_type = type_tok.value       # int, float, bool, string, source

        self._expect(TokenType.LPAREN)

        # First positional arg: default value
        default = self._parse_literal_value()

        # Second positional arg: title (string)
        title = var_name
        if self._match(TokenType.COMMA):
            if self._cur().type == TokenType.STRING:
                title = self._advance().value
            else:
                # It might be a kwarg, rewind logic handled below
                # Actually check if it's key=value
                if self._cur().type == TokenType.IDENT and self._peek(1).type == TokenType.ASSIGN:
                    pass  # will be parsed as kwargs below
                else:
                    title = str(self._parse_literal_value())

        # Remaining kwargs: minval=..., maxval=..., step=...
        kwargs: Dict[str, Any] = {}
        while self._match(TokenType.COMMA):
            if self._cur().type in (TokenType.IDENT, TokenType.KEYWORD):
                if self._peek(1).type == TokenType.ASSIGN:
                    key = self._advance().value
                    self._expect(TokenType.ASSIGN)
                    val = self._parse_literal_value()
                    kwargs[key] = val
                    continue
            # Skip unknown positional args
            self._parse_literal_value()

        self._expect(TokenType.RPAREN)
        return InputDecl(
            var_name=var_name,
            input_type=input_type,
            default=default,
            title=title,
            kwargs=kwargs,
        )

    # ── if blocks ────────────────────────────────────────────

    def _parse_if_block(self) -> IfBlock:
        self._expect(TokenType.KEYWORD, "if")
        cond_tok = self._expect(TokenType.IDENT)
        cond_name = cond_tok.value
        self._skip_newlines()

        block = IfBlock(condition_name=cond_name)

        # Expect INDENT
        if not self._match(TokenType.INDENT):
            return block

        while self._cur().type != TokenType.DEDENT and not self._at_end():
            self._skip_newlines()
            if self._cur().type == TokenType.DEDENT:
                break

            # Parse strategy.entry/close/exit
            if (self._cur().type == TokenType.KEYWORD
                    and self._cur().value == "strategy"):
                action = self._parse_strategy_action()
                if action:
                    block.body.append(action)
            else:
                self._skip_to_next_line()

        self._match(TokenType.DEDENT)
        self._skip_newlines()
        return block

    def _parse_strategy_action(self) -> Optional[StrategyAction]:
        """Parse ``strategy.entry/close/exit(...)``."""
        self._expect(TokenType.KEYWORD, "strategy")
        self._expect(TokenType.DOT)
        action_tok = self._expect(TokenType.IDENT)
        action = action_tok.value       # entry, close, exit

        self._expect(TokenType.LPAREN)
        args: List[Expr] = []
        kwargs: Dict[str, Expr] = {}

        if self._cur().type != TokenType.RPAREN:
            self._parse_call_args(args, kwargs)

        self._expect(TokenType.RPAREN)
        self._skip_newlines()
        return StrategyAction(action=action, args=args, kwargs=kwargs)

    # ── expression parser (precedence climbing) ──────────────

    def _parse_expr(self) -> Expr:
        return self._parse_or()

    def _parse_or(self) -> Expr:
        left = self._parse_and()
        while self._match(TokenType.KEYWORD, "or"):
            right = self._parse_and()
            left = BinOp(left=left, op="or", right=right)
        return left

    def _parse_and(self) -> Expr:
        left = self._parse_not()
        while self._match(TokenType.KEYWORD, "and"):
            right = self._parse_not()
            left = BinOp(left=left, op="and", right=right)
        return left

    def _parse_not(self) -> Expr:
        if self._match(TokenType.KEYWORD, "not"):
            operand = self._parse_not()
            return UnaryOp(op="not", operand=operand)
        return self._parse_comparison()

    def _parse_comparison(self) -> Expr:
        left = self._parse_add_sub()
        comp_ops = {">", "<", ">=", "<=", "==", "!="}
        if self._cur().type == TokenType.OP and self._cur().value in comp_ops:
            op = self._advance().value
            right = self._parse_add_sub()
            return BinOp(left=left, op=op, right=right)
        return left

    def _parse_add_sub(self) -> Expr:
        left = self._parse_mul_div()
        while self._cur().type == TokenType.OP and self._cur().value in ("+", "-"):
            op = self._advance().value
            right = self._parse_mul_div()
            left = BinOp(left=left, op=op, right=right)
        return left

    def _parse_mul_div(self) -> Expr:
        left = self._parse_unary()
        while self._cur().type == TokenType.OP and self._cur().value in ("*", "/", "%"):
            op = self._advance().value
            right = self._parse_unary()
            left = BinOp(left=left, op=op, right=right)
        return left

    def _parse_unary(self) -> Expr:
        if self._cur().type == TokenType.OP and self._cur().value in ("-", "+"):
            op = self._advance().value
            operand = self._parse_unary()
            if op == "+":
                return operand
            return UnaryOp(op=op, operand=operand)
        return self._parse_postfix()

    def _parse_postfix(self) -> Expr:
        """Parse primary then optional [index] subscript."""
        expr = self._parse_primary()
        # Handle [N] subscript (e.g. ta.macd(...)[0])
        if self._cur().type == TokenType.LBRACKET:
            self._advance()
            idx_tok = self._expect(TokenType.NUMBER)
            idx = int(idx_tok.value)
            self._expect(TokenType.RBRACKET)
            expr = Subscript(expr=expr, index=idx)
        return expr

    def _parse_primary(self) -> Expr:
        tok = self._cur()

        # Number
        if tok.type == TokenType.NUMBER:
            self._advance()
            if "." in tok.value:
                return Literal(value=float(tok.value))
            return Literal(value=int(tok.value))

        # String
        if tok.type == TokenType.STRING:
            self._advance()
            return Literal(value=tok.value)

        # Keywords: true, false, na
        if tok.type == TokenType.KEYWORD:
            if tok.value == "true":
                self._advance()
                return Literal(value=True)
            if tok.value == "false":
                self._advance()
                return Literal(value=False)
            if tok.value == "na":
                self._advance()
                return Literal(value=None)
            # 'strategy' as part of dotted access (strategy.long etc.)
            if tok.value == "strategy":
                self._advance()
                if self._match(TokenType.DOT):
                    name = self._advance().value
                    return Ident(name=f"strategy.{name}")
                return Ident(name="strategy")

        # Parenthesized expression
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expr()
            self._expect(TokenType.RPAREN)
            return expr

        # Identifier — could be:
        #   - simple ident
        #   - dotted: namespace.func(...)  or  namespace.property
        #   - function call: func(...)
        if tok.type == TokenType.IDENT:
            name = self._advance().value

            # Check for dot (namespace access)
            if self._cur().type == TokenType.DOT:
                self._advance()  # consume dot
                member_tok = self._cur()
                if member_tok.type not in (TokenType.IDENT, TokenType.KEYWORD):
                    raise ParseError(
                        f"Expected identifier after '.', got {member_tok.type.name}",
                        member_tok,
                    )
                member = self._advance().value

                # namespace.member(...) -> function call
                if self._cur().type == TokenType.LPAREN:
                    return self._parse_func_call(namespace=name, func_name=member)

                # namespace.member -> property access (e.g. ta.obv, strategy.long)
                return PropertyAccess(namespace=name, name=member)

            # func(...)
            if self._cur().type == TokenType.LPAREN:
                return self._parse_func_call(namespace=None, func_name=name)

            # Simple identifier
            return Ident(name=name)

        raise ParseError(f"Unexpected token: {tok.type.name} ({tok.value!r})", tok)

    def _parse_func_call(self, namespace: Optional[str],
                         func_name: str) -> FuncCall:
        """Parse ``name(args, key=val, ...)``."""
        self._expect(TokenType.LPAREN)
        args: List[Expr] = []
        kwargs: Dict[str, Expr] = {}

        if self._cur().type != TokenType.RPAREN:
            self._parse_call_args(args, kwargs)

        self._expect(TokenType.RPAREN)
        return FuncCall(namespace=namespace, name=func_name,
                        args=args, kwargs=kwargs)

    def _parse_call_args(self, args: List[Expr],
                         kwargs: Dict[str, Expr]) -> None:
        """Parse comma-separated arguments (positional and keyword)."""
        while True:
            # Check for keyword argument: ident = expr
            if (self._cur().type == TokenType.IDENT
                    and self._peek(1).type == TokenType.ASSIGN):
                key = self._advance().value
                self._expect(TokenType.ASSIGN)
                val = self._parse_expr()
                kwargs[key] = val
            else:
                args.append(self._parse_expr())

            if not self._match(TokenType.COMMA):
                break

    # ── utility ──────────────────────────────────────────────

    def _skip_to_next_line(self) -> None:
        while not self._at_end() and self._cur().type != TokenType.NEWLINE:
            self._advance()
        self._skip_newlines()
