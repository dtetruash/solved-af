def flatten(list_to_flatten):
    # https://stackoverflow.com/a/952952/5065263
    return [item for sublist in list_to_flatten for item in sublist]


def flattenSet(set_to_flatten):
    # https://stackoverflow.com/a/952952/5065263
    return {item for sublist in set_to_flatten for item in sublist}


def memoize(func):
    # https://dbader.org/blog/python-memoization
    cache = {}

    def memoized_func(*args):
        try:
            return cache[args]
        except KeyError:
            result = func(*args)
            cache[args] = result
            return result

    return memoized_func
