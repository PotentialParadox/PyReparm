from copy import deepcopy
import random
from deap import base
from deap import creator
from deap import tools

def generator(original_list, perturbation):
    param_set = deepcopy(original_list)
    for i in range(0, len(param_set)):
        random_max = original_list[i] + original_list[i] * perturbation
        random_min = original_list[i] - original_list[i] * perturbation
        param_set[i] = random.uniform(random_min, random_max)
    return creator.ParamSet(param_set)
