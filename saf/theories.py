import abc
from saf.argument import Label
from typing import List, Callable, Generator, NewType
from saf.framework import FrameworkRepresentation as Framework


# TODO add caching to the variables generated

def _calculateLabelVar(arg_value: int, num_of_labels, label=Label.In) -> int:
    return num_of_labels * (arg_value - 1) + label


def labelVarToArg(label_var: int, num_of_labels) -> float:
    return (label_var // num_of_labels) + 1


_label_var_cache = {}


def _argToLabelVar(arg_value: int, label=Label.In) -> int:
    label_key = (int(label), arg_value)
    try:
        ret_val = _label_var_cache[label_key]
    except KeyError:
        label_var = _calculateLabelVar(arg_value, 3, label)
        _label_var_cache[label_key] = label_var
        ret_val = label_var

    return ret_val


def inLabelVariable(arg_value: int) -> int:
    return _argToLabelVar(arg_value, Label.In)


def outLabelVariable(arg_value: int) -> int:
    return _argToLabelVar(arg_value, Label.Out)


def undLabelVariable(arg_value: int) -> int:
    return _argToLabelVar(arg_value, Label.Und)


inLab = inLabelVariable
outLab = outLabelVariable
undLab = undLabelVariable


TheoryTemplate = NewType(
    'TheoryTemplate', Callable[[int, Framework], List[List[int]]])
TheoryRepresentation = NewType('TheoryRepresentation', List[List[int]])


class CNFTheory:
    """Representation of a boolean CNF theory as an object.
    As a list of disjunctive clauses.
    """

    def __init__(self, template: TheoryTemplate):
        super().__init__()
        # FIXME template should build a clause? Or the whole theory?
        self._template = template

    @classmethod
    def fromTemplateList(cls, templates: List[TheoryTemplate]) -> Generator:
        return (cls(template) for template in templates)

    @classmethod
    def fromTemplates(cls, *templates: TheoryTemplate) -> Generator:
        return (cls(template) for template in templates)

    def generate(self, argument_value: int,
                 framework: Framework) -> TheoryRepresentation:
        return self._template(argument_value, framework)

    def generateAll(self, argument_values: List[int],
                    framework: Framework) -> TheoryRepresentation:
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
        """Parse the given theories into a usable format to give to a
        solver as input.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parseCNFTheory(self, theory: List[List[int]]) -> str:
        """Parse the given theories into a usable format to give to a
        solver as input.
        """
        raise NotImplementedError

    @abc.abstractstaticmethod
    def extractExtention(sat_output: str) -> List[int]:
        raise NotImplementedError


class DIMACSHeader:
    def __init__(self, num_of_vars=0, num_of_clauses=0):
        self._vars = num_of_vars
        self._clauses = num_of_clauses

    def __str__(self):
        return F"p cnf {self._vars} {self._clauses}\n"

    def incrementClauses(self):
        self._clauses += 1

    def setClauses(self, num_of_clauses):
        self._clauses = num_of_clauses


# TODO FIXME Make this extent str via __new__
class DIMACSInput:
    def __init__(self, num_of_vars=0, num_of_clauses=0, content=''):
        self._header = DIMACSHeader(num_of_vars, num_of_clauses)
        self._content = content

    def __str__(self):
        return str(self._header) + self._content

    def addClause(self, dimacs_clause: str):
        self._content += dimacs_clause
        self._header.incrementClauses()

    def encode(self):
        return str(self)


class DIMACSParser(TheoryParser):
    """Given a set of CNF formulae will produce a DIMACS
    formated file encoding the given argumentation framework
    into a set of SAT theories.
    """

    def __init__(self, *theories: CNFTheory):
        super().__init__(*theories)

    def parseCNFTheory(self, theory: CNFTheory):
        clauses = [' '.join(str(x) for x in clause) +
                   ' 0' for clause in theory]
        return '\n'.join(clauses) + '\n'

    def parse(self, framework: Framework) -> DIMACSInput:
        # generate all theories in raw form,
        # count the number of clauses generated...

        raw_clauses = []
        # For each argument there is bool variable for each label
        # describing it.
        num_of_vars = len(framework) * len(Label)
        argument_values = framework.getArguments()
        for theory in self._theories:
            raw_clauses += theory.generateAll(argument_values, framework)

        num_of_clauses = len(raw_clauses)
        dimacs_content = self.parseCNFTheory(raw_clauses)

        return DIMACSInput(num_of_vars, num_of_clauses, dimacs_content)

    @staticmethod
    def extractExtention(sat_output: str) -> List[int]:
        model = [int(lab_var.strip())
                 for lab_var in sat_output.split(' ')[1:-1]]
        return[labelVarToArg(lab_var, 3) for lab_var in model
               if lab_var > 0 and abs(lab_var)
               in range(1, len(model), len(Label))]

    # FIXME Method doesn't tell what the labeling is.
    @staticmethod
    def extractLabeling(sat_output: str) -> List[int]:
        # FIXME Convert to list comprehension instead
        return list(filter(lambda x: x > 0, [int(lab_var) for lab_var
                                             in sat_output.split(' ')[1:-1]]))


"""
Theory model functions for encoding a full AF for the complete
extensions.

Each theory encoding functions take in the argument {a} they are
encoding into theories and the framework {f} containing said argument.
"""


def uniqueness_theory(a, _): return [[inLab(a), outLab(a), undLab(a)],
                                     [-inLab(a), -outLab(a)],
                                     [-inLab(a), -undLab(a)],
                                     [-outLab(a), -undLab(a)]]


def in_complete_theory_1(a, f): return [[-outLab(attacker)
                                         for attacker in f.getAttackersOf(a)]
                                        + [inLab(a)]]


def in_complete_theory_2(a, f): return [[-inLab(a), outLab(attacked)]
                                        for attacked in f.getAttackedBy(a)]


def out_complete_theory_1(a, f): return [[-inLab(attacker), outLab(a)]
                                         for attacker in f.getAttackersOf(a)]


def out_complete_theory_2(a, f): return [[inLab(attacker)
                                          for attacker in f.getAttackersOf(a)]
                                         + [-outLab(a)]]


# A parser instance for encoding complete extentions

complete_theories = CNFTheory.fromTemplates(uniqueness_theory,
                                            in_complete_theory_1,
                                            in_complete_theory_2,
                                            out_complete_theory_1,
                                            out_complete_theory_2)

CompleteLabelingDIMACSParser = DIMACSParser(*complete_theories)
