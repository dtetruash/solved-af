"""Usage:
    saf -f <file>

    Options:
    --problems    Show supported problem types
    --formtats    Show supported intput file formats
    -h --help     Show this screen.
    -v --version  Show version.
"""

from docopt import docopt
from saf.validate import parseTGF
from saf.framework import ListGraphFramework as Framework
# TODO May need to split saf.theories into a package
from saf.theories import CompleteLabelingDIMACSParser, DIMACSParser
from subprocess import run, PIPE


def main(args):
    if not any(args.values()):
        _showAbout()
        return 0

    file = args["<file>"]
    # TODO Add apx support
    arguments, attacks = parseTGF(file)

    AF = Framework(arguments, attacks)

    theory_parser = CompleteLabelingDIMACSParser

    sat_input = theory_parser.parse(AF)

    SAT_COMMAND = ['glucose', '-model', '-verb=0']
    while True:
        sat_solver = run(SAT_COMMAND, stdout=PIPE,
                         input=str(sat_input), encoding='ascii')
        solution = sat_solver.stdout.split('\n')[-2]
        if sat_solver.returncode == 20:
            break
        print(solution)
        # TODO Encapsulate in a method
        solution_labeling = DIMACSParser.extractLabeling(solution)
        solution_negation_clause = [[str(-lab_var) for lab_var
                                     in solution_labeling]]
        solution_negation_dimacs = theory_parser.parseCNFTheory(
            solution_negation_clause)
        sat_input.addClause(solution_negation_dimacs)


def _showAbout():
    ABOUT_INFO = "SAF v0.1\nDavid Simon Tetruashvili"
    print(ABOUT_INFO)


if __name__ == "__main__":
    args = docopt(__doc__, version='SAF v0.1')
    # print('Program args: ', args)
    main(args)
