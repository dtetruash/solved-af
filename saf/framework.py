import abc
from typing import List, Set

import saf.utils as utils


class FrameworkRepresentation(metaclass=abc.ABCMeta):

    def __init__(self, arguments, attacks):
        super().__init__()
        self._values_to_arguments = arguments
        self._arguments_to_values = {arg: i for i,
                                     arg in enumerate(arguments, start=1)}
        self._args = self.argumentsToValues(arguments)
        self._atts = [[self.argumentToValue(arg)
                       for arg in attack] for attack in attacks]

    def argumentToValue(self, argument_name: str) -> int:
        return self._arguments_to_values[argument_name]

    def valueToArgument(self, argument_value: int) -> str:
        return self._values_to_arguments[argument_value - 1]

    def valuesToArguments(self, argument_values: List[int]) -> List[str]:
        return [self.valueToArgument(v) for v in argument_values]

    def argumentsToValues(self, argument_names: List[str]) -> List[int]:
        return [self.argumentToValue(v) for v in argument_names]

    def __iter__(self):
        return iter(self._args)

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'getAttackersOf') and
                callable(subclass.getAttackersOf) and
                hasattr(subclass, 'getAttackedBy') and
                callable(subclass.getAttackedBy) and
                hasattr(subclass, 'getAttackersOfSet') and
                callable(subclass.getAttackersOfSet) and
                hasattr(subclass, 'getAttackedBySet') and
                callable(subclass.getAttackedBySet) and
                hasattr(subclass, 'getArguments') and
                callable(subclass.getArguments) and
                hasattr(subclass, 'getAttacks') and
                callable(subclass.getAttacks) and
                hasattr(subclass, 'characteristic') and
                callable(subclass.characteristic) and
                hasattr(subclass, '__len__') and
                callable(subclass.__len__) or
                NotImplemented)

    @abc.abstractmethod
    def getAttackersOf(self, arg: int) -> List[int]:
        """Get a list of all arguments which attack of a given argument."""
        raise NotImplementedError

    @abc.abstractmethod
    def getAttackedBy(self, arg: int) -> List[int]:
        """Get a list of all arguments which are attacked by a given
        argument."""
        raise NotImplementedError

    @abc.abstractmethod
    def getArguments(self) -> List[int]:
        """Get a list of all arguments in the framework."""
        raise NotImplementedError

    @abc.abstractmethod
    def getAttacks(self) -> List[List[int]]:
        """Get a list of all attacks in the framework."""
        raise NotImplementedError

    @abc.abstractmethod
    def characteristic(self, argument_values_set: Set[int]) -> Set[int]:
        """The characteristic function F of the framework."""
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        """Get the number of arguments in the framework."""
        raise NotImplementedError


class ListGraphFramework(FrameworkRepresentation):
    """Framework representation via keeping a lists for each argument of
    arguments which it is attacking and is attacked by."""
    # TODO Add SCC and layer split support in construction

    def __init__(self, arguments, attacks):
        """Construct the framework from parsed and validated data.
        Where arguments is a list of named/numbered arguments."""
        super().__init__(arguments, attacks)
        self._node_list = [(set(), set()) for _ in range(len(self._args))]
        # TODO generalise the == to is?
        for (attacker, attacked) in self._atts:
            self._node_list[attacker - 1][0].add(attacked)
            self._node_list[attacked - 1][1].add(attacker)

        self.LENGTH = len(self._node_list)

    def __len__(self):
        return self.LENGTH

    def __str__(self):
        retStr = ""
        for i, (attacking, attacked_by) in enumerate(self._node_list):
            arg = self.valueToArgument(i)
            white_space = ' ' * len(arg)
            SEP = ', '
            def to_str_repr(vs): return SEP.join(self.valuesToArguments(vs))
            attacking_str, attacked_by_str = to_str_repr(
                attacking), to_str_repr(attacked_by)
            retStr += (
                f'{white_space} {attacking_str}\n'
                f'{white_space}\U0001f855\n'
                f'{arg}\n'
                f'{white_space}\U0001f854\n'
                f'{white_space} {attacked_by_str}\n\n'
            )
        return retStr

    def characteristic(self, argument_values):
        # ? Maybe use binary representations of the sets of arguments to
        # ? compair?

        # * Can use lookups in self._att? One by one instead
        # * of computing sets...

        # {B | ∃C ∈ Args. C attacks B}
        attacked_by_args = self.getAttackedBySet(argument_values)

        return {arg for arg in self
                if self.getAttackersOf(arg).issubset(attacked_by_args)}

    @staticmethod
    def _indexOf(arg_value):
        return arg_value - 1

    def getAttackedBy(self, arg):
        return self._node_list[self._indexOf(arg)][0]

    def getAttackersOf(self, arg):
        return self._node_list[self._indexOf(arg)][1]

    def getAttackedBySet(self, arg_set):
        return utils.flattenSet([self.getAttackedBy(arg) for arg in arg_set])

    def getAttackersOfSet(self, arg_set):
        return utils.flattenSet([self.getAttackersOf(arg) for arg in arg_set])

    def getArguments(self):
        return self._args

    def getAttacks(self):
        return self._atts


def extensionToInt(extension):
    # ? Maybe add caching?
    rep = 0
    for arg in extension:
        rep += 2**(arg-1)
    return rep


def isIncluded(extension, other):
    ext_rep = extensionToInt(extension)
    other_rep = extensionToInt(other)

    # ext_rep_b = bin(ext_rep)
    # other_rep_b = bin(other_rep)

    if ext_rep > other_rep:
        return False

    return other_rep & ext_rep == ext_rep


def getMinimal(extensions):
    extensions.sort(key=len)
    for ext in extensions:
        if all((isIncluded(ext, other) for other in extensions)):
            return ext


def generateMaximal(extensions):
    extensions = list(extensions)
    for ext in extensions:

        others = extensions[:]
        others.remove(ext)

        if all(not isIncluded(ext, other) for other in others):
            yield ext
