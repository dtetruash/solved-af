"""
usage: solved-af [-h] -p -f INPUTFILE - fo {tgf, apx}
                      [-a < argumentname >]
                      [--formats][--problems][-v]

required arguments:
  -p TASK, --problemTask TASK
  Path to file containing a argumentation framework encoding
  -f INPUTFILE, --inputFile INPUTFILE
  Path to input file encoding an framework
  -fo {tgf, apx}, --fileFormat {tgf, apx}
  Input file format

optional arguments:
  -a ARGUMENT, --argument ARGUMENT
  Argument to check acceptance for
  --formats             List all supported input file formats and exit
  --problems            List all supported problems and exit
  -v, --validate        Validate the input file before parsing
"""

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

import sys

import saf.io as io
import saf.tasks as tasks
from saf.framework import ListGraphFramework as Framework


NAME = 'Solved-AF'
VERSION = 0.1
AUTHOR = 'David Simon Tetruashvili'
DESCRIPTION = 'A SAT-reduction-based Abstract Argumentation Framework.'
LONG_DESCRIPTION = F"""{DESCRIPTION} Solved-AF is intended as an educational
                    library and is structured and written accordingly."""


def main():
    if len(sys.argv) == 1:
        _showAbout()
        sys.exit(0)

    args = io.parseArguments()

    arguments, attack_relation = io.parseInput(
        args.inputFile, format=args.fileFormat, validate=args.validate)

    af = Framework(arguments, attack_relation)

    # TODO encapsulate and made DRY
    task_name = args.problemTask.upper()
    task_type = task_name[:2]

    parsed_solution = None

    if args.argument is None:
        taskMethod = tasks.getTaskMethod(task_name, is_enumeration=True)
        solution = taskMethod(af)
        if task_type == 'SE' and solution is not None:
            parsed_solution = af.valuesToArguments(solution)
        elif task_type == 'EE':
            parsed_solution = [af.valuesToArguments(ext) for ext in solution]
    else:
        taskMethod = tasks.getTaskMethod(task_name, is_enumeration=False)
        parsed_solution = taskMethod(af, af.argumentToValue(args.argument))

    io.outputSolution(parsed_solution, task_type)


def _showAbout():
    ABOUT_INFO = F"{NAME} v{str(VERSION)}\n{AUTHOR}"
    print(ABOUT_INFO)


if __name__ == "__main__":
    main()
