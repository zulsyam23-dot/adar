from __future__ import annotations
from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    DIMENSION = auto()
    STRING = auto()
    COLOR_HEX = auto()
    IDENTIFIER = auto()
    VARIABLE = auto()
    THEME = auto()
    MIXIN = auto()
    FUNCTION = auto()
    INCLUDE = auto()
    RETURN = auto()
    IMPORT = auto()
    IF = auto()
    ELSE = auto()
    TRUE = auto()
    FALSE = auto()
    LBRACE = auto()
    RBRACE = auto()
    LPAREN = auto()
    RPAREN = auto()
    COLON = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    AMPERSAND = auto()
    AT = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    ASSIGN = auto()
    GREATER = auto()
    HASH = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    PIPE = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    BANG = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    NEWLINE = auto()
    EOF = auto()


KEYWORDS = {
    "theme": TokenType.THEME,
    "mixin": TokenType.MIXIN,
    "function": TokenType.FUNCTION,
    "include": TokenType.INCLUDE,
    "return": TokenType.RETURN,
    "import": TokenType.IMPORT,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}


class SourceLocation:
    __slots__ = ("line", "column", "source")

    def __init__(self, line: int, column: int, source: str = "") -> None:
        self.line = line
        self.column = column
        self.source = source

    def __repr__(self) -> str:
        src = f" in {self.source}" if self.source else ""
        return f"line {self.line}:{self.column}{src}"


class Token:
    __slots__ = ("type", "value", "location")

    def __init__(
        self, type_: TokenType, value: str = "", location: SourceLocation | None = None
    ) -> None:
        self.type = type_
        self.value = value
        self.location = location

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.location})"
