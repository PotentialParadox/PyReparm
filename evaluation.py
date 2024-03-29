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
        nproc = self.reparm_data.reparm_input.number_processors
        gouts = run_gaussian(parameter_group=param_group, number_processors=nproc)
        if not gouts:
            return None
        energy_fitness = self.energy_fitness(gouts)
        dipole_fitness = self.dipole_fitness(gouts)
        current = [energy_fitness, dipole_fitness]
        if self.aebo(current):
            self.reparm_data.targets.append(current)
        self.update_std()
        self.update_best()
        std_current = self.standardize(current)
        print('current', current)
        print('std', std_current)
        total_fitness = np.sum(std_current**2)

        return total_fitness, energy_fitness, dipole_fitness

    def energy_fitness(self, am1):
        hlt = self.reparm_data.high_level_outputs
        nsets = len(self.reparm_data.reparm_input.training_sets)
        ng = self.reparm_data.reparm_input.number_geometries
        sum_of_squares = 0
        for i in range(nsets):
            hlt_energy_differences = np.zeros((ng, ng))
            for j in range(ng):
                for k in range(ng):
                    hlt_energy_differences[j][k] = hlt[i*ng + j].ground_energy - hlt[i*ng + k].ground_energy

            am1_energy_differences = np.zeros((ng, ng))
            for j in range(ng):
                for k in range(ng):
                    am1_energy_differences[j][k] = am1[i*ng + j].ground_energy - am1[i*ng + k].ground_energy

            difference = am1_energy_differences - hlt_energy_differences
            sum_of_squares += np.sum(np.square(difference))

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
            self.reparm_data.best_fitness[0] = np.sum(std_best**2)
            # print("best is now", self.reparm_data.best_fitness)

    # All elements below original
    def aebo(self, elements):
        if self.reparm_data.original_fitness is None:
            return True
        if elements is None:
            return False
        for i, l in zip(elements, self.reparm_data.original_fitness[1:]):
            if i > l:
                return False
        return True


