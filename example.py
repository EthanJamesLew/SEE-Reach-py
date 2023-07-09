from seereach.lang import *
from seereach.context import *

# Variables
x = TypedVariable(Name('x'), Type.INTEGER)
y = TypedVariable(Name('y'), Type.INTEGER)

# Function definition
function_body = Return(
    Block([
        Assignment(
            TypedVariable(Name('local'), Type.INTEGER), 
            BinaryOp(
                Variable(Name('x')), 
                Operator.ADD, 
                FunctionCall(Name('bar'), [Variable(Name('x'))]) 
            )
        ),
        Conditional(
            BinaryOp(Variable(Name('x')), Operator.LESS, Literal(Value(Type.INTEGER, 0))),
            Conditional(
                BinaryOp(Variable(Name('x')), Operator.EQUAL, Literal(Value(Type.INTEGER, 0))),
                Literal(Value(Type.INTEGER, 0)),
                Literal(Value(Type.INTEGER, -1))
            ),
            Conditional(
                BinaryOp(Variable(Name('x')), Operator.EQUAL, Literal(Value(Type.INTEGER, 0))),
                Variable(Name('local')),
                BinaryOp(Literal(Value(Type.INTEGER, 2)), Operator.ADD, Literal(Value(Type.INTEGER, 3))) 
            ),
        )
    ])
    
)

function = Function(Name('foo'), [x], Type.INTEGER, function_body)
function2 = Function(Name('bar'), [x], Type.INTEGER, Return(Literal(Value(Type.INTEGER, 10))))

# Program
program = Program({function.name: function, function2.name: function2}, function.name)

# Create the initial context with a symbolic variable 'x'
initial_context = Context(FunctionCall(Name('foo'), [SVariable(Name('x'))]))

# Execute the program
r = initial_context.execute(program)
print(r)

# pretty print foo
from seereach.pprint import HLTargetPrinter, EvalResultPrinter

print(HLTargetPrinter().visit(program))
for result in r:
    print(EvalResultPrinter().print(result))

# Print all execution paths
# for path in initial_context.get_paths():
#    print(path)
