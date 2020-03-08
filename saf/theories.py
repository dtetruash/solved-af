import abc
from saf.argument import Label
from typing import List, Tuple
from saf.framework import FrameworkRepresentation as Framework


# TODO add caching to the variables generated

def _calculateLabelVar(arg_value: int, label=Label.In) -> int:
    return len(Label) * (arg_value - 1) + label


label_var_cache = {}


def _argToLabelVar(arg_value: int, label=Label.In) -> int:
    label_key = f'{str(label)}-{str(arg_value)}'
    if label_key not in label_var_cache:
        label_var = _calculateLabelVar(arg_value, label)
        label_var_cache[label_key] = label_var
        return label_var
    else:
        return label_var_cache[label_key]


def inLabelVariable(arg_value: int) -> int:
    return _argToLabelVar(arg_value, Label.In)


def outLabelVariable(arg_value: int) -> int:
    return _argToLabelVar(arg_value, Label.Out)


def undLabelVariable(arg_value: int) -> int:
    return _argToLabelVar(arg_value, Label.Und)


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
                callable(subclass.parseCNFTheory) and
                hasattr(subclass, 'extractExtention') and
                callable(subclass.extractExtention) or
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

    @abc.abstractstaticmethod
    def extractExtention(sat_output: str) -> List[int]:
        raise NotImplementedError


class DIMACSParser(TheoryParser):
    """Given a set of CNF formulae will produce a DIMACS
    formated file encoding the given argumentation framework
    into a set of SAT theories.
    """

    def __init__(self, *theories: CNFTheory):
        super().__init__(*theories)

    def parseCNFTheory(self, theory: CNFTheory):
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

    @staticmethod
    def extractExtention(sat_output: str) -> List[int]:
        model = [int(lab_var) for lab_var in sat_output.split(' ')[1:-1]]
        return[lab_var for lab_var in model
               if lab_var > 0 and abs(lab_var)
               in range(1, len(model), len(Label))]

    @staticmethod
    def extractLabeling(sat_output: str) -> List[int]:
        return list(filter(lambda x: x > 0, [int(lab_var) for lab_var
                                             in sat_output.split(' ')[1:-1]]))
