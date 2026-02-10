"""
PineScript tokenizer for builder-generated code.

Handles:
  - ``//`` comment stripping
  - Multi-line continuation (unbalanced parentheses)
  - Indentation-based INDENT / DEDENT (for ``if`` blocks)
  - All token types used by the builder output
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()

    # Identifiers & keywords
    IDENT = auto()
    KEYWORD = auto()       # if, and, or, not, true, false, na, strategy

    # Punctuation
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    COMMA = auto()         # ,
    DOT = auto()           # .
    ASSIGN = auto()        # =

    # Operators
    OP = auto()            # +  -  *  /  %  >  <  >=  <=  ==  !=

    # Structure
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


KEYWORDS = frozenset({
    "if", "and", "or", "not", "true", "false", "na", "strategy",
})

# Two-character operators (must be checked before single-char)
_TWO_CHAR_OPS = {">=", "<=", "==", "!="}
_SINGLE_CHAR_OPS = frozenset("+-*/%><")


@dataclass
class Token:
    type: TokenType
    value: str
    line: int               # 1-based line number (of the original source)

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line})"


class TokenizerError(Exception):
    """Raised on invalid input."""
    def __init__(self, message: str, line: int):
        super().__init__(f"Line {line}: {message}")
        self.line = line


class Tokenizer:
    """
    Convert PineScript source into a flat token stream.

    Usage::

        tokens = Tokenizer(source).tokenize()
    """

    def __init__(self, source: str):
        self._raw = source
        self._tokens: List[Token] = []

    # ── public API ────────────────────────────────────────────

    def tokenize(self) -> List[Token]:
        lines = self._preprocess(self._raw)
        self._tokens = []
        indent_stack = [0]

        for line_no, line in lines:
            if not line.strip():
                continue

            # Measure leading whitespace
            stripped = line.lstrip(" ")
            indent = len(line) - len(stripped)
            text = stripped

            # Emit INDENT / DEDENT
            if indent > indent_stack[-1]:
                indent_stack.append(indent)
                self._tokens.append(Token(TokenType.INDENT, "", line_no))
            while indent < indent_stack[-1]:
                indent_stack.pop()
                self._tokens.append(Token(TokenType.DEDENT, "", line_no))

            # Tokenize the line content
            self._tokenize_line(text, line_no)
            self._tokens.append(Token(TokenType.NEWLINE, "\\n", line_no))

        # Close remaining indents
        while len(indent_stack) > 1:
            indent_stack.pop()
            self._tokens.append(Token(TokenType.DEDENT, "", 0))

        self._tokens.append(Token(TokenType.EOF, "", 0))
        return self._tokens

    # ── preprocessing ────────────────────────────────────────

    @staticmethod
    def _preprocess(source: str) -> List[tuple]:
        """
        1. Strip ``//`` comments.
        2. Join continuation lines (unbalanced parentheses / brackets).
        Returns list of ``(line_number, content)`` tuples.
        """
        raw_lines = source.split("\n")
        processed: List[tuple] = []
        paren_depth = 0
        bracket_depth = 0
        accum = ""
        accum_start = 0

        for i, line in enumerate(raw_lines, start=1):
            # Strip inline comments (but not inside strings)
            line = Tokenizer._strip_comment(line)

            if paren_depth > 0 or bracket_depth > 0:
                # Continuation line — append to accumulator
                accum += " " + line.strip()
            else:
                if accum:
                    processed.append((accum_start, accum))
                accum = line.rstrip()
                accum_start = i

            # Track paren / bracket depth
            for ch in line:
                if ch == "(":
                    paren_depth += 1
                elif ch == ")":
                    paren_depth = max(0, paren_depth - 1)
                elif ch == "[":
                    bracket_depth += 1
                elif ch == "]":
                    bracket_depth = max(0, bracket_depth - 1)

        if accum:
            processed.append((accum_start, accum))

        return processed

    @staticmethod
    def _strip_comment(line: str) -> str:
        """Remove ``//`` comment, but preserve strings."""
        in_string = False
        for i, ch in enumerate(line):
            if ch == '"' and (i == 0 or line[i - 1] != "\\"):
                in_string = not in_string
            elif ch == "/" and not in_string and i + 1 < len(line) and line[i + 1] == "/":
                return line[:i]
        return line

    # ── line tokenization ────────────────────────────────────

    def _tokenize_line(self, text: str, line_no: int) -> None:
        i = 0
        n = len(text)

        while i < n:
            ch = text[i]

            # Whitespace
            if ch in " \t":
                i += 1
                continue

            # String literal
            if ch == '"':
                j = i + 1
                while j < n and text[j] != '"':
                    if text[j] == "\\":
                        j += 1  # skip escaped char
                    j += 1
                j += 1  # closing quote
                self._tokens.append(
                    Token(TokenType.STRING, text[i + 1 : j - 1], line_no)
                )
                i = j
                continue

            # Number
            if ch.isdigit() or (ch == "." and i + 1 < n and text[i + 1].isdigit()):
                j = i
                has_dot = False
                while j < n and (text[j].isdigit() or text[j] == "."):
                    if text[j] == ".":
                        if has_dot:
                            break
                        has_dot = True
                    j += 1
                self._tokens.append(Token(TokenType.NUMBER, text[i:j], line_no))
                i = j
                continue

            # Two-char operators
            if i + 1 < n and text[i : i + 2] in _TWO_CHAR_OPS:
                self._tokens.append(Token(TokenType.OP, text[i : i + 2], line_no))
                i += 2
                continue

            # Single-char operators
            if ch in _SINGLE_CHAR_OPS:
                self._tokens.append(Token(TokenType.OP, ch, line_no))
                i += 1
                continue

            # Assignment (single =, but not ==)
            if ch == "=":
                self._tokens.append(Token(TokenType.ASSIGN, "=", line_no))
                i += 1
                continue

            # Punctuation
            if ch == "(":
                self._tokens.append(Token(TokenType.LPAREN, "(", line_no))
                i += 1
                continue
            if ch == ")":
                self._tokens.append(Token(TokenType.RPAREN, ")", line_no))
                i += 1
                continue
            if ch == "[":
                self._tokens.append(Token(TokenType.LBRACKET, "[", line_no))
                i += 1
                continue
            if ch == "]":
                self._tokens.append(Token(TokenType.RBRACKET, "]", line_no))
                i += 1
                continue
            if ch == ",":
                self._tokens.append(Token(TokenType.COMMA, ",", line_no))
                i += 1
                continue
            if ch == ".":
                self._tokens.append(Token(TokenType.DOT, ".", line_no))
                i += 1
                continue

            # Identifier / keyword
            if ch.isalpha() or ch == "_":
                j = i
                while j < n and (text[j].isalnum() or text[j] == "_"):
                    j += 1
                word = text[i:j]
                if word in KEYWORDS:
                    self._tokens.append(Token(TokenType.KEYWORD, word, line_no))
                else:
                    self._tokens.append(Token(TokenType.IDENT, word, line_no))
                i = j
                continue

            # Unknown character — skip
            i += 1
