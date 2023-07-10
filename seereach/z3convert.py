"""Infrastructure to use Z3 in the symbolic execution engine"""
from typing import Any, Dict, List
from seereach.lang import Name, Operator, Type
from seereach.result import EvalResult
from seereach.symlang import (
    SBinaryOp,
    SUnaryOp,
    SVariable,
    SymLang,
    SBoolean,
    SReal,
    SInteger,
    STuple,
)
from z3 import *


class Z3SatConverter:
    def __init__(self):
        self.variables: Dict[Name, Any] = {}
        self.conditions: List[Any] = []

    def add_condition(self, condition: SymLang):
        # add any unknown variables to the variable map
        self.collect_variables(condition)

        # convert the condition to a z3 expression
        self.conditions.append(self.convert(condition))

        return self

    def add_result(self, result: EvalResult):
        for condition in result.path_condition:
            self.add_condition(condition)
        return self

    def sat(self):
        s = z3.Solver()
        for condition in self.conditions:
            s.add(condition)
        return s.check()

    @property
    def is_sat(self):
        return self.sat() == z3.sat

    @property
    def is_unsat(self):
        return z3.solve(*self.conditions) == z3.unsat

    def collect_variables(self, expr: SymLang):
        if isinstance(expr, SVariable):
            if expr.name not in self.variables:
                if expr.variable_type == Type.REAL:
                    self.variables[expr.name] = z3.Real(expr.name)
                elif expr.variable_type == Type.INTEGER:
                    self.variables[expr.name] = z3.Int(expr.name)
                elif expr.variable_type == Type.BOOLEAN:
                    self.variables[expr.name] = z3.Bool(expr.name)
                elif expr.variable_type == Type.TUPLE:
                    self.variables[expr.name] = z3.Tuple(
                        *[self.collect_variables(e) for e in expr.elements]
                    )
        elif isinstance(expr, SBinaryOp):
            self.collect_variables(expr.left)
            self.collect_variables(expr.right)
        elif isinstance(expr, SUnaryOp):
            return self.collect_variables(expr.expression)
        else:
            return None

    def convert(self, expr: SymLang):
        if isinstance(expr, SVariable):
            return self.variables[expr.name]
        elif isinstance(expr, SBinaryOp):
            if expr.operator == Operator.ADD:
                return self.convert(expr.left) + self.convert(expr.right)
            elif expr.operator == Operator.SUB:
                return self.convert(expr.left) - self.convert(expr.right)
            elif expr.operator == Operator.MUL:
                return self.convert(expr.left) * self.convert(expr.right)
            elif expr.operator == Operator.DIV:
                return self.convert(expr.left) / self.convert(expr.right)
            elif expr.operator == Operator.EQUAL:
                return self.convert(expr.left) == self.convert(expr.right)
            elif expr.operator == Operator.LESS:
                return self.convert(expr.left) < self.convert(expr.right)
            elif expr.operator == Operator.LESS_EQUAL:
                return self.convert(expr.left) <= self.convert(expr.right)
            elif expr.operator == Operator.GREATER:
                return self.convert(expr.left) > self.convert(expr.right)
            elif expr.operator == Operator.GREATER_EQUAL:
                return self.convert(expr.left) >= self.convert(expr.right)
            elif expr.operator == Operator.AND:
                return z3.And(self.convert(expr.left), self.convert(expr.right))
            elif expr.operator == Operator.OR:
                return z3.Or(self.convert(expr.left), self.convert(expr.right))
            else:
                raise ValueError(f"Invalid operator: {expr.operator}")
        elif isinstance(expr, SUnaryOp):
            if expr.operator == Operator.NOT:
                return z3.Not(self.convert(expr.expression))
            else:
                raise ValueError(f"Invalid operator: {expr.operator}")
        elif isinstance(expr, SReal):
            return expr.value
        elif isinstance(expr, SInteger):
            return expr.value
        elif isinstance(expr, SBoolean):
            return expr.value
        elif isinstance(expr, STuple):
            return z3.Tuple(*[self.convert(e) for e in expr.elements])
        return expr
