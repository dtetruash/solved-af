from enum import IntEnum


class Label(IntEnum):
    In = 1
    Out = 2
    Und = 3


class Argument:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def setValue(self, new_value):
        self.value = new_value


class LabeledArgument(Argument):
    def __init__(self, name):
        super().__init__(name)
        self.label = Label.Und
        self.attacks = {}

    def getAttacked(self):
        return self.attacks

    # TODO Need to cache this so not to compute it over and over
    def getAttackers(self):
        pass
