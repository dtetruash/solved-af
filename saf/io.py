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

"""This module provides I/O means to solved-af, including input parsing
    and validation, argument parsing and validation,
    and output formatting.
"""

import argparse
import re
import sys

import saf.tasks as tasks


def _reportInvalidInputFileAndExit(message):
    sys.stderr.write(F'Invalid input file!')
    sys.stderr.write(message)
    sys.stderr.flush()
    sys.exit(1)


def _validateAttack(attack, arguments, attacks, attack_str):
    """Given an input attack and the contextual established components
    of the argumentation fromework (arguments list and attacks list)
    as well as the string encoding the attack notify and exit if the
    attack is invalid.

    Arguments:
        attack {Tuple[str]} -- attack given as a tuple
        arguments {List[str]} -- list of arguments currenly in the AF
        attacks {List[Tuple[str]]} -- list of attacks currenty in the AF
        attack_str {str} -- the input line verbatim describing
            the attack
    """

    if len(attack) != 2:
        _reportInvalidInputFileAndExit(
            F'Attack "{attack_str}" must contain exactly two arguments.')

    elif attack[0] not in arguments or attack[1] not in arguments:
        _reportInvalidInputFileAndExit(
            F'Argument(s) in "{attack_str}" are not defined.')

    elif attack in attacks:
        _reportInvalidInputFileAndExit(
            F'Attack "{attack_str}" is defiled more than once.')


def _validateArgument(argument, arguments):
    """Given an input argument name and the contextual list of
    established argument notify and exit if the argument is invalid.

    Arguments:
        argument {str} -- argument name to be checked for validity
        arguments {List[str]} -- list of arguments currently in the AF
    """

    if len(argument.split()) > 1 or argument.find(',') != -1:
        _reportInvalidInputFileAndExit(
            F'Argument "{argument}" contains whitespace or comma.')

    if argument in arguments:
        _reportInvalidInputFileAndExit(
            F'Argument "{argument}" is defiled more than once.')


def _parseTGF(file, validate=False):
    """Given an input file-like object encoded in the Trivial Graph
    Format parse it and return the AF it describes in term of its
    components.

    Arguments:
        file {File} -- file-like object containing a TGF encoded AF

    Keyword Arguments:
        validate {bool} -- whether to validate the contents of the file
            (default: {False})

    Returns:
        Tuple[List[str],List[Tuple[str]]] -- tuple representation of the
            encoded AF
    """

    arguments = []
    attacks = []

    has_seen_pivot = False

    for line in file:
        line = line.strip()

        if not line:
            # Skip empty or whitespace lines
            continue

        if not has_seen_pivot and '#' in line:
            # check for #-pivot line
            has_seen_pivot = True
            continue

        if not has_seen_pivot:
            # Read an argument line
            argument_name = line.strip()

            if validate:
                _validateArgument(argument_name, arguments)

            arguments.append(argument_name)

        elif validate and '#' in line:
            _reportInvalidInputFileAndExit(
                'TGF file contains more than one "#".')

        else:
            # Read an attack line
            attack = tuple(line.split())

            if validate:
                _validateAttack(attack, arguments, attacks, line)

            attacks.append(tuple(attack))

        if validate and not has_seen_pivot:
            _reportInvalidInputFileAndExit(
                'TGF file does not contain "#".')

    return arguments, attacks


def _parseAPX(file, validate=False):
    """Given an input file-like object encoded in the Aspartix format
    parse it and return the AF it describes in term of its components.

    Arguments:
        file {File} -- file-like object containing a Aspartix encoded AF

    Keyword Arguments:
        validate {bool} -- whether to validate the contents of the file
            (default: {False})

    Returns:
        Tuple[List[str],List[Tuple[str]]] -- tuple representation of the
            encoded AF]
    """

    arguments = []
    attacks = []
    # https://git.io/Jv6wD - Credit to alviano/pyglaf implementation for
    # the following regex pattern
    # TODO Make this pattern match 'att' and 'arg' respectively
    pattern = re.compile("(?P<type>\w+)\s*\((?P<args>[\w,\s]+)\)\.")

    for line in file:
        resolved_line = pattern.match(line)

        if not resolved_line:
            # Skip non apx lines
            # ? Should this throw 'Invalid formatting' error?
            continue

        line_type = resolved_line.group('type')

        if line_type == 'arg':
            # Read argument line e.g. 'arg(...).'
            argument_name = resolved_line.group('args')

            if validate:
                _validateArgument(argument_name, arguments)

            arguments.append(argument_name)

        elif line_type == 'att':
            # Read attack line e.g., 'att(...).'
            attack_wws = resolved_line.group('args').split(',')
            attack = [arg_name.strip() for arg_name in attack_wws]

            if validate:
                _validateAttack(attack, arguments, attacks, line.strip())

            attacks.append(attack)

    return arguments, attacks


_formats = {
    # List spported input formats and their parsing functions here.
    'tgf': _parseTGF,
    'apx': _parseAPX
}


def getFormats():
    return list(_formats.keys())


