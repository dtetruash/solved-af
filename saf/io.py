from saf.formats import InputFormats
import argparse


def parseArguments(*args, **kwargs):
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-p', '--problemTask',
                          help='Path to file containing a argumentation \
                          framework encding', required=True)
    required.add_argument('-f', '--inputFile', type=str,
                          help='Path to input file encoding an framework', required=True)
    required.add_argument('-fo', '--fileFormat',  type=str,
                          choices=['tgf', 'apx'], help='Input file format', required=True)
    optional.add_argument('--formats', action='store_true',
                          help='List all supported input file formats and exit')
    optional.add_argument('--problems', action='store_true',
                          help='List all supported problems and exit')
    optional.add_argument('-a', '--argument', metavar='<argumentname>',
                          help='Argument to check acceptance for')
    optional.add_argument('-v', '--validation', action='store_true',
                          help='Enable validation of the input file before parsing')

    args = parser.parse_args()
    print(args)

    return args


def formatExtention(extention, format):
    pass


def parseInput(file, format=InputFormats.TGF):
    return parseTGF(file) if format == InputFormats.TGF else parseAPX(file)


def parseTGF(file):

    arguments = []
    attacks = []

    with open(file, 'r') as i:
        has_defined_args = False
        for line in i:
            line = line.strip()
            if not line:
                continue
            if line == '#':
                has_defined_args = True
            elif not has_defined_args:
                arguments.append(line)
            else:
                attack = line.split()
                attacks.append(attack)

    return arguments, attacks


def parseAPX(file):
    raise NotImplementedError
