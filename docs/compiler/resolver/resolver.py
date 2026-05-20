from __future__ import annotations
from adar.parser.ast import (
    Node, Stylesheet, Selector, VariableAssign, Rule, MixinDef,
    ThemeDef, FunctionDef, ReturnStmt, Property, MixinInclude,
    MediaQuery, Identifier, Number, Dimension, ColorHex, StringVal,
    Variable, BinaryOp, FunctionCall, ValueList, ValueExpr, ImportStmt,
    IfStmt, UnaryOp,
)


class Resolver:
    def __init__(self) -> None:
        self._variables: dict[str, list[tuple[str, ValueExpr]]] = {}
        self._mixins: dict[str, MixinDef] = {}
        self._functions: dict[str, FunctionDef] = {}
        self._theme: str | None = None

    def resolve(self, stylesheet: Stylesheet) -> Stylesheet:
        self._variables = {}
        self._mixins = {}
        self._functions = {}
        self._theme = None
        new_children: list[Node] = []
        for child in stylesheet.children:
            resolved = self._resolve_top_level(child)
            if isinstance(resolved, list):
                new_children.extend(resolved)
            elif resolved is not None:
                new_children.append(resolved)
        return Stylesheet(new_children)

    def _resolve_top_level(self, node: Node) -> Node | list[Node] | None:
        if isinstance(node, VariableAssign):
            self._declare_variable(node.name, "root", node.value)
            return node
        if isinstance(node, MixinDef):
            self._mixins[node.name] = node
            return node
        if isinstance(node, ThemeDef):
            return self._resolve_theme(node)
        if isinstance(node, FunctionDef):
            self._functions[node.name] = node
            return node
        if isinstance(node, Rule):
            return self._resolve_rule(node)
        if isinstance(node, MediaQuery):
            return self._resolve_media_query(node)
        if isinstance(node, ImportStmt):
            return node
        return node

    def _declare_variable(self, name: str, scope: str, value: ValueExpr) -> None:
        if name not in self._variables:
            self._variables[name] = []
        self._variables[name].append((scope, value))

    def _resolve_variable(self, name: str) -> ValueExpr | None:
        scoped = self._variables.get(name)
        if not scoped:
            return None
        return scoped[-1][1]

    def _resolve_theme(self, node: ThemeDef) -> Node | list[Node]:
        old_theme = self._theme
        self._theme = node.name
        new_children: list[Node] = []
        for child in node.children:
            if isinstance(child, VariableAssign):
                self._declare_variable(child.name, f"theme:{node.name}", child.value)
                new_children.append(child)
            else:
                resolved = self._resolve_block(child)
                if isinstance(resolved, list):
                    new_children.extend(resolved)
                elif resolved is not None:
                    new_children.append(resolved)
        self._theme = old_theme
        return ThemeDef(node.name, new_children)

    def _resolve_rule(self, node: Rule) -> Rule:
        new_children = self._resolve_block(node.children)
        return Rule(node.selectors, new_children)

    def _resolve_block(self, children: list[Node]) -> list[Node]:
        new_children: list[Node] = []
        for child in children:
            resolved = self._resolve_stmt(child)
            if isinstance(resolved, list):
                new_children.extend(resolved)
            elif resolved is not None:
                new_children.append(resolved)
        return new_children

    def _resolve_stmt(self, node: Node) -> Node | list[Node] | None:
        if isinstance(node, VariableAssign):
            self._declare_variable(node.name, self._theme or "block", node.value)
            return None
        if isinstance(node, Property):
            return Property(node.name, self._resolve_value(node.value))
        if isinstance(node, IfStmt):
            return IfStmt(
                self._resolve_value(node.condition),
                self._resolve_block(node.then_body),
                self._resolve_block(node.else_body),
            )
        if isinstance(node, MixinInclude):
            mixin = self._mixins.get(node.name)
            if mixin:
                return self._resolve_block(mixin.children)
            return node
        if isinstance(node, Rule):
            return self._resolve_rule(node)
        if isinstance(node, MediaQuery):
            return self._resolve_media_query(node)
        if isinstance(node, ReturnStmt):
            return ReturnStmt(self._resolve_value(node.value))
        return node

    def _resolve_media_query(self, node: MediaQuery) -> MediaQuery:
        new_children = self._resolve_block(node.children)
        return MediaQuery(node.condition, new_children)

    def _resolve_value(self, value: ValueExpr) -> ValueExpr:
        if isinstance(value, FunctionCall):
            return FunctionCall(
                value.name,
                [self._resolve_value(a) for a in value.args],
            )
        if isinstance(value, BinaryOp):
            return BinaryOp(
                value.op,
                self._resolve_value(value.left),
                self._resolve_value(value.right),
            )
        if isinstance(value, UnaryOp):
            return UnaryOp(value.op, self._resolve_value(value.operand))
        if isinstance(value, ValueList):
            return ValueList([self._resolve_value(v) for v in value.values])
        return value
