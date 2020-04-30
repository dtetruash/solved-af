# Solved-AF -- Copyright (C) 2020  David Simon Tetruashvili

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""This module provides the imeplementations of algorithms used to solve
    argumentation framework problems/tasks to solved-af.
"""

import errno
import subprocess
import sys

from saf.framework import getAllMaximal
from saf.theories import (DIMACSParser, completeLabelingParser,
                          stableLabellingParser)

# Set the external SAT solver command here as a list of individual
# command arguments along with the expected return code indicating that
# the external SAT solver deems the given theory UNSATISFIABLE.
SAT_COMMAND = ['glucose-syrup', '-model', '-verb=0']
UNSAT_RET_CODE = 20


def runSATSolver(encoded_sat_input):
    """Given DIMACS encoded (or encoded for your solver) input, run the
        SAT solver from SAT_COMMAND on the input and return the solver
        process object.

    Arguments:
        encoded_sat_input {str} -- string into to the external
            SAT solver

    Returns:
        subprocess.CompletedProcess -- object representation of the
            external SAT solver process that has finished.
    """

    try:
        solver = subprocess.run(SAT_COMMAND, stdout=subprocess.PIPE,
                                input=encoded_sat_input, encoding='ascii')
        return solver

    except OSError as e:
        # see if solver is installed
        if e.errno == errno.ENOENT:
            solver_name = SAT_COMMAND[0]
            sys.stderr.write(
                (
                    F'command not found: \'{solver_name}\'\n\n'
                    F'\'{solver_name}\' is a dependency of {sys.argv[0]}.\n'
                    F'Please make sure \'{solver_name}\' is executable '
                    'and is in your PATH.'
                )
            )
        else:
            sys.stderr.write(F'{e.strerror}\n\n')
        sys.stderr.flush()
        sys.exit(e.errno)
    except subprocess.CalledProcessError as e:
        # TODO Get the program name from setuptools
        # TODO instead of sys.argv[0]
        sys.stderr.write(
            (F'{sys.argv[0]} encountered an internal error.'
             F'The SAT solver command \'{" ".join(SAT_COMMAND)}\' '
             F'has failed with return code {e.returncode}.')
        )
        sys.stderr.flush()
        sys.exit(1)


def negateClause(clause):
    return [-lab_var for lab_var in clause]


def extractAssignment(raw_dimacs_output):
    """Extract a labelling variable assignment from the external SAT
        solver output.

    Arguments:
        raw_dimacs_output {str} -- DIAMCS encoded SAT solver output

    Returns:
        List[int] -- labelling variable assignment
    """

    # TODO Find the line which starts with 'v' explicitly,
    # TODO raise error if not found
    assignment_line = raw_dimacs_output.split('\n')[-2]
    # Get a list of strings from the assignment line exclusing the
    # beginning 'v' and the concluding '0' converted to ints
    return [int(lab_var) for lab_var in assignment_line.split()[1:-1]]


def excludeAssignment(solution, sat_input):
    """Add an additional clause to the SAT solver DIMACS input which
        will prevent an already found assignment to be generated again
        in subsuquent SAT solver runs. The clause added is the negation
        of the positive literals of the given assignment.

    Arguments:
        solution {List[int]} -- a labelling variable assignment
        sat_input {saf.theories.DIMACSInput} -- object representing
            current SAT solver input
    """

    # TODO Extract methods from DIMACS parser
    positive_literals = DIMACSParser.extractPositiveLiterals(solution)
    negation_clause = negateClause(positive_literals)
    negation_dimacs = DIMACSParser.parseClause(negation_clause)
    sat_input.addSingleClause(negation_dimacs)


def singleEnumeration(framework, reduction_parser):
    """Solve a single enumeration (SE) AF problem given a framework and
        a reduction parser to some argumentation semantics.

    Arguments:
        framework {saf.framework.FrameworkRepresentation} -- object
            representing the argumentation framework
        reduction_parser {saf.theories.DIMACSParser} -- parser object
            to construct the reduction of the framework to a SAT solver
            problem input

    Returns:
        List[int] or None -- the solution to the single enumeration
            problem; None indicates 'no solution;
    """

    sat_input = reduction_parser.parse(framework)

    solver = runSATSolver(sat_input.encode())

    if solver.returncode == UNSAT_RET_CODE:
        return None

    assignment = extractAssignment(solver.stdout)

    extension = reduction_parser.extractExtention(assignment)

    return extension


def fullEnumeration(framework, reduction_parser):
    """Solve a full enumeration (EE) AF problem given a framework and
        a reduction parser to some argumentation semantics.

    Arguments:
        framework {saf.framework.FrameworkRepresentation} -- object
            representing the argumentation framework
        reduction_parser {saf.theories.DIMACSParser} -- parser object
            to construct the reduction of the framework to a SAT solver
            problem input

    Returns:
        List[List[int]] -- the solution to the full enumeration problem
    """

    sat_input = reduction_parser.parse(framework)

    while True:
        solver = runSATSolver(sat_input.encode())

        if solver.returncode == UNSAT_RET_CODE:
            break

        assignment = extractAssignment(solver.stdout)
        extension = reduction_parser.extractExtention(assignment)
        excludeAssignment(assignment, sat_input)

        yield extension


def credulousDecision(framework, argument_value, enumeration_function):
    """Solve a credulous decision (DC) AF problem given a framework, the
        query argument's value, and the function which enumerates the
        extensions of the AF under the relevant semantics.

    Arguments:
         framework {saf.framework.FrameworkRepresentation} -- object
            representing the argumentation framework
        argument_value {int} -- the value of the query argument
        enumeration_function {Callable} -- a method which fully
            enumerates all AF's extensions under some semantics

    Returns:
        bool -- solution to the credulous decision problem
    """

    # TODO Test whether it is faster to use 'isIncluded' here.
    # TODO needs to be lazy, i.e. check after each extension is generated.
    return any(argument_value in extension
               for extension in enumeration_function(framework))


def skepticalDecision(framework, argument_value, enumeration_function):
    """Solve a skeptical decision (DS) AF problem given a framework, the
        query argument's value, and the function which enumerates the
        extensions of the AF under the relevant semantics.

    Arguments:
         framework {saf.framework.FrameworkRepresentation} -- object
            representing the argumentation framework
        argument_value {int} -- the value of the query argument
        enumeration_function {Callable} -- a method which fully
            enumerates all AF's extensions under some semantics

    Returns:
        bool -- solution to the skeptical decision problem
    """

    return all(argument_value in extension
               for extension in enumeration_function(framework))

#
# Concrete task implementations.
#


def groundedSingleEnumeration(framework):
    """Generate the grounded extension of the framework via the
        fixed-point of the framework's characteristic function F:

                    Ext_GR = U_{i=1..inf} F^i({})

        See (Dung,1995): https://doi.org/10.1016/0004-3702(94)00041-X

    Arguments:
        framework {saf.framework.FrameworkRepresentation} -- object
            representing the argumentation framework]

    Returns:
        List[int] -- the grounded extension of the framework
    """

    # ? Would filtering complete extensions be quicker?

    grounded_extension = set()
    curr_characteristic = set()

    while True:
        next_characteristic = framework.characteristic(curr_characteristic)
        grounded_extension |= next_characteristic

        if next_characteristic == curr_characteristic:
            # iterate untill convergance
            break

        curr_characteristic = next_characteristic

    return grounded_extension


def groundedCredulousDecision(framework, argument_value):
    """Solve the credulous decision problem under grounded semantics
    given a framework and the query argument's value.

    Arguments:
        framework {saf.framework.FrameworkRepresentation} -- object
            representing the argumentation framework
        argument_value {int} -- the value of the query argument]

    Returns:
        bool -- solution to the credulous decision problem
    """

    # ! groundedCredulousDecision could be optimised further if the
    # ! extension would be constructed iteratively and the check would
    # ! be made at each iteration against the new additions.

    return argument_value in groundedSingleEnumeration(framework)


def completeFullEnumeration(framework):
    """Solve the full enumeration problem under complete semantics
    given a framework.
    """

    return fullEnumeration(framework, completeLabelingParser)


def completeSingleEnumeration(framework):
    """Solve the single enumeration problem under complete semantics
        given a framework.
    """

    return singleEnumeration(framework, completeLabelingParser)


def completeCredulousDecision(framework, argument_value):
    """Solve the credulous decision problem under complete semantics
        given a framework and the query argument's value.
    """

    return credulousDecision(framework, argument_value,
                             completeFullEnumeration)


def completeSkepticalDecision(framework, argument_value):
    """Solve the skeptical decision problem under complete semantics
        given a framework and the query argument's value.
    """

    return skepticalDecision(framework, argument_value,
                             completeFullEnumeration)


def preferredFullEnumeration(framework):
    """Solve the full enumeration problem under grounded semantics
        given a framework. Do this via filtering complete extensions.
    """

    complete_extensions = completeFullEnumeration(framework)
    return getAllMaximal(complete_extensions)


def preferredSingleEnumeration(framework):
    """Solve the single enumeration problem under preferred semantics
        given a framework.
    """

    try:
        return preferredFullEnumeration(framework).pop()
    except KeyError:
        # A Preferred extension is unversally defined for any framework.
        # Nevertheless, this except block is added for implementational
        # safety.
        return None


def preferredCredulousDecision(framework, argument_value):
    """Solve the credulous decision problem under preferred semantics
        given a framework and the query argument's value.
    """

    return credulousDecision(framework, argument_value,
                             preferredFullEnumeration)


def preferredSkepticalDecision(framework, argument_value):
    """Solve the skeptical decision problem under preferred semantics
        given a framework and the query argument's value.
    """

    return skepticalDecision(framework, argument_value,
                             preferredFullEnumeration)


def stableFullEnumeration(framework):
    """Solve the full enumeration problem under stable semantics
        given a framework.
    """

    return fullEnumeration(framework, stableLabellingParser)


def stableSingleEnumeration(framework):
    """Solve the single enumeration problem under stable semantics
        given a framework.
    """
    return singleEnumeration(framework, stableLabellingParser)


def stableCredulousDecision(framework, argument_value):
    """Solve the credulous decision problem under stable semantics
        given a framework and the query argument's value.
    """

    return credulousDecision(framework, argument_value,
                             stableFullEnumeration)


def stableSkepticalDecision(framework, argument_value):
    """Solve the skeptical decision problem under stable semantics
        given a framework and the query argument's value.
    """

    return skepticalDecision(framework, argument_value,
                             stableFullEnumeration)


_enumerationTasksFunctions = {
    # Here list all suporeted enumeration tasks along with the method
    # which is used to solve said task.

    # Complete semantics
    'EE-CO': completeFullEnumeration,
    'SE-CO': completeSingleEnumeration,

    # Grounded semantics
    'SE-GR': groundedSingleEnumeration,

    # Preferred semantics
    'EE-PR': preferredFullEnumeration,
    'SE-PR': preferredSingleEnumeration,

    # Stable semantics
    'EE-ST': stableFullEnumeration,
    'SE-ST': stableSingleEnumeration
}

_decisionTaskFunctions = {
    # Here list all suporeted decision tasks along with the method
    # which is used to solve said task.

    # Complete semantics
    'DC-CO': completeCredulousDecision,
    'DS-CO': completeSkepticalDecision,

    # Grounded semantics
    'DC-GR': groundedCredulousDecision,

    # Preferred semantics
    'DC-PR': preferredCredulousDecision,
    'DS-PR': preferredSkepticalDecision,

    # Stable semantics
    'DC-ST': stableCredulousDecision,
    'DS-ST': stableSkepticalDecision
}


def getTasks():
    return list(_enumerationTasksFunctions.keys()) \
        + list(_decisionTaskFunctions.keys())


def getTaskMethod(task_name, is_enumeration=True):
    """Return the method which solves the given AF problem task.

    Arguments:
        task_name {str} -- the AF problem task identifier (e.g., EE-CO)

    Keyword Arguments:
        is_enumeration {bool} -- Explicit flag separation the
            enumeration and desicion tasks  (default: {True})

    Returns:
        Callable -- the method which solves the given task
    """
    try:
        task_method = _enumerationTasksFunctions[task_name] \
            if is_enumeration else \
            _decisionTaskFunctions[task_name]
        return task_method
    except KeyError:
        error_msg = (
            task_name + ' is {} task and {} either the '
            '\'-a\' or \'--argument\' option!\n'
            'You may have meant to use {} task instead with a {} or {} prefix.'
            '\n\n'
        )
        if not is_enumeration:
            formatted_err_msg = error_msg.format(
                'an enumeration',
                'forbids',
                'a decision',
                '\'DC\'', '\'DS\'')
        else:
            formatted_err_msg = error_msg.format(
                'a decision',
                'requires',
                'an enumeration',
                '\'SE\'', '\'EE\'')

        sys.stderr.write(formatted_err_msg)
        sys.stderr.write(
            'Use \'--problems\' to see the list of supportted tasks.')
        sys.stderr.flush()
        # TODO change to correct error code
        sys.exit(1)