def parseInput(file_path, format='tgf', validate=False):
    """Parse the input file at the given path under a given supported
    encoding into a tuple AF representation.

    Arguments:
        file_path {str} -- path to the input file encoded in one of the
            supported formats/encodings

    Keyword Arguments:
        format {str} -- name of the format/encoding of the file at
            file_path (default: {'tgf'})
        validate {bool} -- decide whether to check the file at file_path
            for validity under the format (default: {False})

    Returns:
        Tuple[List[str],List[Tuple[str]]] -- tuple representation of the
            encoded AF]]
    """

    try:
        parsingFunction = _formats[format]
    except KeyError:
        sys.stderr.write(F'File format "{format}" is not supported!')
        sys.stderr.write('Use --formats to see the list of supported formats.')
        sys.stderr.flush()
        sys.exit(1)
    try:
        with open(file_path, 'r') as file:
            return parsingFunction(file, validate)
    except OSError as e:
        sys.stderr.write(e.strerror)
        sys.stderr.flush()
        sys.exit(1)


class _FormatsAction(argparse.Action):
    """Argparse action for listing supported formats."""

    def __call__(self, parser, namespace, values, option_string=None):
        print(formatOutput(getFormats(), sep=', '))
        sys.exit(0)


class _ProblemsAction(argparse.Action):
    """Argparse action for listing supported AF tasks."""

    def __call__(self, parser, namespace, values, option_string=None):
        print(formatOutput(tasks.getTasks(), sep=', '))
        sys.exit(0)


def _initialiseArgumentParser():
    """Initilise and return an Argparse parser object in complience to
    ICCMA Solver interface.

    Returns:
        argparse.ArgumentParser -- the argument parser for the AF sovler
    """

    parser = argparse.ArgumentParser()
    # Remove default argument group in the help message
    parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')
    required.add_argument('-p',
                          '--problemTask',
                          type=str,
                          help='Path to file containing a argumentation \
                          framework encding',
                          required=True,
                          choices=tasks.getTasks())

    required.add_argument('-f',
                          '--inputFile',
                          type=str,
                          required=True,
                          help='Path to input file encoding an framework')

    required.add_argument('-fo',
                          '--fileFormat',
                          type=str,
                          required=True,
                          choices=getFormats(),
                          help='Input file format')

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-a',
                          '--argument',
                          type=str,
                          metavar='<argumentname>',
                          help='Argument to check acceptance for')
    # Register the custom action to list supported formats
    parser.register('action', 'list_formats', _FormatsAction)
    optional.add_argument('--formats',
                          nargs=0,
                          action='list_formats',
                          help='List all supported input file \
                              formats and exit')

    parser.register('action', 'list_problems', _ProblemsAction)
    optional.add_argument('--problems',
                          nargs=0,
                          action='list_problems',
                          help='List all supported problems and exit')

    optional.add_argument('-v',
                          '--validate',
                          action='store_true',
                          help='Enable validation of the input \
                              file before parsing')

    return parser


def parseArguments():
    """Create the agument parser and return the parsed arguments
        according the ICCMA solver interface.

    Returns:
        argparse.Namespace -- parsed arguments object
    """

    parser = _initialiseArgumentParser()
    args = parser.parse_args()

    return args


def formatOutput(output, sep=',', prefix='', suffix=''):
    return F'{prefix}[{sep.join(output)}]{suffix}'


def outputDecision(accepted, suffix='\n'):
    """Given a decision task solution, output it according to the
        ICCMA specification.

    Arguments:
        accepted {bool} -- the solution to an AF decision problem

    Keyword Arguments:
        suffix {str} -- seperator to be printed after the solution
            (default: {'\n'})
    """

    sys.stdout.write(('YES' if accepted else 'NO') + suffix)
    sys.stdout.flush()


# Assign names to the output functions for seperate problem types.
outputDC = outputDS = outputDecision


def outputSE(ext, suffix='\n'):
    """Given a single enumeration task solution (extension), output it
        according to the ICCMA spesification.

    Arguments:
        ext {List[int]} -- extension which is a solution to a sigle
            enumeration problem (arguments as values);
            None indicates 'no solution'

    Keyword Arguments:
        suffix {str} -- seperator to be printed after the solution
            (default: {'\n'})
    """

    sys.stdout.write('NO') if ext is None \
        else sys.stdout.write(formatOutput(ext))
    sys.stdout.write(suffix)
    sys.stdout.flush()


def outputEE(ext_list, sep=',', suffix='\n'):
    """Given a full enumeration task solution (list of extensions),
        output it according to the ICCMA spesification.

    Arguments:
        ext_list {List[List[int]]} -- list of extensions which are the
            solution to the full enumeration problem (arguments as
            values)

    Keyword Arguments:
        sep {str} -- separator to be printed between each partial solution
            (default: {','})
        suffix {str} -- seperator to be printed after the solution
            (default: {'\n'})
    """

    sys.stdout.write('[')
    sys.stdout.write(sep.join([formatOutput(ext) for ext in ext_list]))
    sys.stdout.write(']')
    sys.stdout.write(suffix)
    sys.stdout.flush()


_outputFunctions = {'EE': outputEE,
                    'SE': outputSE,
                    'DC': outputDC,
                    'DS': outputDS}


def outputSolution(solution, task_type):
    """Given a solution to a task, output it according to the task type
        and the ICCMA spesification.

    Arguments:
        solution {List[List[int]] or List[int] or bool or None} -- the
            solution to be output
        task_type {str} -- string defining the problem task type.
    """

    try:
        _outputFunctions.get(task_type)(solution)
    except KeyError:
        sys.stderr.write(F'Task_type {task_type} is invalid!')
        sys.stderr.flush()
        sys.exit(1)
