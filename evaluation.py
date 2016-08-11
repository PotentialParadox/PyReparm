from reparm_data import ReparmData
import math
from random import random
from copy import deepcopy
from gaussian import run_gaussian


class Evaluator:
    def __init__(self, reparm_data = None, goal = None):
        self.reparm_data = ReparmData.reference(reparm_data)
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
        total_fitness = energy_fitness
        return total_fitness,

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
