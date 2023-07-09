"""Pretty Printer for the SymLang AST and HL Target AST"""
from seereach.symlang import *
from seereach.lang import *


def lookup_binop(operator: Operator) -> str:
    return {
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
    }.get(operator, operator)


def lookup_unop(operator: Operator, inner) -> str:
    prefix = {
        Operator.NOT: "!",
    }

    funcs = {
        Operator.SIN: "sin",
    }

    if operator in prefix:
        return f"{prefix[operator]}{inner}"
    if operator in funcs:
        return f"{funcs[operator]}({inner})"
    return f"{operator} {inner}"


def lookup_type(value_type: Type) -> str:
    return {
        Type.REAL: "real",
        Type.INTEGER: "int",
        Type.BOOLEAN: "bool",
        Type.TUPLE: "tuple",
    }.get(value_type, value_type)


class SymLangPrinter:
    def print(self, node: SymLang) -> str:
        return self.visit(node)

    def visit(self, node: SymLang) -> str:
        if isinstance(node, SReal):
            return self.visit_sreal(node)
        elif isinstance(node, SInteger):
            return self.visit_sinteger(node)
        elif isinstance(node, SBoolean):
            return self.visit_sboolean(node)
        elif isinstance(node, SVariable):
            return self.visit_svariable(node)
        elif isinstance(node, STuple):
            return self.visit_stuple(node)
        elif isinstance(node, SBinaryOp):
            return self.visit_sbinaryop(node)
        elif isinstance(node, SUnaryOp):
            return self.visit_sunaryop(node)
        elif isinstance(node, STuple):
            return self.visit_stuple(node)
        else:
            return f"{node}"

    def visit_sreal(self, node: SReal) -> str:
        return f"{node.value}"

    def visit_sinteger(self, node: SInteger) -> str:
        return f"{node.value}"

    def visit_sboolean(self, node: SBoolean) -> str:
        return f"{node.value}"

    def visit_svariable(self, node: SVariable) -> str:
        return f"{node.name}"

    def visit_stuple(self, node: STuple) -> str:
        return f"({', '.join([self.visit(e) for e in node.elements])})"

    def visit_sbinaryop(self, node: SBinaryOp) -> str:
        operator_symbol = lookup_binop(node.operator)
        return f"({self.visit(node.left)} {operator_symbol} {self.visit(node.right)})"

    def visit_sunaryop(self, node: SUnaryOp) -> str:
        operator_symbol = lookup_unop(node.operator, self.visit(node.expression))
        return f"({operator_symbol})"

    def visit_stuple(self, node: STuple) -> str:
        return f"({', '.join([self.visit(e) for e in node.elements])})"


