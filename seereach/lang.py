"""The SEE-Reach High Level Compilation Language"""
from typing import List, Dict, Tuple, Union
from enum import Enum


class HLLang:
    """HL Language Base Class"""

    pass


class Name(str, HLLang):
    def __repr__(self) -> str:
        return f"Name({super().__repr__()})"


class Operator(
    Enum,
):
    ADD = "Add"
    SUB = "Sub"
    MUL = "Mul"
    DIV = "Div"
    GREATER = "Greater"
    LESS = "Less"
    GREATER_EQUAL = "GreaterEqual"
    LESS_EQUAL = "LessEqual"
    EQUAL = "Equal"
    AND = "And"
    OR = "Or"
    NOT = "Not"
    SIN = "Sin"


class Type(Enum):
    REAL = "Real"
    INTEGER = "Integer"
    BOOLEAN = "Boolean"
    TUPLE = "Tuple"


class Value:
    def __init__(self, value_type: Type, value: Union[float, int, bool, Tuple]):
        self.type = value_type
        self.value = value

    def __repr__(self) -> str:
        return f"{self.value}"


class Expression:
    pass


class Variable(Expression):
    def __init__(self, name: Name):
        self.name = name

    def __repr__(self) -> str:
        return f"Variable({self.name})"


class Literal(Expression):
    def __init__(self, value: Value):
        self.value = value

    def __repr__(self) -> str:
        return f"Literal({self.value})"


class BinaryOp(Expression):
    def __init__(self, left: Expression, operator: Operator, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"BinaryOp({self.left}, {self.operator}, {self.right})"


class UnaryOp(Expression):
    def __init__(self, operator: Operator, expression: Expression):
        self.operator = operator
        self.expression = expression

    def __repr__(self) -> str:
        return f"UnaryOp({self.operator}, {self.expression})"


class FunctionCall(Expression):
    def __init__(self, function_name: Name, arguments: List[Expression]):
        self.function_name = function_name
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"FunctionCall({self.function_name}, {self.arguments})"


class Conditional(Expression):
    def __init__(
        self, condition: Expression, true_branch: Expression, false_branch: Expression
    ):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __repr__(self) -> str:
        return f"Conditional({self.condition}, {self.true_branch}, {self.false_branch})"


class Block(Expression):
    def __init__(self, expressions: List[Expression]):
        self.expressions = expressions

    def __repr__(self) -> str:
        return f"Block({self.expressions})"


class TupleExpression(Expression):
    def __init__(self, elements: List[Expression]):
        self.elements = elements

    def __repr__(self) -> str:
        return f"Tuple{self.elements})"


class Assignment(Expression):
    def __init__(self, variable: "TypedVariable", expression: Expression):
        self.variable = variable
        self.expression = expression

    def __repr__(self) -> str:
        return f"Assignment({self.variable}, {self.expression})"


class Return(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __repr__(self) -> str:
        return f"Return({self.expression})"


class TypedVariable:
    def __init__(self, name: Name, variable_type: Type):
        self.name = name
        self.variable_type = variable_type

    def __repr__(self) -> str:
        return f"TypedVariable({self.name}, {self.variable_type})"


class Symbolic:
    def __init__(self, name: str, variable_type: Type):
        self.name = name
        self.variable_type = variable_type

    def __repr__(self):
        return f"Symbolic({self.name}, {self.variable_type})"


class Function:
    def __init__(
        self,
        name: Name,
        parameters: List[TypedVariable],
        return_type: Type,
        body: Expression,
    ):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class Program:
    def __init__(self, functions: Dict[Name, Function], start: Name):
        self.functions = functions
        self.start = start
