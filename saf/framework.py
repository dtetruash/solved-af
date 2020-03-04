import abc
from typing import List


class FrameworkRepresentation(metaclass=abc.ABCMeta):

    def __init__(self, arguments, attacks):
        super().__init__()
        self._values_to_arguments = arguments
        self._arguments_to_values = {arg: i for i, arg in enumerate(arguments)}
        # TODO Probably a better way to do this? Populate as you convert?
        self._args = self.argumentsToValues(arguments)
        self._atts = [[self.argumentToValue(arg)
                       for arg in attack] for attack in attacks]

    def argumentToValue(self, argument_name: str) -> int:
        return self._arguments_to_values[argument_name]

    def valueToArgument(self, argument_value: int) -> str:
        return self._values_to_arguments[argument_value]

    def valuesToArguments(self, argument_values: List[int]) -> List[str]:
        return [self.valueToArgument(v) for v in argument_values]

    def argumentsToValues(self, argument_names: List[str]) -> List[int]:
        return [self.argumentToValue(v) for v in argument_names]

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'getAttackers') and
                callable(subclass.getAttackers) and
                hasattr(subclass, 'getAttackedBy') and
                callable(subclass.getAttackedBy) and
                hasattr(subclass, 'getArguments') and
                callable(subclass.getArguments) and
                hasattr(subclass, '__len__') and
                callable(subclass.__len__) or
                NotImplemented)

    @abc.abstractmethod
    def getAttackers(self, arg: int) -> List[int]:
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
        self._node_list = []
        for argument in self._args:
            # TODO generalise the == to is?
            attacked_by = [attacker for (attacker, attacked)
                           in self._atts if argument == attacked]
            attacking = [attacked for (attacker, attacked)
                         in self._atts if argument == attacker]

            self._node_list.append([attacking, attacked_by])

        self.len = len(self._node_list)

    def __len__(self):
        return self.len

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
                f'{white_space}\U0001f856\n'
                f'{white_space} {attacked_by_str}\n\n'
            )
        return retStr

    @staticmethod
    def _indexOf(arg):
        return arg - 1

    def getAttackedBy(self, arg):
        return self._node_list[self._indexOf(arg)][0]

    def getAttackers(self, arg):
        return self._node_list[self._indexOf(arg)][1]

    def getArguments(self):
        return self._args

    def getAttacks(self):
        return self._atts
