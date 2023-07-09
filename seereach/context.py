"""Symbolic Contexts for SEE-Reach"""
from seereach.lang import *
from seereach.result import EvalResult
from seereach.symlang import *
from seereach.z3convert import Z3SatConverter


class Context:
    """
    The symbolic context for an expression
    :param expression: the expression to evaluate
    :param parent: the parent context
    :param path_condition: the path condition that led to this context
    """

    def __init__(self, expression: Expression, parent=None, path_condition=None):
        self.parent = parent
        self.expression: Expression = expression
        self.symbol_table: Dict[str, EvalResult] = (
            {} if parent is None else parent.symbol_table.copy()
        )
        self.path_condition = [] if path_condition is None else path_condition.copy()
        self.branches = []


    def _literal_to_sym(self, literal: Literal):
        if literal.type == Type.REAL:
            return SReal(literal.value)
        elif literal.type == Type.INTEGER:
            return SInteger(literal.value)
        elif literal.type == Type.BOOLEAN:
            return SBoolean(literal.value)
        elif literal.type == Type.TUPLE:
            return STuple([self._literal_to_sym(e) for e in literal.value])
        raise ValueError(f"Invalid literal type: {literal.type}")

    def execute(self, program: Program) -> List[EvalResult]:
        if isinstance(self.expression, Literal):
            # convert the literal to a symbolic expression
            if self.expression.value.type == Type.TUPLE:
                # TODO: this is wrong
                return [EvalResult(STuple([self._literal_to_sym(e.value) for e in self.expression.value.value]), self.path_condition).flatten()]
            else:
                return [EvalResult(self._literal_to_sym(self.expression.value), self.path_condition).flatten()]
        elif isinstance(self.expression, SVariable):
            return [EvalResult(self.expression, self.path_condition).flatten()]

        elif isinstance(self.expression, Variable):
            return [
                EvalResult(
                    evalr.expr_eval, self.path_condition + evalr.path_condition
                ).flatten()
                for evalr in self.symbol_table[self.expression.name]
            ]

        elif isinstance(self.expression, Assignment):
            # assignments update the symbol table in the current context and return nothing
            values = self.execute_sub(self.expression.expression, program)
            self.symbol_table[self.expression.variable.name] = values
            return values

        elif isinstance(self.expression, Block):
            # a expressions in a block share the same context, executed in order
            sub_context = Context(self.expression, self, self.path_condition)
            for expression in self.expression.expressions:
                sub_context.expression = expression
                rets = sub_context.execute(program)
                for ret in rets:
                    if isinstance(ret.expr_eval, Return):
                        return [ret]
            return rets

        elif isinstance(self.expression, Conditional):
            condition_values = self.execute_sub(self.expression.condition, program)

            rets = []
            for condition_value in condition_values:
                true_context = Context(self.expression.true_branch, self)
                false_context = Context(self.expression.false_branch, self)

                self.branches.append((condition_value, true_context, false_context))

                if isinstance(condition_value.expr_eval, SymLang):
                    # If condition involves a symbolic value, execute both branches
                    # add the true path conditions to the tc
                    tcs = [
                        EvalResult(
                            tc.expr_eval,
                            tc.path_condition + [condition_value.expr_eval],
                            is_return=tc.is_return,
                        )
                        for tc in true_context.execute(program)
                    ]
                    # add the false path conditions to the fc
                    fcs = [
                        EvalResult(
                            fc.expr_eval,
                            fc.path_condition
                            + [SUnaryOp(Operator.NOT, condition_value.expr_eval)],
                            is_return=fc.is_return,
                        )
                        for fc in false_context.execute(program)
                    ]
                    for r in tcs + fcs:
                        z3c = Z3SatConverter().add_result(r)
                        if z3c.is_sat:
                            rets += [r]
                else:
                    # If condition is concrete, execute appropriate branch
                    branch_context = (
                        true_context
                        if condition_value.expr_eval.value
                        else false_context
                    )
                    rets += branch_context.execute(program)
            return rets

        elif isinstance(self.expression, FunctionCall):
            function = program.functions[self.expression.function_name]
            function_context = Context(
                function.body, path_condition=self.path_condition
            )
            for arg, param in zip(self.expression.arguments, function.parameters):
                function_context.symbol_table[param.name] = self.execute_sub(
                    arg, program
                )

            results = function_context.execute(program)
            # Look for the Return statement in the results
            return [
                EvalResult(r.expr_eval, r.path_condition, False)
                for r in reversed(results)
                if r.is_return
            ]

        elif isinstance(self.expression, BinaryOp):
            rets = []
            left_values = self.execute_sub(self.expression.left, program)
            right_values = self.execute_sub(self.expression.right, program)
            for left_value in left_values:
                for right_value in right_values:
                    rets.append(
                        EvalResult(
                            self.execute_binary_op(
                                self.expression.operator,
                                left_value.expr_eval,
                                right_value.expr_eval,
                            ),
                            path_condition=self.path_condition
                            + left_value.path_condition
                            + right_value.path_condition,
                        ).flatten()
                    )
            return rets

        elif isinstance(self.expression, UnaryOp):
            rets = []
            values = self.execute_sub(self.expression.expression, program)
            for value in values:
                rets.append(
                    EvalResult(
                        self.execute_unary_op(
                            self.expression.operator, value.expr_eval
                        ),
                        path_condition=self.path_condition + value.path_condition,
                    ).flatten()
                )
            return rets

        elif isinstance(self.expression, Return):
            rets = self.execute_sub(self.expression.expression, program)
            return [
                EvalResult(ret.expr_eval, ret.path_condition, is_return=True)
                for ret in rets
            ]

        elif isinstance(self.expression, TupleExpression):
            # return cartesian product of the elements
            irets = []
            for element in self.expression.elements:
                irets.append(self.execute_sub(element, program))

            # iter prod the rets
            import itertools

            rets = []
            for r in itertools.product(*irets):
                # create a new tuple
                te = STuple([e.expr_eval for e in r])
                er = EvalResult(
                    te,
                    list(
                        itertools.chain.from_iterable([ri.path_condition for ri in r])
                    ),
                    is_return=False,
                )
                rets.append(er)
            return rets
        else:
            raise ValueError(f"Invalid expression: {self.expression}")

    def execute_binary_op(
        self, operator: Operator, left_value: SymLang, right_value: SymLang
    ):
        if isinstance(left_value, SymLang) or isinstance(right_value, SymLang):
            # If either operand is symbolic, the result will also be symbolic
            return SBinaryOp(left_value, operator, right_value)
        else:
            if isinstance(left_value, Symbolic) or isinstance(right_value, Symbolic):
                # If either operand is symbolic, the result will also be symbolic
                return BinaryOp(left_value, operator, right_value)
            else:
                # The existing code for handling concrete values
                if operator == Operator.ADD:
                    return Value(Type.INTEGER, left_value.value + right_value.value)
                elif operator == Operator.SUB:
                    return Value(Type.INTEGER, left_value.value - right_value.value)
                elif operator == Operator.MUL:
                    return Value(Type.INTEGER, left_value.value * right_value.value)
                elif operator == Operator.DIV:
                    if right_value.value == 0:
                        raise ValueError("Division by zero")
                    return Value(Type.INTEGER, left_value.value / right_value.value)
                elif operator == Operator.GREATER:
                    return Value(Type.BOOLEAN, left_value.value > right_value.value)
                elif operator == Operator.LESS:
                    return Value(Type.BOOLEAN, left_value.value < right_value.value)
                elif operator == Operator.GREATER_EQUAL:
                    return Value(Type.BOOLEAN, left_value.value >= right_value.value)
                elif operator == Operator.LESS_EQUAL:
                    return Value(Type.BOOLEAN, left_value.value <= right_value.value)
                elif operator == Operator.EQUAL:
                    return Value(Type.BOOLEAN, left_value.value == right_value.value)
                elif operator == Operator.AND:
                    return Value(Type.BOOLEAN, left_value.value and right_value.value)
                elif operator == Operator.OR:
                    return Value(Type.BOOLEAN, left_value.value or right_value.value)
                else:
                    raise ValueError(f"Invalid operator: {operator}")

    def execute_unary_op(self, operator: Operator, value: SymLang):
        return SUnaryOp(operator, value)
        if isinstance(value, SymbolicBool):
            return UnaryOp(operator, value)
        else:
            raise NotImplementedError(f"Unary operator {operator} not implemented")

    def execute_sub(self, expression: Expression, program: Program):
        sub_context = Context(expression, self, self.path_condition)
        return sub_context.execute(program)

    def __repr__(self):
        return f"Context({self.symbol_table}, {self.branches})"
