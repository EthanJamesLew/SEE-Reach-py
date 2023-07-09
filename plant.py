from seereach.lang import *
from seereach.context import *

x = TypedVariable(Name("x"), Type.REAL)  # plant state
xp = TypedVariable(Name("xp"), Type.REAL)  # next plant state
u = TypedVariable(Name("u"), Type.REAL)  # controller output
kp = Literal(Value(Type.REAL, -1.0))  # proportional gain


controller_body = Return(
    Block(
        [
            Assignment(u, BinaryOp(kp, Operator.MUL, Variable(x.name))),  # u = kp * x
            Conditional(
                BinaryOp(
                    Variable(u.name), Operator.LESS, Literal(Value(Type.REAL, -5.0))
                ),
                Literal(Value(Type.REAL, -5.0)),
                Conditional(
                    BinaryOp(
                        Variable(u.name),
                        Operator.GREATER,
                        Literal(Value(Type.REAL, 5.0)),
                    ),
                    Literal(Value(Type.REAL, 5.0)),
                    Variable(u.name),
                ),
            ),
        ]
    )
)

controller_function = Function(Name("controller"), [x], Type.REAL, controller_body)

plant_body = Return(
    Block(
        [
            Assignment(
                u,
                FunctionCall(
                    Name("controller"), [Variable(x.name)]
                ),  # u = controller(x)
            ),
            # Dynamics here
            # As an example, let's consider a simple integrator: xp = x + u
            Assignment(
                xp,
                BinaryOp(
                    Variable(x.name), Operator.ADD, Variable(u.name)
                ),  # xp = x + u
            ),
            Variable(xp.name),  # return xp
        ]
    )
)

plant_function = Function(Name("plant"), [x], Type.REAL, plant_body)

program = Program(
    {
        plant_function.name: plant_function,
        controller_function.name: controller_function,
    },
    plant_function.name,
)

# Create the initial context with a symbolic variable 'x'
initial_context = Context(FunctionCall(Name("plant"), [SVariable(Name("x"))]))

# pretty print the program
from seereach.pprint import HLTargetPrinter, EvalResultPrinter

print(HLTargetPrinter().visit(program))

# Execute the program
r = initial_context.execute(program)
for result in r:
    print(EvalResultPrinter().print(result))
