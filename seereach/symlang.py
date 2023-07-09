"""Symbolic language for SEE-Reach"""

from typing import List, Union
from seereach.lang import Name, Operator, Expression


class SymVal:
    pass

class SReal(SymVal):
    def __init__(self, value: float):
        self.value = value

    def __repr__(self) -> str:
        return f"SReal({self.value})"

class SInteger(SymVal):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"SInteger({self.value})"

class SBoolean(SymVal):
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self) -> str:
        return f"SBoolean({self.value})"

class SVariable(SymVal):
    def __init__(self, name: Name):
        self.name = name
        self.value = self

    def __repr__(self) -> str:
        return f"SVariable({self.name})"

class STuple(SymVal):
    def __init__(self, elements: List[SymVal]):
        self.elements = elements

    def __repr__(self) -> str:
        return f"STuple({self.elements})"

class SBinaryOp(SymVal):
    def __init__(self, left: SymVal, operator: Operator, right: SymVal):
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
        }[self.operator]
        return f"({self.left} {operator_symbol} {self.right})" 

class SUnaryOp(SymVal):
    def __init__(self, operator: Operator, expression: SymVal):
        self.operator = operator
        self.expression = expression

    def __repr__(self) -> str:
        return f"SUnaryOp({self.operator}, {self.expression})"

class SymbolicBool(SymVal):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __repr__(self) -> str:
        return f"SymbolicBool({self.expression})"
