import random
from evaluation import Evaluator
from mutate import mutateset, MyTakeStep
from evaluation import Evaluator
from generator import generator
from deap import base
from deap import creator
from deap import tools
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
# Survival Rate
SR = reparm_data.reparm_input.survival_chance
# Number Survivals
NSURV = int(PSIZE * SR)
# Number Elites
NELITES = reparm_data.reparm_input.number_excited_states
# Number of normal members
NNORMALS = PSIZE - NELITES
# Initial Perturbation
IMUTPT = 0.05

# Uncomment to test parameters that are modified
# gin = GaussianInput(open('test.com', 'r').read())
# gin = GaussianInput(gin.str(), fetch_all=True)
# for i in range(len(reparm_data.best_am1_individual.inputs)):
    # reparm_data.best_am1_individual.inputs[i] = gin

# Uncomment to test parameters that are modified
# for i in range(len(IL)):
    # IL[i] = 5
# gin.parameters[0].set_floats(IL)
# print(gin.str())



#############################################
#         END USER INPUT
#############################################

evaluator = Evaluator(reparm_data=reparm_data)

# Initial List of parameters
IL = []
for i in range(0, len(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats), 4):
    IL.append(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats[i])

# The evaluator (fitness, cost) function
if reparm_data.original_fitness is None:
    eval.eval(IL)
print("Original Fitness:", reparm_data.original_fitness)

#############################################
#         BEGIN GA
#############################################

# def testval(x):
    # nx = np.array(x)
    # ny = np.array([1,2,3,4,5,6,7,8])
    # return float(np.sum(np.square(nx-ny))),
# PSIZE = 8
# NELITES = 2
# NNOMALS = PSIZE - NELITES
# NSURV = 6
# CWD = 2
# IL = [8,7,6,5,4,3,2,1]

creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("ParamSet", list, fitness=creator.FitnessMax, best=None)
toolbox = base.Toolbox()
toolbox.register("individual", generator, IL, 0.01)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxSimulatedBinary, eta=CWD)
toolbox.register("mutate", mutateset, pert=0.5, chance=0.1)
toolbox.register("select", tools.selBest, k=NSURV)
toolbox.register("evaluate", evaluator.eval)

pop = toolbox.population(n=PSIZE)
for i in pop: i.fitness.values = toolbox.evaluate(i)

for n in range(NGEN):
    print('Begining Step', n)
    # Do aristocratic cloning
    pop = sorted(pop, key=lambda individual: individual.fitness.values[0])
    for i, father in enumerate(pop[0:NELITES]):
        clone = toolbox.clone(father)
        toolbox.mutate(clone, pert=0.1, chance=1)
        clone.fitness.values = toolbox.evaluate(clone)
        if clone.fitness.values[0] < father.fitness.values[0]:
            pop[i] = clone

    # Select the Parents
    selected = toolbox.select(pop)
    parents = [toolbox.clone(ind) for ind in selected]

    # Apply Crossover
    for i in range(NELITES,PSIZE):
        selected = tools.selRoulette(parents, k=2)
        child1, child2 = [toolbox.clone(ind) for ind in (selected[0], selected[1])]
        toolbox.mate(child1, child2)
        toolbox.mutate(child1)
        toolbox.mutate(child2)
        child1.fitness.values = toolbox.evaluate(child1)
        child2.fitness.values = toolbox.evaluate(child2)
        if child1.fitness.values[0] < child2.fitness.values[0]:
            pop[i] = child1
        else:
            pop[i] = child2
for i in pop: print(i)

#############################################
#         END GA
#############################################


# Differential Evolution
# diff_init=None
# if should_continue:
    # diff_init="saved"
# else:
    # diff_init="latinhypercube"
# bounds = []
# bp = 1.5
# for i in IL:
    # lowbound = 0
    # if i*(1-bp) > 0:
        # lowbound = i*(1-bp)
    # highbound = i*(1+bp)
    # value = lowbound, highbound
    # bounds.append(value)

# time_start = time.time()
# ret = differential_evolution(eval.eval, bounds=bounds, popsize=PSIZE, maxiter=NGEN, init=diff_init,
                             # mutation=(0.3, 0.9), recombination=CXPB, disp=True, strategy='best2bin')
# time_finish = time.time()
# print("Finished DE in", time_finish - time_start, "seconds")
# best = reparm_data.best_am1_individual
# best.set_pfloats(ret.x)
# reparm_data.save()
# open('ga_best.com', 'w').write(best.inputs[0].str())

# BasinHopping
# ret = basinhopping(eval.eval, IL, niter=200)
# best.set_pfloats(ret.x)
# reparm_data.save()
# open('ga_best.com', 'w').write(best.inputs[0].str())

# Nelder-Mead
# We need to activate all the parameters
# best = reparm_data.best_am1_individual
# # Initial List of parameters
# for i in range(len(best.inputs)):
    # best.inputs[i] = GaussianInput(best.inputs[i].str(), fetch_all=True)
# IL = []
# for i in range(0, len(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats), 4):
    # IL.append(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats[i])
# time_start = time.time()
# ret=fmin(eval.eval, IL, maxiter=NGEN)
# time_finish = time.time()
# print("Finished NM in", time_finish - time_start, "seconds")
# best = reparm_data.best_am1_individual
# best.set_pfloats(ret.x)
# reparm_data.save()
# open('ga_best.com', 'w').write(best.inputs[0].str())

