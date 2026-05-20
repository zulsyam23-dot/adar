from __future__ import annotations
from dataclasses import dataclass, field
from adar.checker.css_spec import CSSSpec, ValueType

_NUMERIC_TYPES = {
    ValueType.LENGTH, ValueType.PERCENTAGE, ValueType.ANGLE,
    ValueType.TIME, ValueType.FREQUENCY, ValueType.RESOLUTION,
}
from adar.parser.ast import (
    Node, Stylesheet, Selector, VariableAssign, Rule, MixinDef,
    ThemeDef, FunctionDef, ReturnStmt, Property, MixinInclude,
    MediaQuery, Identifier, Number, Dimension, ColorHex, StringVal,
    Variable, BinaryOp, FunctionCall, ValueList, ValueExpr, ImportStmt,
    IfStmt, UnaryOp,
)


@dataclass
class AdarError:
    message: str
    node: Node | None = None
    location: str = ""

    def __repr__(self) -> str:
        loc = f" [{self.location}]" if self.location else ""
        return f"Error{loc}: {self.message}"


@dataclass
class CheckResult:
    errors: list[AdarError] = field(default_factory=list)
    warnings: list[AdarError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def merge(self, other: CheckResult) -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


class Checker:
    def __init__(self, spec: CSSSpec | None = None) -> None:
        self.spec = spec or CSSSpec()
        self.result = CheckResult()
        self._variables: dict[str, ValueExpr] = {}
        self._mixins: dict[str, MixinDef] = {}
        self._functions: dict[str, FunctionDef] = {}

    def check(self, stylesheet: Stylesheet) -> CheckResult:
        self.result = CheckResult()
        self._variables = {}
        self._mixins = {}
        self._functions = {}
        self._check_stylesheet(stylesheet)
        return self.result

    def _error(self, msg: str, node: Node | None = None) -> None:
        loc = getattr(node, "loc", None)
        loc_str = str(loc) if loc else ""
        self.result.errors.append(AdarError(msg, node, loc_str))

    def _warn(self, msg: str, node: Node | None = None) -> None:
        loc = getattr(node, "loc", None)
        loc_str = str(loc) if loc else ""
        self.result.warnings.append(AdarError(msg, node, loc_str))

    def _check_stylesheet(self, ss: Stylesheet) -> None:
        for child in ss.children:
            self._check_top_level(child)

    def _check_top_level(self, node: Node) -> None:
        if isinstance(node, VariableAssign):
            self._check_variable_assign(node)
        elif isinstance(node, MixinDef):
            self._mixins[node.name] = node
        elif isinstance(node, ThemeDef):
            self._check_theme(node)
        elif isinstance(node, FunctionDef):
            self._functions[node.name] = node
        elif isinstance(node, ImportStmt):
            pass
        elif isinstance(node, Rule):
            self._check_rule(node)
        elif isinstance(node, MediaQuery):
            self._check_block(node.children)
        elif isinstance(node, IfStmt):
            self._check_value(node.condition)
            for c in node.then_body:
                self._check_top_level(c)
            for c in node.else_body:
                self._check_top_level(c)
        else:
            self._error(f"Unexpected top-level statement: {type(node).__name__}", node)

    def _check_variable_assign(self, node: VariableAssign) -> None:
        self._check_value(node.value)
        self._variables[node.name] = node.value

    def _check_value(self, value: ValueExpr) -> ValueType | None:
        if isinstance(value, Identifier):
            return ValueType.IDENT
        if isinstance(value, Number):
            return ValueType.NUMBER
        if isinstance(value, Dimension):
            unit = value.unit
            if unit in ("px", "rem", "em", "ex", "ch", "cm", "mm", "in", "pt", "pc", "q", "vw", "vh", "vmin", "vmax"):
                return ValueType.LENGTH
            if unit == "%":
                return ValueType.PERCENTAGE
            if unit in ("deg", "rad", "grad", "turn"):
                return ValueType.ANGLE
            if unit in ("s", "ms"):
                return ValueType.TIME
            return ValueType.LENGTH
        if isinstance(value, ColorHex):
            return ValueType.COLOR
        if isinstance(value, StringVal):
            return ValueType.STRING
        if isinstance(value, Variable):
            resolved = self._variables.get(value.name)
            if resolved is None:
                self._error(f"Undefined variable: ${value.name}", value)
                return None
            return self._check_value(resolved)
        if isinstance(value, BinaryOp):
            left_type = self._check_value(value.left)
            right_type = self._check_value(value.right)
            if left_type is not None and right_type is not None and left_type != right_type:
                ok = (left_type in _NUMERIC_TYPES and right_type == ValueType.NUMBER) or \
                     (right_type in _NUMERIC_TYPES and left_type == ValueType.NUMBER)
                if not ok:
                    self._error(
                        f"Binary operation type mismatch: {left_type.name} {value.op} {right_type.name}",
                        value,
                    )
            return left_type or right_type
        if isinstance(value, FunctionCall):
            fn = self._functions.get(value.name)
            if fn is None:
                return ValueType.ANY
            if len(value.args) != len(fn.params):
                self._error(
                    f"Function '{value.name}()' expects {len(fn.params)} arguments, "
                    f"got {len(value.args)}",
                    value,
                )
            for arg in value.args:
                self._check_value(arg)
            return ValueType.ANY
        if isinstance(value, UnaryOp):
            return self._check_value(value.operand)
        if isinstance(value, ValueList):
            for v in value.values:
                self._check_value(v)
            return ValueType.ANY
        return None

    def _check_rule(self, rule: Rule) -> None:
        self._check_block(rule.children)

    def _check_block(self, children: list[Node]) -> None:
        for child in children:
            if isinstance(child, Property):
                self._check_property(child)
            elif isinstance(child, MixinInclude):
                if child.name not in self._mixins:
                    self._error(f"Undefined mixin: {child.name}", child)
            elif isinstance(child, Rule):
                self._check_rule(child)
            elif isinstance(child, MediaQuery):
                self._check_block(child.children)
            elif isinstance(child, VariableAssign):
                self._check_variable_assign(child)
            elif isinstance(child, ReturnStmt):
                self._check_value(child.value)
            elif isinstance(child, IfStmt):
                self._check_value(child.condition)
                self._check_block(child.then_body)
                self._check_block(child.else_body)
            else:
                self._error(f"Unexpected statement in block: {type(child).__name__}", child)

    def _check_property(self, prop: Property) -> None:
        value_type = self._check_value(prop.value)
        if value_type is not None:
            err = self.spec.validate_value(prop.name, value_type, str(prop.value))
            if err:
                self._error(err, prop)

    def _check_theme(self, theme: ThemeDef) -> None:
        self._check_block(theme.children)
