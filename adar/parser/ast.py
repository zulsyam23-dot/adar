from __future__ import annotations
from typing import Any


class Node:
    def __init__(self) -> None:
        self.loc: Any = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def _repr(self, **kwargs: str) -> str:
        fields = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        return f"{type(self).__name__}({fields})"


class Selector(Node):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return self._repr(value=self.value)


class Stylesheet(Node):
    def __init__(self, children: list[Node]) -> None:
        super().__init__()
        self.children = children

    def __repr__(self) -> str:
        return self._repr(children=f"[{len(self.children)} nodes]")


class VariableAssign(Node):
    def __init__(self, name: str, value: ValueExpr) -> None:
        super().__init__()
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return self._repr(name=f"${self.name}", value=str(self.value))


class Rule(Node):
    def __init__(self, selectors: list[Selector], children: list[Node]) -> None:
        super().__init__()
        self.selectors = selectors
        self.children = children

    def __repr__(self) -> str:
        sels = ", ".join(s.value for s in self.selectors)
        return self._repr(selectors=sels, children=f"[{len(self.children)} nodes]")


class MixinDef(Node):
    def __init__(self, name: str, params: list[str], children: list[Node]) -> None:
        super().__init__()
        self.name = name
        self.params = params
        self.children = children

    def __repr__(self) -> str:
        return self._repr(name=self.name, params=str(self.params))


class ThemeDef(Node):
    def __init__(self, name: str, children: list[Node]) -> None:
        super().__init__()
        self.name = name
        self.children = children

    def __repr__(self) -> str:
        return self._repr(name=self.name)


class FunctionDef(Node):
    def __init__(self, name: str, params: list[str], children: list[Node]) -> None:
        super().__init__()
        self.name = name
        self.params = params
        self.children = children

    def __repr__(self) -> str:
        return self._repr(name=self.name, params=str(self.params))


class ReturnStmt(Node):
    def __init__(self, value: ValueExpr) -> None:
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return self._repr(value=str(self.value))


class ImportStmt(Node):
    def __init__(self, path: str) -> None:
        super().__init__()
        self.path = path

    def __repr__(self) -> str:
        return self._repr(path=self.path)


class Property(Node):
    def __init__(self, name: str, value: ValueExpr) -> None:
        super().__init__()
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return self._repr(name=self.name, value=str(self.value))


class MixinInclude(Node):
    def __init__(self, name: str, args: list[ValueExpr] | None = None) -> None:
        super().__init__()
        self.name = name
        self.args = args or []

    def __repr__(self) -> str:
        return self._repr(name=self.name, args=str(self.args))


class MediaQuery(Node):
    def __init__(self, condition: str, children: list[Node]) -> None:
        super().__init__()
        self.condition = condition
        self.children = children

    def __repr__(self) -> str:
        return self._repr(condition=self.condition)


class ValueExpr(Node):
    pass


class Identifier(ValueExpr):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def __repr__(self) -> str:
        return self._repr(name=self.name)


class Number(ValueExpr):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return self._repr(value=self.value)


class Dimension(ValueExpr):
    def __init__(self, value: str, unit: str) -> None:
        super().__init__()
        self.value = value
        self.unit = unit

    def __repr__(self) -> str:
        return self._repr(value=self.value, unit=self.unit)


class ColorHex(ValueExpr):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return self._repr(value=f"#{self.value}")


class StringVal(ValueExpr):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return self._repr(value=self.value)


class Variable(ValueExpr):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def __repr__(self) -> str:
        return self._repr(name=f"${self.name}")


class BinaryOp(ValueExpr):
    def __init__(self, op: str, left: ValueExpr, right: ValueExpr) -> None:
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return self._repr(op=self.op, left=str(self.left), right=str(self.right))


class FunctionCall(ValueExpr):
    def __init__(self, name: str, args: list[ValueExpr]) -> None:
        super().__init__()
        self.name = name
        self.args = args

    def __repr__(self) -> str:
        return self._repr(name=self.name, args=str(self.args))


class ValueList(ValueExpr):
    def __init__(self, values: list[ValueExpr]) -> None:
        super().__init__()
        self.values = values

    def __repr__(self) -> str:
        return self._repr(values=str(self.values))


class IfStmt(Node):
    def __init__(self, condition: ValueExpr, then_body: list[Node],
                 else_body: list[Node] | None = None) -> None:
        super().__init__()
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body or []

    def __repr__(self) -> str:
        return self._repr(condition=str(self.condition),
                          then=f"[{len(self.then_body)}]",
                          else_=f"[{len(self.else_body)}]")


class UnaryOp(ValueExpr):
    def __init__(self, op: str, operand: ValueExpr) -> None:
        super().__init__()
        self.op = op
        self.operand = operand

    def __repr__(self) -> str:
        return self._repr(op=self.op, operand=str(self.operand))
