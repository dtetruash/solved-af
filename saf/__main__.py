"""Usage:
    saf -f <file>

    Options:
    --problems    Show supported problem types
    --formtats    Show supported intput file formats
    -h --help     Show this screen.
    -v --version  Show version.
"""

import saf.io as io
import sys
from saf.framework import ListGraphFramework as Framework
# TODO May need to split saf.theories into a package
from saf.theories import CompleteLabelingDIMACSParser as CLDIMACSParser
from saf.theories import DIMACSParser
import saf.tasks as tasks
from subprocess import run, PIPE


def main():
    if len(sys.argv) == 1:
        _showAbout()
        sys.exit(0)

    args = io.parseArguments()

    file = args.inputFile
    file_format = args.fileFormat
    arguments, attacks = io.parseInput(
        file, format=file_format, validate=args.validate)

    taskMethod = tasks.getTaskMethod(args.problemTask.upper())

    AF = Framework(arguments, attacks)

    theory_parser = CLDIMACSParser

    sat_input = theory_parser.parse(AF)

    SAT_COMMAND = ['glucose', '-model', '-verb=0']
    unsatisfiable = False
    while not unsatisfiable:
        sat_solver = run(SAT_COMMAND, stdout=PIPE,
                         input=str(sat_input), encoding='ascii')
        solution = sat_solver.stdout.split('\n')[-2]
        unsatisfiable = sat_solver.returncode == 20
        if not unsatisfiable:
            extension = DIMACSParser.extractExtention(solution)
            print(AF.valuesToArguments(extension))
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
    main()
