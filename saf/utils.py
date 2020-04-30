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

"""This method provides some misc. untilities to solved-af."""


def flatten(list_to_flatten):
    # Credit to https://stackoverflow.com/a/952952/5065263
    return [item for sublist in list_to_flatten for item in sublist]


def flattenSet(set_to_flatten):
    # Credit to https://stackoverflow.com/a/952952/5065263
    return {item for sublist in set_to_flatten for item in sublist}


def memoize(func):
    # Credit to https://dbader.org/blog/python-memoization
    cache = {}

    def memoized_func(*args):
        try:
            return cache[args]
        except KeyError:
            result = func(*args)
            cache[args] = result
            return result

    return memoized_func
