"""Usage:
    __main__.py -f <file>

    Options:
    --problems    Show supported problem types
    --formtats    Show supported intput file formats
    -h --help     Show this screen.
    -v --version  Show version.
"""

from docopt import docopt
import networkx as nx
from saf.validate import parseTGF
from matplotlib import pyplot as plt


def main(args):
    if not any(args.values()):
        _showAbout()
        return 0

    file = arguments["<file>"]
    AF = parseTGF(file)
    nx.draw(AF, pos=nx.circular_layout(AF), node_color='r',
            edge_color='b', with_labels=True)
    plt.savefig('af.svg')


def _showAbout():
    ABOUT_INFO = "SAF v0.1\nDavid Simon Tetruashvili"
    print(ABOUT_INFO)


if __name__ == "__main__":
    arguments = docopt(__doc__, version='SAF v0.1')
    main(arguments)
