import networkx as nx
from argument import Label
import re


ERR_INVALID_INPUT = "Input TFG Invalid: "


def parseTGF(file):

    Af = nx.DiGraph()
    # check for '#'
    # TODO improve by checking lyzily
    with open(file) as in_file:
        hashCount = 0

        for line in in_file:
            if "#" in line:
                hashCount += 1

        if hashCount == 0:
            raise IOError(ERR_INVALID_INPUT + "# missing!")
        elif hashCount > 1:
            raise IOError(ERR_INVALID_INPUT + "too many #s!")

    with open(file) as in_file:
        lines = list(filter(None, (line.rstrip() for line in in_file)))
        pivot_index = lines.index("#")
        arg_declarations = lines[:pivot_index]
        att_declarations = lines[pivot_index+1:]

        if len(arg_declarations) == 0:
            raise IOError(ERR_INVALID_INPUT + "no arguments declared!")

        # TODO Maybe store refs to Argument objects?
        # Add arguents to AF
        for arg in arg_declarations:
            if arg not in Af.nodes():
                Af.add_node(arg, lab=Label.Und)
            else:
                raise IOError(ERR_INVALID_INPUT + F"argument {arg} declared \
                    more than once!")

        for att in att_declarations:
            # Check if line conforms to format
            if not re.match(r"^(\w+\ \w+)$", att):
                raise IOError(ERR_INVALID_INPUT + F"attack relation \"{att}\" \
                    does not conform to TGF standard!")
            # Check if both arguments exist
            arg1, arg2 = att.split(" ")
            if arg1 not in Af.nodes() or arg2 not in Af.nodes():
                raise IOError(ERR_INVALID_INPUT + F"undeclaired arguments in \
                    attack \"{att}\"!")
            # Check if there already is such an edge in AF
            if (arg1, arg2) in Af.edges():
                raise IOError(ERR_INVALID_INPUT + F"attack \"{att}\" is declared \
                    more than once!")
            # Add the edge
            Af.add_edge(arg1, arg2)

    return Af
