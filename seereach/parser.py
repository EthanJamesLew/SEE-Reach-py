"""A Bad Parser for the SEE-Reach Language"""
from seereach.lang import *
from ply import lex, yacc

tokens = [
    "NAME",
    "REAL",
    "INTEGER",
    "BOOLEAN",
    "OPERATOR",
    "EQUALS",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "COLON",
    "ARROW",
    "LCURLY",
    "RCURLY",
    "RETURN",
    "TYPE",
    "FNDEC",
    "SEMICOLON",
    "IF",
    "ELSE",
    "ASSIGN",
    "MINUS",
    "NEG_NUMBER",
    "NEG_INTEGER",
    "SIN",
]


def t_ARROW(t):
    r"-\>"
    return t


t_ASSIGN = r"="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_COMMA = r","
t_COLON = r":"
t_LCURLY = r"\{"
t_RCURLY = r"\}"
t_SEMICOLON = r";"
t_NAME = r"[a-zA-Z_][a-zA-Z_0-9]*"

# Ignore whitespace
t_ignore = " \t"


# Newline handling; track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_REAL(t):
    r"\d+\.\d+"
    t.value = Literal(Value(Type.REAL, float(t.value)))
    return t


def t_NEG_NUMBER(t):
    r"-\d+(\.\d+)?"
    t.value = Literal(
        Value(Type.REAL, float(t.value))
    )  # Convert the string representation into a float
    return t


def t_NEG_INTEGER(t):
    r"-\d+"
    t.value = Literal(
        Value(Type.INTEGER, int(t.value))
    )  # Convert the string representation into an int
    return t


def t_INTEGER(t):
    r"\d+"
    t.value = Literal(Value(Type.INTEGER, int(t.value)))
    return t


def t_SIN(t):
    r"sin"
    t.value = Operator.SIN
    return t


# Handle arithmetic operations
def t_OPERATOR(t):
    r"\+|\*|/|<|>|<=|>=|==|&&"
    # map the operators to your internal representation here
    if t.value == "+":
        t.value = Operator.ADD
    elif t.value == "-":
        t.value = Operator.SUB
    elif t.value == "*":
        t.value = Operator.MUL
    elif t.value == "/":
        t.value = Operator.DIV
    elif t.value == "<":
        t.value = Operator.LESS
    elif t.value == ">":
        t.value = Operator.GREATER
    elif t.value == "<=":
        t.value = Operator.LESS_EQUAL
    elif t.value == ">=":
        t.value = Operator.GREATER_EQUAL
    elif t.value == "==":
        t.value = Operator.EQUAL
    elif t.value == "&&":
        t.value = Operator.AND
    else:
        raise ValueError(f"Unknown operator {t.value}")
    return t


def t_TYPE(t):
    r"real|int|bool|tuple"
    if t.value == "real":
        t.value = Type.REAL
    elif t.value == "int":
        t.value = Type.INTEGER
    elif t.value == "bool":
        t.value = Type.BOOLEAN
    elif t.value == "tuple":
        t.value = Type.TUPLE
    else:
        raise ValueError(f"Unknown type {t.value}")
    return t


def t_BOOLEAN(t):
    r"true|false"
    if t.value == "true":
        t.value = Literal(Value(Type.BOOLEAN, True))
    elif t.value == "false":
        t.value = Literal(Value(Type.BOOLEAN, False))
    else:
        raise ValueError(f"Unknown boolean {t.value}")
    return t


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def t_FNDEC(t):
    r"fn"
    return t


def t_RETURN(t):
    r"return"
    return t


def t_IF(t):
    r"if"
    return t


def t_ELSE(t):
    r"else"
    return t


precedence = (
    ("left", "RETURN"),
    ("left", "OPERATOR"),
    ("nonassoc", "REAL", "NAME"),
)


def p_program(p):
    "program : functions"
    p[0] = Program(p[1], list(p[1].keys())[0])


def p_functions(p):
    """functions : function
    | functions function"""
    if len(p) == 2:
        p[0] = {p[1].name: p[1]}
    else:
        p[0] = p[1]
        p[0][p[2].name] = p[2]


def p_function(p):
    "function : FNDEC NAME LPAREN parameters RPAREN ARROW TYPE LCURLY body RCURLY"
    p[0] = Function(Name(p[2]), p[4], p[7], p[9])


def p_parameters(p):
    """parameters : parameter
    | parameters COMMA parameter"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1][:]
        p[0].append(p[3])


def p_parameter(p):
    "parameter : NAME COLON TYPE"
    p[0] = TypedVariable(Name(p[1]), p[3])


def p_body(p):
    """body : expression
    | body SEMICOLON expression"""
    if len(p) == 2:
        p[0] = Block([p[1]])
    else:
        p[0] = p[1]
        p[0] = Block(p[0].expressions + [p[3]])


def p_return(p):
    "expression : RETURN expression"
    p[0] = Return(p[2])


def p_expression_binop(p):
    "expression : expression OPERATOR expression"
    p[0] = BinaryOp(p[1], p[2], p[3])


def p_expression_name(p):
    "expression : NAME"
    p[0] = Variable(Name(p[1]))


def p_expression_number(p):
    """expression : REAL
    | INTEGER
    | BOOLEAN
    | NEG_NUMBER
    | NEG_INTEGER"""
    p[0] = p[1]


def p_expression_func_call(p):
    "expression : NAME LPAREN expressions RPAREN"
    p[0] = FunctionCall(Name(p[1]), p[3])


def p_expressions(p):
    """expressions : expression
    | expressions COMMA expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])


def p_assignment(p):
    "expression : NAME COLON TYPE ASSIGN expression"
    p[0] = Assignment(TypedVariable(Name(p[1]), p[3]), p[5])


def p_expression_conditional(p):
    """expression : IF expression LCURLY body RCURLY ELSE LCURLY body RCURLY
    | IF expression LCURLY body RCURLY"""
    if len(p) == 6:
        p[0] = Conditional(p[2], p[4], None)
    else:
        p[0] = Conditional(p[2], p[4], p[8])


def p_expression_tuple(p):
    "expression : LPAREN tuple_contents RPAREN"
    p[0] = TupleExpression(p[2])


def p_tuple_contents(p):
    """tuple_contents : expression COMMA expression
    | tuple_contents COMMA expression"""
    # if len(p) == 2:
    #    p[0] = [p[1]]
    # else:
    #    p[0] = p[1] + [p[3]]
    if len(p) == 4:
        p[0] = [p[1], p[3]]
    else:
        p[0] = p[1] + [p[3]]


def p_sin(p):
    "expression : SIN LPAREN expression RPAREN"
    p[0] = UnaryOp(Operator.SIN, p[3])


def p_error(p):
    print(f"Syntax error in input! {p}")


SReachLexer = lex.lex()
SReachParser = yacc.yacc(debug=True)
