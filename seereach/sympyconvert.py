"""SymPy interface for SeeReach"""
from seereach.lang import Type, Value
from seereach.symlang import (
    STuple,
    SVariable,
    SInteger,
    SReal,
    SBoolean,
    SBinaryOp,
    SUnaryOp,
    Operator,
    Name,
    SymLang,
)
from sympy import (
    symbols,
    simplify,
    sin,
    cos,
    tan,
    sqrt,
    pi,
    E,
    log,
    Eq,
    Lt,
    Le,
    Gt,
    Ge,
    And,
    Or,
    Not,
)
from sympy.core.symbol import Symbol
import sympy


class SymPyConverter:
    def from_sympy(self, expr: sympy.Expr) -> SymLang:
        """
        Convert a sympy expression to a SymLang expression.
        """
        if isinstance(expr, Symbol):
            return SVariable(
                Name(str(expr)), Type.REAL if expr.is_real else Type.INTEGER
            )
        elif isinstance(expr, sympy.core.numbers.Integer):
            return SInteger(int(expr))
        elif isinstance(expr, sympy.core.numbers.Float):
            return SReal(float(expr))
        elif isinstance(expr, sympy.logic.boolalg.BooleanTrue):
            return SBoolean(True)
        elif isinstance(expr, sympy.logic.boolalg.BooleanFalse):
            return SBoolean(False)
        elif isinstance(expr, sympy.Add):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.ADD,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, sympy.Mul):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.MUL,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, sympy.Pow):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.POW,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, Eq):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.EQUAL,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, Lt):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.LESS,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, Le):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.LESS_EQUAL,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, Gt):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.GREATER,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, Ge):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.GREATER_EQUAL,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, And):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.AND,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, Or):
            return SBinaryOp(
                self.from_sympy(expr.args[0]),
                Operator.OR,
                self.from_sympy(expr.args[1]),
            )
        elif isinstance(expr, Not):
            return SUnaryOp(Operator.NOT, self.from_sympy(expr.args[0]))
        elif isinstance(expr, sin):
            return SUnaryOp(Operator.SIN, self.from_sympy(expr.args[0]))
        else:
            raise ValueError(f"Cannot convert {type(expr)} from sympy")

    def to_sympy(self, expr: SymLang):
        """
        Convert a SymLang expression to a sympy expression.
        """
        if isinstance(expr, SVariable):
            return symbols(str(expr.name))
        elif isinstance(expr, Value):
            return expr.value
        elif isinstance(expr, SInteger):
            return sympy.core.numbers.Integer(expr.value)
        elif isinstance(expr, SReal):
            return sympy.core.numbers.Float(expr.value)
        elif isinstance(expr, SBoolean):
            return (
                sympy.logic.boolalg.BooleanTrue()
                if expr.value
                else sympy.logic.boolalg.BooleanFalse()
            )
        elif isinstance(expr, SBinaryOp):
            operator_func = {
                Operator.ADD: lambda x, y: x + y,
                Operator.SUB: lambda x, y: x - y,
                Operator.MUL: lambda x, y: x * y,
                Operator.DIV: lambda x, y: x / y,
                Operator.POW: lambda x, y: x**y,
                Operator.EQUAL: lambda x, y: Eq(x, y),
                Operator.LESS: lambda x, y: Lt(x, y),
                Operator.LESS_EQUAL: lambda x, y: Le(x, y),
                Operator.GREATER: lambda x, y: Gt(x, y),
                Operator.GREATER_EQUAL: lambda x, y: Ge(x, y),
                Operator.AND: lambda x, y: And(x, y),
                Operator.OR: lambda x, y: Or(x, y),
            }[expr.operator]
            return operator_func(self.to_sympy(expr.left), self.to_sympy(expr.right))
        elif isinstance(expr, SUnaryOp):
            operator_func = {
                Operator.NOT: lambda x: Not(x),
                Operator.SIN: lambda x: sin(x),
            }[expr.operator]
            return operator_func(self.to_sympy(expr.expression))
        else:
            raise ValueError(f"Cannot convert {type(expr)} to sympy")

    def simplify(self, expr: SymLang):
        """applies simplification to a SymLang expression"""
        if isinstance(expr, STuple):
            return STuple([self.simplify(e) for e in expr.elements])
        else:
            return self.from_sympy(simplify(self.to_sympy(expr)))

    def latex(self, expr: SymLang):
        """returns a latex representation of a SymLang expression"""
        if isinstance(expr, STuple):
            return sympy.latex(sympy.Matrix([self.to_sympy(e) for e in expr.elements]))
        else:
            return sympy.latex(self.to_sympy(expr))
