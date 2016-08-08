from reparm_data import ReparmData
from copy import deepcopy
from parameter_group import ParameterGroup


class Evaluator:
    def __init__(self, reparm_data = None, goal = None):
        self.reparm_data = ReparmData.reference(reparm_data)
        self.goal = goal

    # Evaluates an individual
    def eval(self, part):
        individual = deepcopy(self.reparm_data.best_am1_individual)
        print(individual.inputs[0].parameters[0].p_floats)
        print(part)
        answer = 0
        for i, s in enumerate(part):
            answer += pow(s - self.goal[i], 2)
        return answer,
