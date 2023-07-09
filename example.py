from seereach.lang import *
from seereach.context import *

# Variables
x = TypedVariable(Name('x'), Type.INTEGER)
y = TypedVariable(Name('y'), Type.INTEGER)

# Function definition
function_body = Return(
    Block([
        Assignment(TypedVariable(Name('local'), Type.INTEGER), Literal(Value(Type.INTEGER, 0))),
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

# Program
program = Program({function.name: function}, function.name)

# Create the initial context with a symbolic variable 'x'
initial_context = Context(FunctionCall(Name('foo'), [SVariable(Name('x'))]))

# Execute the program
r = initial_context.execute(program)
print(r)

# Print all execution paths
# for path in initial_context.get_paths():
#    print(path)
