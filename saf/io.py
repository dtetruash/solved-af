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
    if len(argument.split()) > 1 or argument.find(',') != -1:
        _reportInvalidInputFileAndExit(
            F'Argument "{argument}" contains whitespace or comma.')

    if argument in arguments:
        _reportInvalidInputFileAndExit(
            F'Argument "{argument}" is defiled more than once.')


def _parseTGF(file, validate=False):

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
    arguments = []
    attacks = []
    # https://git.io/Jv6wD - Taken from alviano/pyglaf implementation
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
    'tgf': _parseTGF,
    'apx': _parseAPX
}


def getFormats():
    return list(_formats.keys())


def parseInput(file_path, format='tgf', validate=False):
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
    def __call__(self, parser, namespace, values, option_string=None):
        print(formatOutput(getFormats(), sep=', '))
        sys.exit(0)


class _ProblemsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(formatOutput(tasks.getTasks(), sep=', '))
        sys.exit(0)


def _initialiseArgumentParser():
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
    parser = _initialiseArgumentParser()
    args = parser.parse_args()

    return args


def formatOutput(output, sep=',', prefix='', suffix=''):
    return F'{prefix}[{sep.join(output)}]{suffix}'


def outputDecision(accepted, suffix='\n'):
    sys.stdout.write(('YES' if accepted else 'NO') + suffix)
    sys.stdout.flush()


# Rename for consistency
outputDC = outputDS = outputDecision


def outputSE(ext, suffix='\n'):
    sys.stdout.write('NO') if ext is None \
        else sys.stdout.write(formatOutput(ext))
    sys.stdout.write(suffix)
    sys.stdout.flush()


def outputEE(ext_list, sep=',', suffix='\n'):
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
    try:
        _outputFunctions.get(task_type)(solution)
    except KeyError:
        sys.stderr.write(F'Task_type {task_type} is invalid!')
        sys.stderr.flush()
        sys.exit(1)
