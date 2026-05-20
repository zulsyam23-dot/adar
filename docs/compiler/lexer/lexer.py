from __future__ import annotations
import re
from adar.lexer.token import Token, TokenType, SourceLocation, KEYWORDS


_UNITS = (
    "px", "rem", "em", "ex", "ch", "vh", "vw", "vmin", "vmax",
    "cm", "mm", "in", "pt", "pc", "deg", "rad", "grad", "turn",
    "s", "ms", "Hz", "kHz", "dpi", "dpcm", "dppx", "fr", "q", "%",
)

_UNIT_RE = re.compile(r"(%s)" % "|".join(sorted(_UNITS, key=len, reverse=True)), re.IGNORECASE)


class Lexer:
    def __init__(self, source: str, filename: str = "") -> None:
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: list[Token] = []
        self._token_index = 0

    def _loc(self) -> SourceLocation:
        return SourceLocation(self.line, self.col, self.filename)

    def _error(self, msg: str) -> None:
        loc = self._loc()
        raise SyntaxError(f"{loc}: {msg}")

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else ""

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < len(self.source):
            ch = self._peek()
            if ch in " \t\r":
                self._advance()
            elif ch == "\n":
                self._advance()
                self._emit(TokenType.NEWLINE, "\\n")
            elif ch == "/" and self._peek(1) == "/":
                while self.pos < len(self.source) and self._peek() != "\n":
                    self._advance()
            elif ch == "/" and self._peek(1) == "*":
                self._advance()
                self._advance()
                while self.pos < len(self.source):
                    if self._peek() == "*" and self._peek(1) == "/":
                        self._advance()
                        self._advance()
                        break
                    self._advance()
            else:
                break

    def _emit(self, type_: TokenType, value: str = "") -> None:
        self.tokens.append(Token(type_, value, self._loc()))

    def _read_string(self, quote: str) -> str:
        result = []
        while self.pos < len(self.source):
            ch = self._advance()
            if ch == "\\":
                if self.pos < len(self.source):
                    result.append(self._advance())
            elif ch == quote:
                return "".join(result)
            else:
                result.append(ch)
        self._error("Unterminated string literal")

    def _read_number(self) -> tuple[str, str]:
        num = []
        if self._peek() == "-" or self._peek() == "+":
            num.append(self._advance())
        while self.pos < len(self.source) and self._peek().isdigit():
            num.append(self._advance())
        if self._peek() == "." and self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit():
            num.append(self._advance())
            while self.pos < len(self.source) and self._peek().isdigit():
                num.append(self._advance())
        unit = ""
        if num and num != ["-"] and num != ["+"]:
            m = _UNIT_RE.match(self.source, self.pos)
            if m:
                unit = m.group(1)
                self.pos += len(unit)
        return "".join(num), unit

    def _read_ident(self) -> str:
        start = self.pos
        while self.pos < len(self.source) and (self._peek().isalnum() or self._peek() in "_-"):
            self._advance()
        return self.source[start:self.pos]

    def tokenize(self) -> list[Token]:
        self.tokens = []
        self.pos = 0
        self.line = 1
        self.col = 1

        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()

            if self.pos >= len(self.source):
                break

            ch = self._peek()

            if ch == "-" and self._peek(1) == "-":
                prefix = "--"
                self._advance()
                self._advance()
                name = self._read_ident()
                self._emit(TokenType.IDENTIFIER, prefix + name)
                continue

            if ch == "@" and self._peek(1).isalpha():
                self._advance()
                ident = self._read_ident()
                self._emit(TokenType.AT, ident)
                continue

            if ch == "$":
                self._advance()
                ident = self._read_ident()
                if not ident:
                    self._error("Expected variable name after $")
                self._emit(TokenType.VARIABLE, ident)
                continue

            if ch == "." and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == "(":
                self._advance()
                self._emit(TokenType.DOT)
                continue

            if ch == "#":
                self._advance()
                hex_chars = []
                while self.pos < len(self.source) and self._peek() in "0123456789abcdefABCDEF":
                    hex_chars.append(self._advance())
                nxt = self._peek()
                if len(hex_chars) in (3, 4, 6, 8) and (not nxt or not nxt.isalnum() or nxt in ";})"):
                    self._emit(TokenType.COLOR_HEX, "".join(hex_chars))
                else:
                    for _ in hex_chars:
                        self.pos -= 1
                        self.col -= 1
                    self._emit(TokenType.HASH)
                continue

            if ch in "\"'":
                self._advance()
                val = self._read_string(ch)
                self._emit(TokenType.STRING, val)
                continue

            num, unit = self._read_number()
            if num and (num != "-" and num != "+"):
                if unit:
                    self._emit(TokenType.DIMENSION, f"{num}{unit}")
                else:
                    self._emit(TokenType.NUMBER, num)
                continue

            if ch.isalpha() or ch == "_" or ch == "-":
                ident = self._read_ident()
                kw_type = KEYWORDS.get(ident)
                if kw_type:
                    self._emit(kw_type)
                else:
                    if ident == "and" or ident == "or" or ident == "not":
                        self._emit(TokenType.IDENTIFIER, ident)
                    else:
                        self._emit(TokenType.IDENTIFIER, ident)
                continue

            multi_map = {
                ("=", "="): TokenType.EQUALS,
                ("!", "="): TokenType.NOT_EQUALS,
                (">", "="): TokenType.GREATER_EQUAL,
                ("<", "="): TokenType.LESS_EQUAL,
            }

            pair = (ch, self._peek(1))
            if pair in multi_map:
                self._advance()
                self._advance()
                self._emit(multi_map[pair])
                continue

            punct_map = {
                "{": TokenType.LBRACE,
                "}": TokenType.RBRACE,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                ":": TokenType.COLON,
                ";": TokenType.SEMICOLON,
                ",": TokenType.COMMA,
                ".": TokenType.DOT,
                "&": TokenType.AMPERSAND,
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "=": TokenType.ASSIGN,
                ">": TokenType.GREATER,
                "<": TokenType.LESS,
                "[": TokenType.LBRACKET,
                "]": TokenType.RBRACKET,
                "|": TokenType.PIPE,
                "#": TokenType.HASH,
                "!": TokenType.BANG,
            }

            if ch in punct_map:
                self._advance()
                self._emit(punct_map[ch])
                continue

            self._error(f"Unexpected character: {ch!r}")

        self._emit(TokenType.EOF)
        return self.tokens
