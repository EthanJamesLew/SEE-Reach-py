"""Symbolic execution result"""


class EvalResult:
    """EvalResult is *path* the return of evaluating an expression, meaning that branching expressions can return a list of EvalResults's"""

    def __init__(self, expr_eval, path_condition, is_return=False):
        """
        :param expr_eval: the result of evaluating the expression
        :param path_condition: the path condition that led to this result
        :param is_return: whether this result is a return statement (is that a good idea?)
        """
        self.expr_eval = expr_eval
        self.path_condition = path_condition
        self.is_return = is_return

    def flatten(self):
        """Flatten the path condition into a single symbolic expression"""
        # if expr_eval is a EvalResult, flatten it
        if isinstance(self.expr_eval, EvalResult):
            er = EvalResult(
                self.expr_eval.expr_eval,
                self.path_condition + self.expr_eval.path_condition,
            )
            return er.flatten()
        else:
            return self

    def __repr__(self):
        return f"EvalResult({self.expr_eval}, {self.path_condition}, {self.is_return})"
