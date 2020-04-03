import abc
from typing import Callable, FrozenSet, Generator, List, NewType

import saf.utils as utils
from saf.argument import Label
from saf.framework import FrameworkRepresentation as Framework


def _calculateLabelVar(arg_value: int, num_of_labels, label=Label.In) -> int:
    return num_of_labels * (arg_value - 1) + label


def labelVarToArg(label_var: int, num_of_labels) -> float:
    return (label_var // num_of_labels) + 1


@utils.memoize
def inLabelVariable(arg_value: int) -> int:
    return _calculateLabelVar(arg_value, 3, Label.In)


@utils.memoize
def outLabelVariable(arg_value: int) -> int:
    return _calculateLabelVar(arg_value, 3, Label.Out)


@utils.memoize
def undLabelVariable(arg_value: int) -> int:
    return _calculateLabelVar(arg_value, 3, Label.Und)


@utils.memoize
def stableInLabelVariable(arg_value: int) -> int:
    return _calculateLabelVar(arg_value, 2, Label.In)


@utils.memoize
def stableOutLabelVariable(arg_value: int) -> int:
    return _calculateLabelVar(arg_value, 2, Label.Out)


inLab = inLabelVariable
outLab = outLabelVariable
undLab = undLabelVariable

stbInLab = stableInLabelVariable
stbOutLab = stableOutLabelVariable


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

    def addSingleClause(self, dimacs_clause: str):
        self._content += dimacs_clause
        self._header.incrementClauses()

    def encode(self):
        return str(self)


class DIMACSParser(TheoryParser):
    """Given a set of CNF formulae will produce a DIMACS
    formated file encoding the given argumentation framework
    into a set of SAT theories.
    """

    def __init__(self, *theories: CNFTheory, vars_per_argument=len(Label)):
        super().__init__(*theories)
        self.vars_per_argument = vars_per_argument

    @classmethod
    def parseCNFTheory(cls, theory: CNFTheory):
        clauses = [cls.parseClause(clause) for clause in theory]
        return '\n'.join(clauses) + '\n'

    @staticmethod
    def parseClause(clause: List[int]):
        return ' '.join(str(lab_var) for lab_var in clause) + ' 0'

    def parse(self, framework: Framework) -> DIMACSInput:
        # generate all theories in raw form,
        # count the number of clauses generated...

        raw_clauses = []
        # For each argument there is a bool variable for each label
        # describing it.
        num_of_vars = len(framework) * self.vars_per_argument
        argument_values = framework.getArguments()
        for theory in self._theories:
            raw_clauses += theory.generateAll(argument_values, framework)

        num_of_clauses = len(raw_clauses)
        dimacs_content = self.parseCNFTheory(raw_clauses)

        return DIMACSInput(num_of_vars, num_of_clauses, dimacs_content)

    def extractExtention(self, assignment: List[int]) -> FrozenSet[int]:
        # FIXME need a better way to check for being an in-label var.
        if self.vars_per_argument > 1:
            in_labels = set(range(1, len(assignment), self.vars_per_argument))

            extension = []

            for lab_var in assignment:
                if abs(lab_var) in in_labels and lab_var > 0:
                    extension.append(labelVarToArg(lab_var, len(Label)))
            return frozenset(extension)
        else:
            return frozenset(self.extractPositiveLiterals(assignment))

    @staticmethod
    def extractPositiveLiterals(assignment: List[int]) -> List[int]:
        return [lab_var for lab_var in assignment if lab_var > 0]


"""
Theory model functions for encoding a full AF for the complete
extensions.

Each theory encoding functions take in the argument {a} they are
encoding into theories and the framework {f} containing said argument.
"""


def uniqueness_theory(a, _):
    return [[inLab(a), outLab(a), undLab(a)],
            [-inLab(a), -outLab(a)],
            [-inLab(a), -undLab(a)],
            [-outLab(a), -undLab(a)]]


def complete_in_theory_1(a, f):
    return [[-outLab(attacker)
             for attacker in f.getAttackersOf(a)]
            + [inLab(a)]]


def complete_in_theory_2(a, f):
    return [[-inLab(a), outLab(attacked)]
            for attacked in f.getAttackedBy(a)]


def complete_out_theory_1(a, f):
    return [[-inLab(attacker), outLab(a)]
            for attacker in f.getAttackersOf(a)]


def complete_out_theory_2(a, f):
    return [[inLab(attacker)
             for attacker in f.getAttackersOf(a)]
            + [-outLab(a)]]


# A parser instance for encoding complete extentions

complete_theories = CNFTheory.fromTemplates(uniqueness_theory,
                                            complete_in_theory_1,
                                            complete_in_theory_2,
                                            complete_out_theory_1,
                                            complete_out_theory_2)

completeLabelingParser = DIMACSParser(*complete_theories)


"""
Theory model functions for encoding a full AF for the stable
extensions.

Each theory encoding functions take in the argument {a} they are
encoding into theories and the framework {f} containing said argument.
"""


# def stable_uniqueness_theory(a, _):
#     return [[stbInLab(a), stbOutLab(a)],
#             [-stbInLab(a), -stbOutLab(a)]]


def stable_in_theory(a, f):
    clause = [attacker for attacker in f.getAttackersOf(a)]
    clause.append(a)
    return [clause]


def stable_out_theory(a, f):
    return [[-attacker, -a]
            for attacker in f.getAttackersOf(a)]


stable_theories = CNFTheory.fromTemplates(stable_in_theory, stable_out_theory)

stableLabellingParser = DIMACSParser(*stable_theories, vars_per_argument=1)
