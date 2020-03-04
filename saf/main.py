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


def main(args):
    if not any(args.values()):
        _showAbout()
        return 0

    file = args["<file>"]
    # TODO Add apx support
    arguments, attacks = parseTGF(file)
    AF = Framework(arguments, attacks)
    print('Representation:\n', AF)


def _showAbout():
    ABOUT_INFO = "SAF v0.1\nDavid Simon Tetruashvili"
    print(ABOUT_INFO)


if __name__ == "__main__":
    args = docopt(__doc__, version='SAF v0.1')
    print('Program args: ', args)
    main(args)
