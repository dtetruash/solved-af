import errno
import subprocess
import sys

from saf.framework import getAllMaximal
from saf.theories import DIMACSParser
from saf.theories import completeLabelingParser, stableLabellingParser

SAT_COMMAND = ['glucose', '-model', '-verb=0']
UNSAT_CODE = 20


def runSATSolver(encoded_sat_input):
    """TODO Use input buffers and Popen() to write to the buffer
        stream directly"""
    try:
        return subprocess.run(SAT_COMMAND, stdout=subprocess.PIPE,
                              input=encoded_sat_input, encoding='ascii')
        # return subprocess.Popen(SAT_COMMAND,
        #                         stdout=subprocess.PIPE,
        #                         stdin=subprocess.PIPE)
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
            # TODO Get the program name from setuptools
            # TODO instead of sys.argv[0]
            sys.stderr.write(
                (F'{sys.argv[0]} encountered an internal error.'
                 F'The SAT solver command \'{" ".join(SAT_COMMAND)}\' '
                 F'has failed with return code {e.returncode}.')
            )
        sys.stderr.flush()
        sys.exit(e.errno)


def negateClause(clause):
    return [-lab_var for lab_var in clause]


def extractAssignment(raw_dimacs_output):
    # TODO Find the line which starts with 'v' explicitly,
    # TODO raise error if not found
    assignment_line = raw_dimacs_output.split('\n')[-2]
    # Get a list of strings from the assignment line exclusing the
    # beginning 'v' and the concluding '0' converted to ints
    return [int(lab_var) for lab_var in assignment_line.split()[1:-1]]


def excludeAssignment(solution, sat_input):
    # TODO Extract methods from DIMACS parser
    positive_literals = DIMACSParser.extractPositiveLiterals(solution)
    negation_clause = negateClause(positive_literals)
    negation_dimacs = DIMACSParser.parseClause(negation_clause)
    sat_input.addSingleClause(negation_dimacs)


def singleEnumeration(framework, reduction_parser):
    sat_input = reduction_parser.parse(framework)

    solver = runSATSolver(sat_input.encode())

    if solver.returncode == UNSAT_CODE:
        return None

    assignment = extractAssignment(solver.stdout)

    extension = reduction_parser.extractExtention(assignment)

    return extension


def fullEnumeration(framework, reduction_parser):
    sat_input = reduction_parser.parse(framework)

    while True:
        solver = runSATSolver(sat_input.encode())

        if solver.returncode == UNSAT_CODE:
            break

        assignment = extractAssignment(solver.stdout)
        extension = reduction_parser.extractExtention(assignment)
        excludeAssignment(assignment, sat_input)

        yield extension


def credulousDecision(framework, argument_value, enumeration_function):
    # TODO Test whether it is faster to use 'isIncluded' here.
    # TODO needs to be lazy, i.e. check after each extension is generated.
    return any(argument_value in extension
               for extension in enumeration_function(framework))


def skepticalDecision(framework, argument_value, enumeration_function):
    return all(argument_value in extension
               for extension in enumeration_function(framework))


"""
Concrete task implementations.
"""


def groundedSingleEnumeration(framework):
    # U_{1..inf} F^i({})
    grounded_extension = set()
    curr_characteristic = set()

    # Currently this is an O(n^n) optation... as each call to
    # framework.characteristic is O(n) and it may loop n+1 times...
    # ? Would filtering complete extensions be quicker?

    while True:
        next_characteristic = framework.characteristic(curr_characteristic)
        grounded_extension |= next_characteristic

        if next_characteristic == curr_characteristic:
            break

        curr_characteristic = next_characteristic

    return grounded_extension


def groundedCredulousDecision(framework, argument_value):
    # ! groundedCredulousDecision could be optimised further if the
    # ! extension would be constructed iteratively and the check would
    # ! be made at each iteration against the new additions.

    return argument_value in groundedSingleEnumeration(framework)


def completeFullEnumeration(framework):
    return fullEnumeration(framework, completeLabelingParser)


def completeSingleEnumeration(framework):
    return singleEnumeration(framework, completeLabelingParser)


def completeCredulousDecision(framework, argument_value):
    return credulousDecision(framework, argument_value,
                             completeFullEnumeration)


def completeSkepticalDecision(framework, argument_value):
    return skepticalDecision(framework, argument_value,
                             completeFullEnumeration)


def preferredFullEnumeration(framework):
    complete_extensions = completeFullEnumeration(framework)

    return getAllMaximal(complete_extensions)


def preferredSingleEnumeration(framework):
    try:
        return preferredFullEnumeration(framework).pop()
    except KeyError:
        return None
    # try:
    #     return next(preferredFullEnumeration(framework))
    # except StopIteration:
    #     return None


def preferredCredulousDecision(framework, argument_value):
    return credulousDecision(framework, argument_value,
                             preferredFullEnumeration)


def preferredSkepticalDecision(framework, argument_value):
    return skepticalDecision(framework, argument_value,
                             preferredFullEnumeration)


def stableFullEnumeration(framework):
    return fullEnumeration(framework, stableLabellingParser)


def stableSingleEnumeration(framework):
    return singleEnumeration(framework, stableLabellingParser)


def stableCredulousDecision(framework, argument_value):
    return credulousDecision(framework, argument_value,
                             stableFullEnumeration)


def stableSkepticalDecision(framework, argument_value):
    return skepticalDecision(framework, argument_value,
                             stableFullEnumeration)


_enumerationTasksFunctions = {
    # Complete semantics`
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
    try:
        task_method = _enumerationTasksFunctions[task_name] \
            if is_enumeration else \
            _decisionTaskFunctions[task_name]
        return task_method
    except KeyError:
        # TODO !!! Deligate this error throw to Argsparse or __main__
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
