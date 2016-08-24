import re
import copy
import pickle
from reparm_input import ReparmInput
from parameters import Parameters
from coordinates import Coordinates
from gaussian_input import GaussianInput
from gaussian_output import GaussianOutput
from parameter_group import ParameterGroup
from header import Header


class ReparmData():
    def __init__(self, file_name):
        self.reparm_input = ReparmInput(file_name)
        self.best_fitness = None
        self.original_fitness = None
        # This is a list of gaussian outputs
        self.high_level_outputs = None
        # This is of type param_group
        self.best_am1_individual = None
        # Store Jobs for scikit-learn
        self.observations = []
        self.targets = []

    def copy(self):
        return copy.deepcopy(self)

    def reference(self):
        return self

    def save(self):
        pickle.dump(self, open("reparm.dat", "wb"))

    def load(self):
        lf = pickle.load(open("reparm.dat", 'rb'))
        self.best_fitness = lf.best_fitness
        self.original_fitness = lf.original_fitness
        self.high_level_outputs = lf.high_level_outputs
        self.best_am1_individual = lf.best_am1_individual
        self.observations = lf.observations
        self.targets = lf.targets

