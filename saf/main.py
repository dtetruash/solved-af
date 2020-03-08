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
from saf.theories import DIMACSParser, CNFTheory, inLab, outLab, undLab
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

    # TODO Move to another place
    unique_theory = CNFTheory(
        lambda a, _: [[inLab(a), outLab(a), undLab(a)],
                      [-inLab(a), -outLab(a)],
                      [-inLab(a), -undLab(a)],
                      [-outLab(a), -undLab(a)]])

    in_complete_1 = CNFTheory(
        lambda a, f: [[-outLab(attacker)
                       for attacker in f.getAttackers(a)] + [inLab(a)]]
    )

    in_complete_2 = CNFTheory(
        lambda a, f: [[-inLab(a), outLab(attacked)]
                      for attacked in f.getAttackedBy(a)]
    )

    out_complete_1 = CNFTheory(
        lambda a, f: [[-inLab(attacker), outLab(a)]
                      for attacker in f.getAttackers(a)]
    )

    out_complete_2 = CNFTheory(
        lambda a, f: [[inLab(attacker)
                       for attacker in f.getAttackers(a)] + [-outLab(a)]]
    )

    theory_parser = DIMACSParser(unique_theory,
                                 in_complete_1,
                                 in_complete_2,
                                 out_complete_1,
                                 out_complete_2)

    dimacs = theory_parser.parse(AF)

    # TODO use stdin instead of file! Via a pipe!
    with NamedTemporaryFile(prefix='input_', delete=False, dir=Path('saf/tmp'), mode='w+') as i:
        i.write(dimacs)
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
