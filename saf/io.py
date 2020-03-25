import saf.tasks as tasks
import argparse
import sys
import re


def _reportInvalidInputFileAndExit(message):
    print(F'Invalid input file!')
    print(message)
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


def _parseTGF(file_path, validate=False):

    arguments = []
    attacks = []

    with open(file_path, 'r') as i:
        has_seen_pivot = False

        for line in i:
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


def _parseAPX(file_path, validate=False):
    arguments = []
    attacks = []
    # https://git.io/Jv6wD - Taken from alviano/pyglaf implementation
    # TODO Make this pattern match 'att' and 'arg' respectively
    pattern = re.compile("(?P<type>\w+)\s*\((?P<args>[\w,\s]+)\)\.")

    with open(file_path, 'r') as i:
        for line in i:
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
        return parsingFunction(file_path, validate)
    except KeyError:
        print(F'File format "{format}" is not supported!')
        print('Use --formats to see the list of supported formats.')
        sys.exit(1)


def _formatOutputFromList(str_list):
    return F"[{', '.join(str_list)}]"


class _FormatsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_formatOutputFromList(getFormats()))
        sys.exit(0)


class _ProblemsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_formatOutputFromList(tasks.getTasks()))
        sys.exit(0)


# TODO Move help to a constants file..?
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

    optional.add_argument('-a',
                          '--argument',
                          type=str,
                          metavar='<argumentname>',
                          help='Argument to check acceptance for')

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


def outputExtension(ext, sep=',', prefix='', suffix='\n'):
    sys.stdout.write(F'{prefix}[{sep.join(ext)}]{suffix}')


def outputDecision(accepted, suffix='\n'):
    sys.stdout.write(('YES' if accepted else 'NO') + suffix)
    sys.stdout.flush()


# Rename for consistency
outputDC = outputDS = outputDecision


def outputSE(ext, suffix='\n'):
    sys.stdout.write('NO') if ext is None else outputExtension(ext)
    sys.stdout.write(suffix)
    sys.stdout.flush()

# ! FIXME Might be better to have a single print function and multiple
# ! formatting functions


def outputEE(ext_list, suffix='\n'):
    sys.stdout.write('[\n')
    for ext in ext_list:
        outputExtension(ext, prefix='\t')
    sys.stdout.write(']')
    sys.stdout.write(suffix)
    sys.stdout.flush()
