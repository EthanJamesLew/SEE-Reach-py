"""Symbolic Expression Language for SEE-Reach

This is what the executor compiles *to* and the HL target language is what the executor compiles *from*.
"""

from typing import List, Union
from seereach.lang import Name, Operator, Expression


class SymLang:
    pass


class SReal(SymLang):
    def __init__(self, value: float):
        self.value = value

    def __repr__(self) -> str:
        return f"SReal({self.value})"


class SInteger(SymLang):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"SInteger({self.value})"


class SBoolean(SymLang):
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self) -> str:
        return f"SBoolean({self.value})"


class SVariable(SymLang):
    def __init__(self, name: Name, variable_type):
        self.name = name
        self.value = self
        self.variable_type = variable_type

    def __repr__(self) -> str:
        return f"SVariable({self.name})"


class STuple(SymLang):
    def __init__(self, elements: List[SymLang]):
        self.elements = elements

    def __repr__(self) -> str:
        return f"STuple({self.elements})"


class SBinaryOp(SymLang):
    def __init__(self, left: SymLang, operator: Operator, right: SymLang):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        # infix print
        # lookup operator symbol
        operator_symbol = {
            Operator.ADD: "+",
            Operator.SUB: "-",
            Operator.MUL: "*",
            Operator.DIV: "/",
            Operator.EQUAL: "==",
            Operator.LESS: "<",
            Operator.LESS_EQUAL: "<=",
            Operator.GREATER: ">",
            Operator.GREATER_EQUAL: ">=",
            Operator.AND: "&&",
            Operator.OR: "||",
        }.get(self.operator, self.operator)
        return f"({self.left} {operator_symbol} {self.right})"


class SUnaryOp(SymLang):
    def __init__(self, operator: Operator, expression: SymLang):
        self.operator = operator
        self.expression = expression

    def __repr__(self) -> str:
        return f"SUnaryOp({self.operator}, {self.expression})"


class SymbolicBool(SymLang):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __repr__(self) -> str:
        return f"SymbolicBool({self.expression})"
