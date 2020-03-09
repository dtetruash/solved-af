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
import subprocess
from tempfile import NamedTemporaryFile
from pathlib import Path


def main(args):
    if not any(args.values()):
        _showAbout()
        return 0

    file = args["<file>"]
    # TODO Add apx support
    arguments, attacks = parseTGF(file)

    AF = Framework(arguments, attacks)

    theory_parser = CompleteLabelingDIMACSParser

    sat_dimacs_input = theory_parser.parse(AF)

    # TODO use stdin instead of file! Via a pipe!
    # TODO Move to 'Generate complete extensions' part of the solver
    with NamedTemporaryFile(prefix='input_', delete=False, dir=Path('saf/tmp'),
                            mode='w+') as i:
        i.write(sat_dimacs_input)
        i.flush()
        while True:
            glucose_out = subprocess.run(
                ['glucose',
                    Path(i.name),
                    '-model',
                    '-verb=0'],
                capture_output=True).stdout.decode('ASCII').split('\n')[-2]
            print(glucose_out)
            if glucose_out == 's UNSATISFIABLE':
                break
            found_solution_negation_clause = theory_parser.parseCNFTheory([
                [str(-lab_var) for lab_var
                 in DIMACSParser.extractLabeling(glucose_out)]])
            i.write(found_solution_negation_clause)
            i.flush()


def _showAbout():
    ABOUT_INFO = "SAF v0.1\nDavid Simon Tetruashvili"
    print(ABOUT_INFO)


if __name__ == "__main__":
    args = docopt(__doc__, version='SAF v0.1')
    # print('Program args: ', args)
    main(args)
