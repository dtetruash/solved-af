import re


# TODO Move to constants file
ERR_INVALID_INPUT = "Input TFG Invalid: "


def parseTGF(file):

    # TODO Maybe arguments would be better as a name -> value dict..?
    arguments = []
    attacks = []

    # check for '#'
    with open(file) as in_file:
        hashCount = 0

        for line in in_file:
            if "#" in line:
                hashCount += 1

        if hashCount == 0:
            raise IOError(ERR_INVALID_INPUT + "# missing!")
        elif hashCount > 1:
            raise IOError(ERR_INVALID_INPUT + "too many '#' in TFG file!")

    with open(file) as in_file:
        lines = list(filter(None, (line.rstrip() for line in in_file)))
        pivot_index = lines.index("#")
        arg_declarations = lines[:pivot_index]
        att_declarations = lines[pivot_index+1:]

        if len(arg_declarations) == 0:
            raise IOError(ERR_INVALID_INPUT + "no arguments declared!")

        # TODO Maybe store refs to Argument objects?
        # Add arguments to AF
        for arg_name in arg_declarations:
            if arg_name not in arguments:
                arguments.append(arg_name)
            else:
                raise IOError(ERR_INVALID_INPUT + F"argument {arg_name} declared \
                    more than once!")

        for att in att_declarations:
            # Check if line conforms to format
            if not re.match(r"^(\w+\ \w+)$", att):
                raise IOError(ERR_INVALID_INPUT + F"attack relation \"{att}\" \
                    does not conform to TGF standard!")
            # Check if both arguments exist
            arg1, arg2 = att.split(" ")
            # TODO find args by name!
            # This is wasteful as is runs in O(n). The lookup can be O(1) via
            # hash-tables or similar.
            if arg1 not in arguments or arg2 not in arguments:
                raise IOError(ERR_INVALID_INPUT + F"undeclared arguments in \
                    attack \"{att}\"!")
            attack = (arg1, arg2)
            if attack in attacks:
                raise IOError(ERR_INVALID_INPUT + F"attack \"{att}\" is declared \
                    more than once!")
            # Add the edge
            # TODO Find arguments by name and pass the reference to the
            # respective Argument object from the arguments list
            attacks.append(attack)
    return arguments, attacks
