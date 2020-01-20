"""Usage: 
    saf.py
    saf.py (-p <task> -f <file>) --fo <fileformat> [-a <additional_parameter>]

    Options:
    --problems    Show supported problem types
    --formtats    Show supported intput file formats
    -h --help     Show this screen.
    -v --version  Show version.
"""
from docopt import docopt

def main(args):
    print(args)


if __name__ == "__main__":
    arguments = docopt(__doc__, version='SAF v0.1')
    main(arguments)