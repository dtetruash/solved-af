from enum import Enum


class Label(Enum):
    In = 1
    Out = 2
    Und = 3


class Argument():
    def __init__(self, name):
        self.name = name
        self.label = Label.Und
        self.attacks = {}

    def getAttacked(self):
        return self.attacks

    # TODO Need to cache this so not to compute it over and over
    def getAttackers(self):
        pass