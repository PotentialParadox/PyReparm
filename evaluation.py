from reparm_data import ReparmData
import numpy as np
import math
from random import random
from copy import deepcopy
from gaussian import run_gaussian


class Evaluator:
    def __init__(self, reparm_data=None, goal=None):
        self.reparm_data = ReparmData.reference(reparm_data)
        self.std = None
        self.goal = goal

    # Evaluates an individual
    def eval(self, am1):
        param_group = deepcopy(self.reparm_data.best_am1_individual)
        hlt = deepcopy(self.reparm_data.high_level_outputs)
        param_group.set_pfloats(am1)
        gouts = run_gaussian(parameter_group=param_group)
        if not gouts:
            return None
        energy_fitness = self.energy_fitness(gouts)
        dipole_fitness = self.dipole_fitness(gouts)
        current = [energy_fitness, dipole_fitness]
        self.reparm_data.targets.append(current)
        self.update_std()
        self.update_best()
        std_current = self.standardize(current)
        total_fitness = np.sum(np.square(std_current))

        return total_fitness, energy_fitness, dipole_fitness

    def energy_fitness(self, am1):
        hlt = self.reparm_data.high_level_outputs
        hlt_energy_differences = []
        for i in range(1, len(hlt)):
            hlt_energy_differences.append(hlt[i].ground_energy - hlt[i-1].ground_energy)

        am1_energy_differences = []
        for i in range(1, len(am1)):
            am1_energy_differences.append(am1[i].ground_energy - am1[i-1].ground_energy)

        sum_of_squares = 0
        for am1_diff, hlt_diff in zip(am1_energy_differences, hlt_energy_differences):
            sum_of_squares += math.pow(am1_diff - hlt_diff, 2)

        return sum_of_squares

    def dipole_fitness(self, am1):
        hlt = self.reparm_data.high_level_outputs
        hlt_dipoles = []
        for i in hlt:
            hlt_dipoles.extend(i.dipole)

        am1_dipoles = []
        for i in am1:
            am1_dipoles.extend(i.dipole)

        sum_of_squares = 0
        for am1_d, hlt_d in zip(am1_dipoles, hlt_dipoles):
            sum_of_squares += math.pow(am1_d - hlt_d, 2)

        return sum_of_squares

    def update_std(self):
        if len(self.reparm_data.targets) > 2:
            tgs = np.array(self.reparm_data.targets)
            self.std = np.std(tgs, axis=0)

    def standardize(self, list_object):
        if self.std is not None:
            return np.array(list_object) / self.std
        return np.array(list_object)

    def update_best(self):
        if self.reparm_data.best_fitness is not None and self.std is not None:
            # print("starting with", self.reparm_data.best_fitness)
            std_best = self.standardize(self.reparm_data.best_fitness[1:])
            self.reparm_data.best_fitness[0] = np.sum(np.square(std_best))
            # print("best is now", self.reparm_data.best_fitness)
