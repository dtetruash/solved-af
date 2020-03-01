import abc
from typing import List, Tuple


class FrameworkRepresentation(metaclass=abc.ABCMeta):
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
    def getAttacks(self) -> List[Tuple[int, int]]:
        """Get a list of all attacks in the framework."""
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        """Get the number of arguments in the framework."""
        raise NotImplementedError


class _ListGraphArgument:
    def __init__(self, argument, attacks):
        super().__init__()
        self.attacked_by = [attacker for (attacker, attacked)
                            in attacks if attacked == argument]
        self.attacking = [attacked for (attacker, attacked)
                          in attacks if attacker == argument]


class ListGraphFramework(FrameworkRepresentation):
    """Framework representation via keeping a lists for each argument of
    arguments which it is attacking and is attacked by."""
    # TODO Add SCC and layer split support in construction

    def __init__(self, arguments, attacks):
        """Construct the framework from parsed and validated data.
        Where arguments is a list of named/numbered arguments."""
        super().__init__()
        self._args = arguments
        self._atts = attacks
        self._graph = []

        for argument in arguments:
            # TODO generalise the == to is?
            attacked_by = [attacker for (attacker, attacked)
                           in attacks if argument == attacked]
            attacking = [attacked for (attacker, attacked)
                         in attacks if argument == attacker]

            self._graph.append((attacking, attacked_by))

        self.len = len(self._graph)

    def __len__(self):
        return self.len

    @classmethod
    def _indexOf(cls, arg):
        return arg - 1

    def getAttackedBy(self, arg):
        return self._graph[self._indexOf(arg)][0]

    def getAttackers(self, arg):
        return self._graph[self._indexOf(arg)][1]

    def getArguments(self):
        return self._args

    def getAttacks(self):
        return self._atts
