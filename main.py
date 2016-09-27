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
from diff_evo import differential_evolution
import numpy as np
from scipy.optimize import basinhopping
from scipy.optimize import fmin
from copy import deepcopy
import time


def print_fun(x, f, accepted):
    print("at minimum %.4f accepted %d" % (f, int(accepted)))

#############################################
#         BEGIN USER INPUT
#############################################
fin = open("reparm.in", 'r')
file = fin.read()
reparm_data = ReparmData(file)
should_continue = False
if reparm_data.reparm_input.should_continue:
    good_load = reparm_data.load()
    should_continue = True
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

# Uncomment to test parameters that are modified
# gin = GaussianInput(open('test.com', 'r').read())
# gin = GaussianInput(gin.str(), fetch_all=True)
# for i in range(len(reparm_data.best_am1_individual.inputs)):
    # reparm_data.best_am1_individual.inputs[i] = gin


# Initial List of parameters
IL = []
for i in range(0, len(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats), 4):
    IL.append(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats[i])


# Uncomment to test parameters that are modified
# for i in range(len(IL)):
    # IL[i] = 5
# gin.parameters[0].set_floats(IL)
# print(gin.str())


# The evaluator (fitness, cost) function
eval = Evaluator(reparm_data=reparm_data)
if reparm_data.original_fitness is None:
    eval.eval(IL)
print("Original Fitness:", reparm_data.original_fitness)

# Differential Evolution
diff_init=None
if should_continue:
    diff_init="saved"
else:
    diff_init="latinhypercube"
bounds = []
bp = 0.5
for i in IL:
    value = i*(1+bp), i*(1-bp)
    bounds.append(value)

time_start = time.time()
ret = differential_evolution(eval.eval, bounds=bounds, popsize=PSIZE, maxiter=NGEN, init=diff_init,
                             mutation=(0.3, 0.9), recombination=CXPB, disp=True, strategy='best2bin')
time_finish = time.time()
print("Finished DE in", time_finish - time_start, "seconds")
best = reparm_data.best_am1_individual
best.set_pfloats(ret.x)
reparm_data.save()
open('ga_best.com', 'w').write(best.inputs[0].str())

# BasinHopping
# ret = basinhopping(eval.eval, IL, niter=200)
# best.set_pfloats(ret.x)
# reparm_data.save()
# open('ga_best.com', 'w').write(best.inputs[0].str())

# Nelder-Mead
# We need to activate all the parameters
best = reparm_data.best_am1_individual
# Initial List of parameters
for i in range(len(best.inputs)):
    best.inputs[i] = GaussianInput(best.inputs[i].str(), fetch_all=True)
IL = []
for i in range(0, len(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats), 4):
    IL.append(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats[i])
time_start = time.time()
ret=fmin(eval.eval, IL, maxiter=NGEN)
time_finish = time.time()
print("Finished NM in", time_finish - time_start, "seconds")
best = reparm_data.best_am1_individual
best.set_pfloats(ret.x)
reparm_data.save()
open('ga_best.com', 'w').write(best.inputs[0].str())

