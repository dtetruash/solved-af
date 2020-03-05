import abc
from saf.argument import Label
from typing import List
from saf.framework import FrameworkRepresentation as Framework


def _argLabelVariable(arg_value: int, label=Label.In) -> int:
    return 3 * (arg_value - 1) + label


def inLabelVariable(arg_value: int) -> int:
    return _argLabelVariable(arg_value, Label.In)


def outLabelVariable(arg_value: int) -> int:
    return _argLabelVariable(arg_value, Label.Out)


def undLabelVariable(arg_value: int) -> int:
    return _argLabelVariable(arg_value, Label.Und)


inLab = inLabelVariable
outLab = outLabelVariable
undLab = undLabelVariable


class CNFTheory:
    """Representation of a boolean CNF theory as an object.
    As a list of disjunctive clauses.
    """

    def __init__(self, template):
        super().__init__()
        self._template = template

    def generate(self, argument_value: int,
                 framework: Framework) -> List[List[int]]:
        ret_val = self._template(argument_value, framework)
        return ret_val

    def generateAll(self, argument_values: List[int], framework: Framework) -> List[List[int]]:
        ret_cnf = []
        for arg_val in argument_values:
            ret_cnf += self.generate(arg_val, framework)
        return ret_cnf


class TheoryParser(metaclass=abc.ABCMeta):

    def __init__(self, *theories):
        super().__init__()
        self._theories = theories

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'parse') and
                callable(subclass.parse) and
                hasattr(subclass, 'parseCNFTheory') and
                callable(subclass.parseCNFTheory) or
                NotImplemented)

    @abc.abstractmethod
    def parse(self, framework: Framework) -> str:
        """Parse the given theories into a usable format to give to a solver as input.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parseCNFTheory(self, theory: List[List[int]]) -> str:
        """Parse the given theories into a usable format to give to a solver as input.
        """
        raise NotImplementedError


class DIMACSParser(TheoryParser):
    """Given a set of CNF formulae will produce a DIMACS
    formated file encoding the given argumentation framework
    into a set of SAT theories.
    """

    def __init__(self, *theories: CNFTheory):
        super().__init__(*theories)

    def parseCNFTheory(self, theory: CNFTheory):
        print(theory)
        return '\n'.join([' '.join(str(x) for x in clause) + ' 0' for clause in theory])

    def parse(self, framework):
        # generate all theories in raw form,
        # count the number of clauses generated...

        raw_clauses = []
        # For each argument there is bool variable for each label
        # describing it.
        num_of_vars = len(framework) * len(Label)
        num_of_clauses = 0
        argument_values = framework.getArguments()
        for theory in self._theories:
            new_clauses = theory.generateAll(argument_values, framework)
            num_of_clauses += len(new_clauses)
            raw_clauses += new_clauses

        parsed_dimacs = f"p cnf {num_of_vars} {num_of_clauses}\n"
        parsed_dimacs += self.parseCNFTheory(raw_clauses)

        return parsed_dimacs
