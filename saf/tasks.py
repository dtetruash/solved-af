import sys
from saf.theories import CompleteLabelingDIMACSParser as CLDIMACSParser
from saf.theories import DIMACSParser
from subprocess import run, PIPE
# from saf.framework import getMinimal, getMaximal

SAT_COMMAND = ['glucose', '-model', '-verb=0']


def CompleteEnumeration(framework):
    theory_parser = CLDIMACSParser

    sat_input = theory_parser.parse(framework)

    extentions = []
    extension_values_list = []
    unsatisfiable = False
    while not unsatisfiable:
        """TODO Use input buffers and Popen() to write to the buffer
        stream directly"""
        sat_solver_proccess = run(SAT_COMMAND, stdout=PIPE,
                                  input=sat_input.encode(), encoding='ascii')
        # TODO Encapsulate
        # TODO maybe try extracting the solution universally via regex
        solution = sat_solver_proccess.stdout.split('\n')[-2]
        unsatisfiable = sat_solver_proccess.returncode == 20
        if not unsatisfiable:
            extension_values = DIMACSParser.extractExtention(solution)
            extension_values_list.append(extension_values)
            extension = framework.valuesToArguments(extension_values)
            extentions.append(extension)
            # TODO Encapsulate in a method
            solution_labeling = DIMACSParser.extractLabeling(solution)
            solution_negation_clause = [[str(-lab_var) for lab_var
                                         in solution_labeling]]
            solution_negation_dimacs = theory_parser.parseCNFTheory(
                solution_negation_clause)
            sat_input.addClause(solution_negation_dimacs)
    return extentions

    # # Minimal extension TEST
    # minimal_extention_values = getMinimal(extension_values_list)
    # minimal_extension = framework.valuesToArguments(minimal_extention_values)
    # print('the minimal extension is: ')
    # saf.io.outputSE(minimal_extension)

    # # maximal extension TEST
    # maximal_extensions = [framework.valuesToArguments(
    #     maximal_extention_values) for maximal_extention_values
    #     in getMaximal(extension_values_list)]
    # print('the maximal extensions are: ')
    # saf.io.outputEE(maximal_extensions)


def GroundedSingleEnumeration(framework):
    # U_{1..inf} Fi([])
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


def GroundedCredulousDecision(framework, argument_value):
    return argument_value in GroundedSingleEnumeration(framework)


_enumerationTasksFunctions = {
    # Complete semantics`
    'EE-CO': CompleteEnumeration,
    # 'SE-CO': CompleteSingleEnumeration,

    # Grounded semantics
    'SE-GR': GroundedSingleEnumeration

    # Preferred semantics
    # 'EE-PR': PreferredEnumeration,
    # 'SE-PR': PreferredSingleEnumeration,

    # Stable semantics
    # 'EE-ST': StableEnumeration,
    # 'SE-ST': StableSingleEnumeration
}

_decisionTaskFunctions = {
    # Complete semantics
    # 'DC-CO': CompleteCredulousDecision,
    # 'DS-CO': CompleteSkepticalDecision,

    # Grounded semantics
    'DC-GR': GroundedCredulousDecision,

    # Preferred semantics
    # 'DC-PR': PreferredCredulousDecision,
    # 'DS-PR': PreferredSkepticalDecision,

    # Stable semantics
    # 'DC-ST': StableCredulousDecision,
    # 'DS-ST': StableSkepticalDecision
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
