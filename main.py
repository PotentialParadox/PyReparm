import random
from evaluation import Evaluator
from mutate import mutateset, MyTakeStep
from parameter_group import ParameterGroup
import gaussian_output
from gaussian_input import GaussianInput
from gaussian import gaussian_single
from header import Header
from reparm_data import ReparmData
from genesis import Genesis
import numpy as np
from scipy.optimize import basinhopping
from scipy.optimize import differential_evolution
from copy import deepcopy


def print_fun(x, f, accepted):
    print("at minimum %.4f accepted %d" % (f, int(accepted)))

#############################################
#         BEGIN USER INPUT
#############################################
fin = open("reparm.in", 'r')
file = fin.read()
reparm_data = ReparmData(file)
if reparm_data.reparm_input.should_continue:
    good_load = reparm_data.load()
    if not good_load:
        Genesis(reparm_data=reparm_data)
        reparm_data.save()
else:
    Genesis(reparm_data=reparm_data)
    reparm_data.save()
############################################
#        END USER INPUT
############################################

#############################################
#         BEGIN USER INPUT
#############################################
# Number of Generation
NGEN = reparm_data.reparm_input.number_generations
# PopulationSize
PSIZE = reparm_data.reparm_input.population_size
# Crossover Probability
CXPB = reparm_data.reparm_input.crossover_probability
# Mutation Probability
# How likely and individual will be mutated
MUTPB = reparm_data.reparm_input.mutation_probability
# Mutation Rate
# How likely a member of an individual will be mutated
MUTR = reparm_data.reparm_input.mutation_rate
# Crowding Factor
CWD = reparm_data.reparm_input.crowding_factor
# Mutation Perturbation
MUTPT = reparm_data.reparm_input.mutation_perturbation
# Initial Perturbation
IMUTPT = 0.05
# Initial List of parameters
IL = []
for i in range(0, len(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats), 4):
    IL.append(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats[i])

# The evaluator (fitness, cost) function
eval = Evaluator(reparm_data=reparm_data)
if reparm_data.original_fitness is None:
    eval.eval(IL)
print("Original Fitness:", reparm_data.original_fitness)

# Differential Evolution
bounds = []
bp = 1.05
for i in IL:
    value = i*(2-bp), i*bp
    bounds.append(value)
ret = differential_evolution(eval.eval, bounds=bounds, popsize=PSIZE, maxiter=NGEN,
                             mutation=(0.5, 1), recombination=CXPB, disp=True)
best = reparm_data.best_am1_individual
best.set_pfloats(ret.x)
open('ga_best.com', 'w').write(best.inputs[0].str())

# BasinHopping
# ret = basinhopping(eval.eval, IL, niter=2)

# def fitness(x):
#     sum = 0
#     for i in x:
#         sum += (5 - i)**2
#     return sum
#
# test = [(3, 5), (4, 9), (1, 6), (-65, 100)]
# ret = differential_evolution(fitness, bounds=test)
# print(ret.x)
