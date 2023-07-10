"""Function Analyzer"""

from typing import List
from seereach.context import Context
from seereach.lang import FunctionCall, Name, Program, Type
from seereach.result import EvalResult
from seereach.symlang import SVariable


def function_symbolic_execution(
    program: Program, funname: str, signature_params=None
) -> List[EvalResult]:
    """Symbolic execution of a function inside a program"""
    # Create the function signature with SVariables
    if signature_params is None:
        signature_params = []
        for param in program.functions[funname].parameters:
            signature_params.append(SVariable(param.name, param.variable_type))

    # Create the initial context with symbolic variables 'theta' and 'omega'
    initial_context = Context(
        FunctionCall(
            Name(funname),
            signature_params,
        )
    )

    # Execute the program
    return initial_context.execute(program)
