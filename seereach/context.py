"""Symbolic Contexts for SEE-Reach"""
from seereach.lang import *
from seereach.symlang import *

class Function:
    def __init__(self, name: Name, parameters: List[TypedVariable], return_type: Type, body: Expression):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body
    
    def execute(self, context: 'Context', program: 'Program'):
        # bind the parameters to the arguments
        for param, arg in zip(self.parameters, context.expression.arguments):
            context.symbol_table[param.name] = arg
        # execute the body
        body_context = Context(self.body, context)
        return body_context.execute(program)


class Program:
    def __init__(self, functions: Dict[Name, Function], start: Name):
        self.functions = functions
        self.start = start


class SymbolicValue:
    def __init__(self, expression: Expression):
        self.expression = expression

    def __repr__(self):
        return f"SymbolicValue({self.expression})"


class Context:
    def __init__(self, expression: Expression, parent=None, path_condition=None):
        self.parent = parent
        self.expression = expression
        self.symbol_table = {} if parent is None else parent.symbol_table.copy()
        self.path_condition = [] if path_condition is None else path_condition.copy()
        self.branches = []

    def execute(self, program: Program):
        if isinstance(self.expression, Literal):
            return [self.expression.value]
        elif isinstance(self.expression, SVariable):
            return [self.expression]
        elif isinstance(self.expression, Variable):
            return [self.symbol_table[self.expression.name]]
        elif isinstance(self.expression, Assignment):
            value = self.execute_sub(self.expression.expression, program)
            # TODO: this is wrong
            self.symbol_table[self.expression.variable.name] = value[0]
            return [value]
        elif isinstance(self.expression, Block):
            # create a sub context
            sub_context = Context(self.expression, self, self.path_condition)
            for expression in self.expression.expressions:
                sub_context.expression = expression
                ret = sub_context.execute(program)
                # if expression if return, return the value
                if isinstance(expression, Return):
                    return [ret]
            return [ret]
        elif isinstance(self.expression, Conditional):
            condition_values = self.execute_sub(self.expression.condition, program)

            rets = [] 
            for condition_value in condition_values:
                true_context = Context(self.expression.true_branch, self)
                false_context = Context(self.expression.false_branch, self)

                self.branches.append((condition_value, true_context, false_context))

                if isinstance(condition_value, SymVal):
                    # If condition involves a symbolic value, execute both branches
                    rets += true_context.execute(program) + false_context.execute(program)
                else:
                    # If condition is concrete, execute appropriate branch
                    branch_context = true_context if condition_value.value else false_context
                    rets += branch_context.execute(program)
            return rets
        
        elif isinstance(self.expression, FunctionCall):
            function = program.functions[self.expression.function_name]
            function_context = Context(function.body, path_condition=self.path_condition)
            for arg, param in zip(self.expression.arguments, function.parameters):
                function_context.symbol_table[param.name] = self.execute_sub(arg, program)[0]

            results = function_context.execute(program)
            # Look for the Return statement in the results
            for result in reversed(results):
                if isinstance(result, Return):
                    return [result.expression]
            
            # No Return statement found, return an empty list
            return []
        elif isinstance(self.expression, BinaryOp):
            left_value = self.execute_sub(self.expression.left, program)[0]
            right_value = self.execute_sub(self.expression.right, program)[0]
            return [self.execute_binary_op(self.expression.operator, left_value, right_value)]
        elif isinstance(self.expression, UnaryOp):
            value = self.execute_sub(self.expression.expression, program)[0]
            return [self.execute_unary_op(self.expression.operator, value)]
        elif isinstance(self.expression, Return):
            return [Return(self.execute_sub(self.expression.expression, program))]
        else:
            raise ValueError(f'Invalid expression: {self.expression}') 

    def execute_binary_op(self, operator: Operator, left_value: SymVal, right_value: SymVal):
        if isinstance(left_value, SymVal) or isinstance(right_value, SymVal):
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
                        raise ValueError('Division by zero')
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
                    raise ValueError(f'Invalid operator: {operator}')

    def execute_unary_op(self, operator: Operator, value: SymVal):
        if isinstance(value, SymbolicBool):
            return UnaryOp(operator, value)
        else:
            raise NotImplementedError

    def execute_sub(self, expression: Expression, program: Program):
        sub_context = Context(expression, self, self.path_condition)
        return sub_context.execute(program)
    
    def contains_symbolic(self, expression: Expression):
        if isinstance(expression, Variable):
            # check if the variable has a symbolic value
            return isinstance(self.symbol_table.get(expression.name, None), SymbolicValue)
        elif isinstance(expression, Literal):
            return False
        elif isinstance(expression, BinaryOp):
            return self.contains_symbolic(expression.left) or self.contains_symbolic(expression.right)
        else:
            return False

    def get_paths(self):
        if self.branches:
            return [path for branch in self.branches for path in branch.get_paths()]
        else:
            return [(self.symbol_table, self.path_condition)]

    def __repr__(self):
        return f'Context({self.symbol_table}, {self.branches})'