class HLTargetPrinter:
    def print(self, node: HLLang) -> str:
        return self.visit(node)

    def visit(self, node: HLLang, indent="") -> str:
        if isinstance(node, Program):
            return self.visit_program(node, indent)
        elif isinstance(node, Block):
            return self.visit_block(node, indent)
        elif isinstance(node, TypedVariable):
            return self.visit_tvariable(node, indent)
        elif isinstance(node, Assignment):
            return self.visit_assignment(node, indent)
        elif isinstance(node, Name):
            return self.visit_name(node, indent)
        elif isinstance(node, Function):
            return self.visit_function(node, indent)
        elif isinstance(node, Variable):
            return self.visit_variable(node, indent)
        elif isinstance(node, Literal):
            return self.visit_literal(node, indent)
        elif isinstance(node, BinaryOp):
            return self.visit_binaryop(node, indent)
        elif isinstance(node, UnaryOp):
            return self.visit_unaryop(node, indent)
        elif isinstance(node, Return):
            return self.visit_return(node, indent)
        elif isinstance(node, Conditional):
            return self.visit_conditional(node, indent)
        elif isinstance(node, FunctionCall):
            return self.visit_functioncall(node, indent)
        elif isinstance(node, TupleExpression):
            return self.visit_tupleexpression(node, indent)
        else:
            raise NotImplementedError(
                f"Unknown node type: {node}({node.__class__.__name__})"
            )

    def visit_program(self, node: Program, indent="") -> str:
        """program is printed as a bunch of indented lines"""

        # print functions
        functions = "\n".join([self.visit(f, "") for f in node.functions.values()])

        # print main
        main = self.visit(node.start, "")

        return f"{indent}{functions}\n{indent}{main}"

    def visit_function(self, node: Function, indent="") -> str:
        """function is printed like a rust function

        fn <name>(<parameters>) -> <return_type> {
            <body>
        }
        """

        # print parameters
        parameters = ", ".join([self.visit(p) for p in node.parameters])

        # print body
        body = self.visit(node.body, indent + "    ")

        return f"{indent}fn {node.name}({parameters}) -> {lookup_type(node.return_type)} {{\n{indent + '    '}{body}\n{indent}}}"

    def visit_variable(self, node: Variable, indent="") -> str:
        return f"{node.name}"

    def visit_literal(self, node: Literal, indent="") -> str:
        return f"{node.value}"

    def visit_binaryop(self, node: BinaryOp, indent="") -> str:
        return f"{self.visit(node.left, '')} {lookup_binop(node.operator)} {self.visit(node.right, '')}"

    def visit_unaryop(self, node: UnaryOp, indent="") -> str:
        return f"{lookup_unop(node.operator, self.visit(node.expression, ''))}"

    def visit_return(self, node: Return, indent="") -> str:
        return f"return {self.visit(node.expression, indent + '    ')}"

    def visit_value(self, node: Value, indent="") -> str:
        return f"Value({node.type}, {node.value})"

    def visit_name(self, node: Name, indent="") -> str:
        return f"{node.value}"

    def visit_conditional(self, node: Conditional, indent="") -> str:
        """conditional is printed like a rust if expression

        if <condition> {
            <then_expression>
        } else {
            <else_expression>
        }
        """
        # condition
        condition = self.visit(node.condition, "")

        # then expression
        then_expression = self.visit(node.true_branch, indent + "    ")

        # else expression
        else_expression = self.visit(node.false_branch, indent + "    ")

        return f"if {condition} {{\n{indent + '    '}{then_expression}\n{indent}}} else {{\n{indent + '    '}{else_expression}\n{indent}}}"

    def visit_functioncall(self, node: FunctionCall, indent="") -> str:
        """function call is printed like a rust function call

        <name>(<arguments>)
        """
        # name
        name = self.visit(node.function_name, "")

        # arguments
        arguments = ", ".join([self.visit(a) for a in node.arguments])

        return f"{name}({arguments})"

    def visit_block(self, node: Block, indent="") -> str:
        """block is printed as a bunch of indented lines"""
        # print statements
        statements = f";\n{indent + '    '}".join(
            [self.visit(s, indent + "    ") for s in node.expressions]
        )

        return "{\n" + f"{indent + '    '}{statements}" + f"\n{indent}" + "}"

    def visit_name(self, node: Name, indent="") -> str:
        return f"{node}"

    def visit_tvariable(self, node: TypedVariable, indent="") -> str:
        return f"{node.name}: {lookup_type(node.variable_type)}"

    def visit_assignment(self, node: Assignment, indent="") -> str:
        return f"{self.visit(node.variable)} = {self.visit(node.expression)}"

    def visit_tupleexpression(self, node: TupleExpression, indent="") -> str:
        return f"({', '.join([self.visit(e) for e in node.elements])})"


class EvalResultPrinter:
    def print(self, node: "EvalResult") -> str:
        """
        format
        ===
        Expr:
            <expr>
        Path Condition(s):
            <path_condition0>
            <path_condition1>
        ===

        """
        sp = SymLangPrinter()
        hl = HLTargetPrinter()
        path_conditions = [sp.print(p) for p in node.path_condition]
        expr = sp.print(node.expr_eval)

        return (
            f"===\nExpr:\n    {expr}\nPath Condition(s):\n    "
            + ("\n    ".join(path_conditions) if len(path_conditions) > 0 else "<NONE>")
            + "\n==="
        )
