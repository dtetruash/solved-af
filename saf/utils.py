def flatten(list_to_flatten):
    # https://stackoverflow.com/a/952952/5065263
    return [item for sublist in list_to_flatten for item in sublist]


def flattenSet(set_to_flatten):
    # https://stackoverflow.com/a/952952/5065263
    return {item for sublist in set_to_flatten for item in sublist}
