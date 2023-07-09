from seereach.lang import *
from seereach.context import *

# Define pendulum constants
m = 1.0  # mass of pendulum
g = 9.81  # gravity constant
l = 1.0  # length of pendulum
x = TypedVariable(Name("x"), Type.REAL)  # plant state
u = TypedVariable(Name("u"), Type.REAL)  # controller output
kp = Literal(Value(Type.REAL, -1.0))  # proportional gain


controller_body = Block(
    [
        Assignment(u, BinaryOp(kp, Operator.MUL, Variable(x.name))),  # u = kp * x
        Conditional(
            BinaryOp(Variable(u.name), Operator.LESS, Literal(Value(Type.REAL, -5.0))),
            Return(Literal(Value(Type.REAL, -5.0))),
            Conditional(
                BinaryOp(
                    Variable(u.name),
                    Operator.GREATER,
                    Literal(Value(Type.REAL, 5.0)),
                ),
                Return(Literal(Value(Type.REAL, 5.0))),
                Return(Variable(u.name)),
            ),
        ),
    ]
)

controller_function = Function(Name("controller"), [x], Type.REAL, controller_body)

# Define variables
theta = TypedVariable(Name("theta"), Type.REAL)  # angle
omega = TypedVariable(Name("omega"), Type.REAL)  # angular velocity

# Define the pendulum dynamics
dynamics_body = Return(
    Block(
        [
            Assignment(
                TypedVariable(Name("theta_dot"), Type.REAL), Variable(Name("omega"))
            ),
            Assignment(
                TypedVariable(Name("omega_dot"), Type.REAL),
                BinaryOp(
                    FunctionCall(Name("controller"), [Variable(Name("theta"))]),
                    Operator.ADD,
                    BinaryOp(
                        Literal(Value(Type.REAL, -g / l)),
                        Operator.MUL,
                        UnaryOp(Operator.SIN, Variable(Name("theta"))),
                    ),
                ),
            ),
            TupleExpression([Variable(Name("theta_dot")), Variable(Name("omega_dot"))]),
        ]
    )
)

# Function for pendulum dynamics
dynamics_func = Function(
    Name("pendulum_dynamics"), [theta, omega], Type.TUPLE, dynamics_body
)

# Program
program = Program(
    {
        dynamics_func.name: dynamics_func,
        controller_function.name: controller_function,
    },
    dynamics_func.name,
)

# Create the initial context with symbolic variables 'theta' and 'omega'
initial_context = Context(
    FunctionCall(
        Name("pendulum_dynamics"),
        [
            SVariable(Name("theta"), variable_type=Type.REAL),
            SVariable(Name("omega"), variable_type=Type.REAL),
        ],
    )
)

# Execute the program
r = initial_context.execute(program)
print(r)

# pretty print the program
from seereach.pprint import HLTargetPrinter, EvalResultPrinter
from seereach.z3convert import Z3SatConverter

print(HLTargetPrinter().visit(program))

# Execute the program
r = initial_context.execute(program)
for result in r:
    print(EvalResultPrinter().print(result))
    print(Z3SatConverter().add_result(result).is_sat)
