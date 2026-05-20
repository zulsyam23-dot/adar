from __future__ import annotations
import hashlib
import re
from pathlib import Path
from adar.parser.ast import VariableAssign
from adar.parser.ast import (
    Node, Stylesheet, Selector, VariableAssign, Rule, MixinDef,
    ThemeDef, FunctionDef, ReturnStmt, Property, MixinInclude,
    MediaQuery, Identifier, Number, Dimension, ColorHex, StringVal,
    Variable, BinaryOp, FunctionCall, ValueList, ValueExpr, ImportStmt,
    IfStmt, UnaryOp,
)

_RESET = "\x1b[0m"
_GREEN = "\x1b[32m"
_CYAN = "\x1b[36m"
_YELLOW = "\x1b[33m"
_RED = "\x1b[31m"


class CodeGenerator:
    def __init__(
        self, scoped: bool = True, pretty: bool = True,
        source_file: str = "",
    ) -> None:
        self.scoped = scoped
        self.pretty = pretty
        self._indent = 0
        self._lines: list[str] = []
        self._mapping: dict[str, str] = {}
        self._themes: list[ThemeDef] = []
        self._css_vars: dict[str, str] = {}
        self.source_file = source_file
        self._global_vars: list[VariableAssign] = []

    def generate(self, stylesheet: Stylesheet) -> str:
        self._lines = []
        self._mapping = {}
        self._themes = []
        self._css_vars = {}
        self._global_vars = []
        self._indent = 0

        self._collect_globals(stylesheet)
        self._emit_global_vars()

        for child in stylesheet.children:
            self._generate_node(child)

        return self._output()

    def _collect_globals(self, ss: Stylesheet) -> None:
        for child in ss.children:
            if isinstance(child, VariableAssign):
                self._global_vars.append(child)
            elif isinstance(child, ThemeDef):
                self._themes.append(child)

    def _emit_global_vars(self) -> None:
        if not self._global_vars:
            return
        self._writeln(":root {")
        self._indent += 1
        for var in self._global_vars:
            val_str = self._value_to_css(var.value)
            self._writeln(f"--{var.name}: {val_str};")
        self._indent -= 1
        self._writeln("}")
        self._writeln("")

        for theme in self._themes:
            attr = f"[data-theme=\"{theme.name}\"]"
            self._write(f"{attr} {{")
            self._indent += 1
            for child in theme.children:
                if isinstance(child, VariableAssign):
                    val_str = self._value_to_css(child.value)
                    self._writeln(f"--{child.name}: {val_str};")
            self._indent -= 1
            self._writeln("}")
            self._writeln("")

    def _generate_node(self, node: Node) -> None:
        if isinstance(node, Rule):
            self._generate_rule(node)
        elif isinstance(node, MixinDef):
            pass
        elif isinstance(node, FunctionDef):
            pass
        elif isinstance(node, ImportStmt):
            pass
        elif isinstance(node, MediaQuery):
            self._generate_media_query(node)
        elif isinstance(node, VariableAssign):
            pass
        elif isinstance(node, IfStmt):
            if self._eval_condition(node.condition):
                for c in node.then_body:
                    self._generate_node(c)
            else:
                for c in node.else_body:
                    self._generate_node(c)

    def _generate_rule(self, rule: Rule, parent_selector: str = "") -> None:
        for sel in rule.selectors:
            raw_sel = sel.value
            scoped_sel = self._scope_selector(raw_sel) if self.scoped else raw_sel

            if parent_selector and "&" not in scoped_sel:
                scoped_sel = f"& {scoped_sel}"

            self._write(f"{scoped_sel} {{")
            self._indent += 1
            for child in rule.children:
                self._generate_block_child(child, parent_selector or scoped_sel)
            self._indent -= 1
            self._writeln("}")

    def _generate_block_child(self, node: Node, parent_sel: str = "") -> None:
        if isinstance(node, Property):
            val_str = self._value_to_css(node.value)
            self._writeln(f"{node.name}: {val_str};")
        elif isinstance(node, Rule):
            self._generate_rule(node, parent_sel)
        elif isinstance(node, MediaQuery):
            self._generate_media_query(node, parent_sel)
        elif isinstance(node, IfStmt):
            if self._eval_condition(node.condition):
                for c in node.then_body:
                    self._generate_block_child(c, parent_sel)
            else:
                for c in node.else_body:
                    self._generate_block_child(c, parent_sel)
        elif isinstance(node, VariableAssign):
            val_str = self._value_to_css(node.value)
            self._writeln(f"--{node.name}: {val_str};")
        elif isinstance(node, MixinInclude):
            pass

    def _generate_media_query(self, mq: MediaQuery, parent_sel: str = "") -> None:
        self._write(f"@{mq.condition} {{")
        self._indent += 1
        for child in mq.children:
            self._generate_block_child(child, parent_sel)
        self._indent -= 1
        self._writeln("}")

    def _scope_selector(self, selector: str) -> str:
        if selector == "&":
            return "&"
        cls_match = re.search(r"\.[a-zA-Z_][a-zA-Z0-9_-]*", selector)
        if cls_match:
            cls = cls_match.group(0)
            clean = cls.lstrip(".")
            hash_str = hashlib.md5(clean.encode()).hexdigest()[:6]
            scoped_cls = f".{clean}__{hash_str}"
            scoped = selector.replace(cls, scoped_cls, 1)
            self._mapping[cls] = scoped_cls
            return scoped
        return selector

    def _eval_condition(self, expr: ValueExpr) -> bool:
        if isinstance(expr, Identifier):
            return expr.name == "true"
        if isinstance(expr, Number):
            return expr.value not in ("0", "0.0", "")
        if isinstance(expr, StringVal):
            return expr.value != ""
        if isinstance(expr, Variable):
            val = self._resolve_variable_raw(expr.name)
            if val is None:
                return True
            if isinstance(val, Identifier):
                return val.name == "true"
            if isinstance(val, StringVal):
                return val.value != ""
            if isinstance(val, Number):
                return val.value not in ("0", "0.0", "")
            return True
        if isinstance(expr, UnaryOp) and expr.op == "not":
            return not self._eval_condition(expr.operand)
        if isinstance(expr, BinaryOp):
            if expr.op == "and":
                return self._eval_condition(expr.left) and self._eval_condition(expr.right)
            if expr.op == "or":
                return self._eval_condition(expr.left) or self._eval_condition(expr.right)
            left_val = self._eval_to_raw(expr.left)
            right_val = self._eval_to_raw(expr.right)
            if expr.op == "==":
                return left_val == right_val
            if expr.op == "!=":
                return left_val != right_val
            try:
                ln = float(left_val)
                rn = float(right_val)
                if expr.op == ">": return ln > rn
                if expr.op == "<": return ln < rn
                if expr.op == ">=": return ln >= rn
                if expr.op == "<=": return ln <= rn
            except (ValueError, TypeError):
                pass
        return True

    def _resolve_variable_raw(self, name: str) -> ValueExpr | None:
        for child in self._global_vars:
            if child.name == name:
                return child.value
        return None

    def _eval_to_raw(self, expr: ValueExpr) -> str:
        if isinstance(expr, Variable):
            val = self._resolve_variable_raw(expr.name)
            if val:
                return self._eval_to_raw(val)
            return ""
        if isinstance(expr, Identifier):
            return expr.name
        if isinstance(expr, StringVal):
            return expr.value
        if isinstance(expr, Number):
            return expr.value
        if isinstance(expr, Dimension):
            try:
                return str(float(expr.value))
            except ValueError:
                return expr.value
        return self._value_to_css(expr)

    def _value_to_css(self, value: ValueExpr) -> str:
        if isinstance(value, Number):
            return value.value
        if isinstance(value, Dimension):
            return f"{value.value}{value.unit}"
        if isinstance(value, ColorHex):
            return f"#{value.value}"
        if isinstance(value, StringVal):
            return f'"{value.value}"'
        if isinstance(value, Identifier):
            return value.name
        if isinstance(value, Variable):
            return f"var(--{value.name})"
        if isinstance(value, BinaryOp):
            left = self._value_to_css(value.left)
            right = self._value_to_css(value.right)
            if value.op in ("*", "/"):
                return f"calc({left} {value.op} {right})"
            if value.op in ("+", "-"):
                return f"calc({left} {value.op} {right})"
            return f"{left} {value.op} {right}"
        if isinstance(value, FunctionCall):
            args = ", ".join(self._value_to_css(a) for a in value.args)
            return f"{value.name}({args})"
        if isinstance(value, UnaryOp):
            return f"{value.op}({self._value_to_css(value.operand)})"
        if isinstance(value, ValueList):
            res = []
            for i, v in enumerate(value.values):
                css = self._value_to_css(v)
                if css == "," and res:
                    res[-1] = res[-1] + ","
                elif css == "!" and res:
                    # Don't add space before ! (e.g. color: white !important)
                    # But actually CSS allows space. However, let's join it with next if possible
                    # Or just don't add space between previous and !
                    res[-1] = res[-1] + " !"
                elif res and res[-1].endswith(" !"):
                    # Join ! with important
                    res[-1] = res[-1] + css
                else:
                    res.append(css)
            return " ".join(res)
        return ""

    def _write(self, text: str) -> None:
        indent = "  " * self._indent if self.pretty else ""
        self._lines.append(indent + text)

    def _writeln(self, text: str = "") -> None:
        indent = "  " * self._indent if self.pretty and text else ""
        if text:
            self._lines.append(indent + text)
        else:
            self._lines.append("")

    def _output(self) -> str:
        return "\n".join(self._lines) + "\n"

    @property
    def mapping(self) -> dict[str, str]:
        return dict(self._mapping)
