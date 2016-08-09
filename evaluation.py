from reparm_data import ReparmData
import math
from random import random
from copy import deepcopy
from parameter_group import ParameterGroup


class Evaluator:
    def __init__(self, reparm_data = None, goal = None):
        self.reparm_data = ReparmData.reference(reparm_data)
        self.goal = goal

    # Evaluates an individual
    def eval(self, part):
        r_value = random()
        if r_value < 0.1:
            return None
        sum = 0
        for i in range(0, len(part)):
            if part[i] > 0:
                sum += math.pow((part[i] - 6), 2)
            if part[i] < 0:
                sum += math.pow((part[i] + 6), 2)
        return sum,
