from __future__ import annotations
from adar.lexer.token import Token, TokenType
from adar.parser.ast import (
    Node, Stylesheet, Selector, VariableAssign, Rule, MixinDef,
    ThemeDef, FunctionDef, ReturnStmt, ImportStmt, Property,
    MixinInclude, MediaQuery, Identifier, Number, Dimension,
    ColorHex, StringVal, Variable, BinaryOp, FunctionCall, ValueList,
    ValueExpr, IfStmt, UnaryOp,
)


_BINARY_OPS = {
    TokenType.PLUS: "+",
    TokenType.MINUS: "-",
    TokenType.STAR: "*",
    TokenType.SLASH: "/",
}


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def _advance(self) -> Token:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def _expect(self, *types: TokenType) -> Token:
        t = self._peek()
        if t.type not in types:
            got = t.type.name
            expected = ", ".join(tt.name for tt in types)
            raise SyntaxError(f"{t.location}: Expected {expected}, got {got} ({t.value!r})")
        return self._advance()

    def _skip_newlines(self) -> None:
        while self._peek().type == TokenType.NEWLINE:
            self._advance()

    def _check(self, *types: TokenType) -> bool:
        return self._peek().type in types

    def parse(self) -> Stylesheet:
        children: list[Node] = []
        self._skip_newlines()
        while self._peek().type != TokenType.EOF:
            stmt = self._parse_top_level()
            if stmt is not None:
                children.append(stmt)
            self._skip_newlines()
        return Stylesheet(children)

    def _parse_top_level(self) -> Node | None:
        tok = self._peek()

        if tok.type == TokenType.VARIABLE:
            return self._parse_variable_assign()

        if tok.type == TokenType.MIXIN:
            return self._parse_mixin_def()

        if tok.type == TokenType.IF:
            return self._parse_if_stmt()

        if tok.type == TokenType.THEME:
            return self._parse_theme_def()

        if tok.type == TokenType.FUNCTION:
            return self._parse_function_def()

        if tok.type == TokenType.IMPORT:
            return self._parse_import()

        if tok.type == TokenType.AT:
            return self._parse_at_rule()

        if tok.type in (TokenType.IDENTIFIER, TokenType.DOT, TokenType.AMPERSAND, TokenType.STAR):
            return self._parse_rule()

        if tok.type == TokenType.NEWLINE:
            self._advance()
            return None

        if tok.type == TokenType.EOF:
            return None

        raise SyntaxError(f"{tok.location}: Unexpected token {tok.type.name} ({tok.value!r})")

    def _parse_variable_assign(self) -> VariableAssign:
        var_tok = self._expect(TokenType.VARIABLE)
        if self._check(TokenType.COLON):
            self._advance()
        self._expect(TokenType.ASSIGN)
        value = self._parse_value_expr()
        self._skip_newlines()
        return VariableAssign(var_tok.value, value)

    def _parse_block_body(self) -> list[Node]:
        self._expect(TokenType.LBRACE)
        children: list[Node] = []
        self._skip_newlines()
        while self._peek().type not in (TokenType.RBRACE, TokenType.EOF):
            stmt = self._parse_block_stmt()
            if stmt is not None:
                children.append(stmt)
            self._skip_newlines()
        self._expect(TokenType.RBRACE)
        return children

    def _parse_block_stmt(self) -> Node | None:
        tok = self._peek()

        if tok.type == TokenType.VARIABLE:
            return self._parse_variable_assign()

        if tok.type == TokenType.RETURN:
            self._advance()
            val = self._parse_value_expr()
            return ReturnStmt(val)

        if tok.type == TokenType.INCLUDE:
            self._advance()
            name_tok = self._expect(TokenType.IDENTIFIER)
            args: list[ValueExpr] = []
            if self._peek().type == TokenType.LPAREN:
                self._advance()
                if self._peek().type != TokenType.RPAREN:
                    args.append(self._parse_value_expr())
                    while self._peek().type == TokenType.COMMA:
                        self._advance()
                        args.append(self._parse_value_expr())
                self._expect(TokenType.RPAREN)
            return MixinInclude(name_tok.value, args)

        if tok.type == TokenType.IF:
            return self._parse_if_stmt()

        if tok.type == TokenType.AT:
            return self._parse_at_rule()

        if tok.type in (TokenType.IDENTIFIER, TokenType.DOT, TokenType.AMPERSAND, TokenType.STAR,
                         TokenType.COLON, TokenType.LBRACKET, TokenType.PIPE):
            return self._parse_rule_or_property()

        if tok.type == TokenType.NEWLINE:
            self._advance()
            return None

        if tok.type == TokenType.EOF:
            return None

        raise SyntaxError(f"{tok.location}: Unexpected token in block: {tok.type.name} ({tok.value!r})")

    def _parse_rule_or_property(self) -> Node:
        if self._peek().type == TokenType.IDENTIFIER and self._peek(1).type == TokenType.COLON:
            save = self.pos
            try:
                prop = self._parse_property()
                if self._peek().type == TokenType.LBRACE:
                    self.pos = save
                    return self._parse_rule()
                return prop
            except SyntaxError:
                self.pos = save
                return self._parse_rule()
        return self._parse_rule()

    def _parse_rule(self) -> Rule:
        selectors = self._parse_selectors()
        self._skip_newlines()
        children = self._parse_block_body()
        return Rule(selectors, children)

    def _parse_selectors(self) -> list[Selector]:
        sels: list[Selector] = []
        raw = self._parse_selector_raw()
        sels.append(Selector(raw))
        while self._peek().type == TokenType.COMMA:
            self._advance()
            self._skip_newlines()
            raw = self._parse_selector_raw()
            sels.append(Selector(raw))
        return sels

    def _parse_selector_raw(self) -> str:
        parts: list[str] = []
        while self._peek().type not in (
            TokenType.LBRACE, TokenType.COMMA, TokenType.EOF, TokenType.NEWLINE,
        ):
            if self._peek().type == TokenType.AT:
                break
            tok = self._advance()
            if tok.type == TokenType.VARIABLE:
                parts.append(f"${tok.value}")
            elif tok.type == TokenType.AMPERSAND:
                parts.append("&")
            elif tok.type == TokenType.COLON:
                parts.append(":")
            elif tok.type == TokenType.DOT:
                parts.append(".")
            elif tok.type == TokenType.STAR:
                parts.append("*")
            elif tok.type == TokenType.GREATER:
                parts.append(">")
            elif tok.type == TokenType.PIPE:
                parts.append("|")
            elif tok.type == TokenType.IDENTIFIER:
                parts.append(tok.value)
            elif tok.type == TokenType.NUMBER:
                parts.append(tok.value)
            elif tok.type == TokenType.LPAREN:
                parts.append("(")
            elif tok.type == TokenType.RPAREN:
                parts.append(")")
            elif tok.type == TokenType.LBRACKET:
                parts.append("[")
            elif tok.type == TokenType.RBRACKET:
                parts.append("]")
            elif tok.type == TokenType.ASSIGN:
                parts.append("=")
            elif tok.type == TokenType.STRING:
                parts.append(f'"{tok.value}"')
            elif tok.type == TokenType.PLUS:
                parts.append("+")
            elif tok.type == TokenType.MINUS:
                parts.append("-")
            elif tok.type == TokenType.SLASH:
                parts.append("/")
            elif tok.type == TokenType.HASH:
                parts.append("#")
                if self._peek().type == TokenType.IDENTIFIER:
                    id_tok = self._advance()
                    parts.append(id_tok.value)
            elif tok.type == TokenType.COLOR_HEX:
                parts.append(f"#{tok.value}")
            elif tok.type in (TokenType.THEME, TokenType.MIXIN, TokenType.FUNCTION,
                               TokenType.INCLUDE, TokenType.RETURN, TokenType.IMPORT,
                               TokenType.IF, TokenType.ELSE, TokenType.TRUE, TokenType.FALSE):
                parts.append(tok.value)
            else:
                raise SyntaxError(f"{tok.location}: Unexpected token in selector: {tok.type.name} ({tok.value!r})")
        raw = "".join(parts).strip()
        if not raw:
            raise SyntaxError(f"{self._peek().location}: Empty selector")
        return raw

    def _parse_property(self) -> Property:
        name_tok = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.COLON)
        value = self._parse_value_expr()
        return Property(name_tok.value, value)

    def _parse_value_expr(self) -> ValueExpr:
        values: list[ValueExpr] = []
        values.append(self._parse_single_value())

        _STOP = {
            TokenType.RBRACE, TokenType.LBRACE, TokenType.SEMICOLON,
            TokenType.NEWLINE, TokenType.EOF, TokenType.RPAREN,
            TokenType.COLON,
        }

        while self._peek().type not in _STOP:
            if self._peek().type == TokenType.NEWLINE:
                break
            
            if self._peek().type == TokenType.COMMA:
                self._advance()
                # Represent comma as a special identifier for now or handle in ValueList
                values.append(Identifier(","))
                continue

            values.append(self._parse_single_value())

        if len(values) == 1:
            return values[0]
        return ValueList(values)

    def _parse_single_value(self) -> ValueExpr:
        left = self._parse_primary_expr()

        while self._peek().type in _BINARY_OPS:
            op_tok = self._advance()
            right = self._parse_primary_expr()
            left = BinaryOp(_BINARY_OPS[op_tok.type], left, right)

        return left

    def _parse_primary_expr(self) -> ValueExpr:
        tok = self._advance()

        if tok.type == TokenType.NUMBER:
            return Number(tok.value)

        if tok.type == TokenType.DIMENSION:
            val = tok.value
            for u in ("px", "rem", "em", "ex", "ch", "vh", "vw", "vmin", "vmax",
                       "cm", "mm", "in", "pt", "pc", "deg", "rad", "grad", "turn",
                       "s", "ms", "Hz", "kHz", "dpi", "dpcm", "dppx", "fr", "q", "%"):
                if val.endswith(u):
                    return Dimension(val[:-len(u)], u)
            return Dimension(tok.value, "")

        if tok.type == TokenType.COLOR_HEX:
            return ColorHex(tok.value)

        if tok.type == TokenType.HASH:
            if self._peek().type == TokenType.IDENTIFIER:
                id_tok = self._advance()
                return ColorHex(id_tok.value)
            raise SyntaxError(f"{tok.location}: Expected identifier after # in color value")

        if tok.type == TokenType.STRING:
            return StringVal(tok.value)

        if tok.type == TokenType.VARIABLE:
            return Variable(tok.value)

        if tok.type == TokenType.IDENTIFIER:
            if self._peek().type == TokenType.LPAREN:
                self._advance()
                args: list[ValueExpr] = []
                if self._peek().type != TokenType.RPAREN:
                    args.append(self._parse_value_expr())
                    while self._peek().type == TokenType.COMMA:
                        self._advance()
                        args.append(self._parse_value_expr())
                self._expect(TokenType.RPAREN)
                return FunctionCall(tok.value, args)
            return Identifier(tok.value)

        if tok.type == TokenType.TRUE:
            return Identifier("true")

        if tok.type == TokenType.FALSE:
            return Identifier("false")

        if tok.type == TokenType.MINUS:
            next_tok = self._peek()
            if next_tok.type in (TokenType.NUMBER, TokenType.DIMENSION):
                expr = self._parse_primary_expr()
                if isinstance(expr, Number):
                    expr.value = "-" + expr.value
                    return expr
                if isinstance(expr, Dimension):
                    expr.value = "-" + expr.value
                    return expr
            return BinaryOp("-", Number("0"), self._parse_primary_expr())

        if tok.type == TokenType.PLUS:
            return self._parse_primary_expr()

        if tok.type == TokenType.LPAREN:
            expr = self._parse_value_expr()
            self._expect(TokenType.RPAREN)
            return expr

        if tok.type == TokenType.DOT:
            if self._peek().type == TokenType.NUMBER:
                num_tok = self._advance()
                val = "." + num_tok.value
                self._peek()
                for u in ("px", "rem", "em", "ex", "ch", "vh", "vw", "vmin", "vmax",
                           "cm", "mm", "in", "pt", "pc", "deg", "rad", "grad", "turn",
                           "s", "ms", "Hz", "kHz", "dpi", "dpcm", "dppx", "fr", "q", "%"):
                    if val.endswith(u):
                        return Dimension(val[:-len(u)], u)
                return Number(val)

        raise SyntaxError(f"{tok.location}: Unexpected token in value: {tok.type.name} ({tok.value!r})")

    def _parse_mixin_def(self) -> MixinDef:
        self._expect(TokenType.MIXIN)
        name_tok = self._expect(TokenType.IDENTIFIER)
        params: list[str] = []
        if self._peek().type == TokenType.LPAREN:
            self._advance()
            if self._peek().type != TokenType.RPAREN:
                params.append(self._expect(TokenType.VARIABLE).value)
                while self._peek().type == TokenType.COMMA:
                    self._advance()
                    params.append(self._expect(TokenType.VARIABLE).value)
            self._expect(TokenType.RPAREN)
        self._skip_newlines()
        children = self._parse_block_body()
        return MixinDef(name_tok.value, params, children)

    def _parse_theme_def(self) -> ThemeDef:
        self._expect(TokenType.THEME)
        name_tok: Token = self._expect(TokenType.IDENTIFIER)
        self._skip_newlines()
        children = self._parse_block_body()
        return ThemeDef(name_tok.value, children)

    def _parse_function_def(self) -> FunctionDef:
        self._expect(TokenType.FUNCTION)
        name_tok = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.LPAREN)
        params: list[str] = []
        if self._peek().type != TokenType.RPAREN:
            params.append(self._expect(TokenType.VARIABLE).value)
            while self._peek().type == TokenType.COMMA:
                self._advance()
                params.append(self._expect(TokenType.VARIABLE).value)
        self._expect(TokenType.RPAREN)
        self._skip_newlines()
        children = self._parse_block_body()
        return FunctionDef(name_tok.value, params, children)

    def _parse_import(self) -> ImportStmt:
        self._expect(TokenType.IMPORT)
        path_tok = self._expect(TokenType.STRING)
        return ImportStmt(path_tok.value)

    def _parse_at_rule(self) -> MediaQuery:
        at_tok = self._advance()
        rest: list[str] = []
        if at_tok.value:
            rest.append(at_tok.value)
            rest.append(" ")
        while self._peek().type not in (TokenType.LBRACE, TokenType.NEWLINE, TokenType.EOF):
            tok = self._advance()
            if tok.type == TokenType.IDENTIFIER:
                rest.append(tok.value)
            elif tok.type == TokenType.LPAREN:
                rest.append("(")
            elif tok.type == TokenType.RPAREN:
                rest.append(")")
            elif tok.type == TokenType.COLON:
                rest.append(":")
            elif tok.type == TokenType.DOT:
                rest.append(".")
            elif tok.type == TokenType.NUMBER:
                rest.append(tok.value)
            elif tok.type == TokenType.DIMENSION:
                rest.append(tok.value)
            elif tok.type == TokenType.MINUS:
                rest.append("-")
            elif tok.type == TokenType.COMMA:
                rest.append(", ")
            else:
                rest.append(" ")
        condition = "".join(rest).strip()
        self._skip_newlines()
        children = self._parse_block_body()
        return MediaQuery(condition, children)

    def _parse_if_stmt(self) -> IfStmt:
        self._expect(TokenType.IF)
        condition = self._parse_condition()
        self._skip_newlines()
        then_body = self._parse_block_body()
        self._skip_newlines()
        else_body: list[Node] = []
        if self._peek().type == TokenType.ELSE:
            self._advance()
            self._skip_newlines()
            if self._peek().type == TokenType.IF:
                else_body = [self._parse_if_stmt()]
            else:
                else_body = self._parse_block_body()
        return IfStmt(condition, then_body, else_body)

    def _parse_condition(self) -> ValueExpr:
        return self._parse_or_expr()

    def _parse_or_expr(self) -> ValueExpr:
        left = self._parse_and_expr()
        while self._peek().type == TokenType.OR:
            self._advance()
            right = self._parse_and_expr()
            left = BinaryOp("or", left, right)
        return left

    def _parse_and_expr(self) -> ValueExpr:
        left = self._parse_not_expr()
        while self._peek().type == TokenType.AND:
            self._advance()
            right = self._parse_not_expr()
            left = BinaryOp("and", left, right)
        return left

    def _parse_not_expr(self) -> ValueExpr:
        if self._peek().type == TokenType.NOT:
            self._advance()
            return UnaryOp("not", self._parse_comparison())
        return self._parse_comparison()

    def _parse_comparison(self) -> ValueExpr:
        left = self._parse_single_value()
        _CMP = {
            TokenType.EQUALS: "==",
            TokenType.NOT_EQUALS: "!=",
            TokenType.LESS: "<",
            TokenType.GREATER: ">",
            TokenType.LESS_EQUAL: "<=",
            TokenType.GREATER_EQUAL: ">=",
        }
        if self._peek().type in _CMP:
            op_tok = self._advance()
            right = self._parse_single_value()
            return BinaryOp(_CMP[op_tok.type], left, right)
        return left
