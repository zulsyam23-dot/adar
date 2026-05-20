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
            return node
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
                # Bind parameters to arguments
                # Note: we use CSS variables for these, so we emit them as VariableAssign
                # which will be turned into CSS variables by codegen.
                # However, if we want compile-time substitution, we should bind them here.
                # The documentation says "Parameters become var(--name)", which means
                # they are intended to be CSS variables.
                # But if we pass arguments, we should probably emit VariableAssign nodes
                # at the beginning of the included block.
                
                new_stmts: list[Node] = []
                for param, arg in zip(mixin.params, node.args):
                    new_stmts.append(VariableAssign(param, arg))
                
                new_stmts.extend(mixin.children)
                return self._resolve_block(new_stmts)
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
            fn = self._functions.get(value.name)
            if fn:
                # Simple function evaluation by substitution
                # Bind params to args
                bindings = {}
                for param, arg in zip(fn.params, value.args):
                    bindings[param] = self._resolve_value(arg)
                
                # Find ReturnStmt
                for child in fn.children:
                    if isinstance(child, ReturnStmt):
                        return self._substitute_variables(child.value, bindings)
            
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

    def _substitute_variables(self, expr: ValueExpr, bindings: dict[str, ValueExpr]) -> ValueExpr:
        if isinstance(expr, Variable):
            return bindings.get(expr.name, expr)
        if isinstance(expr, BinaryOp):
            return BinaryOp(
                expr.op,
                self._substitute_variables(expr.left, bindings),
                self._substitute_variables(expr.right, bindings),
            )
        if isinstance(expr, UnaryOp):
            return UnaryOp(expr.op, self._substitute_variables(expr.operand, bindings))
        if isinstance(expr, FunctionCall):
            return FunctionCall(
                expr.name,
                [self._substitute_variables(a, bindings) for a in expr.args],
            )
        if isinstance(expr, ValueList):
            return ValueList([self._substitute_variables(v, bindings) for v in expr.values])
        return expr
