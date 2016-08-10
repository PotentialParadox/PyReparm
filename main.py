import random
import bitstring
import math
from evaluation import Evaluator
from generator import generator
from mutate import mutateset
from deap import base
from deap import creator
from deap import tools
from parameter_group import ParameterGroup
import numpy as np
import gaussian_output
from gaussian_input import GaussianInput
from gaussian import gaussian_single
from reparm_input import ReparmInput
from reparm_data import ReparmData
from genesis import Genesis


#############################################
#         BEGIN USER INPUT
#############################################
fin = open("reparm.in", 'r')
file = fin.read()
reparm_data = ReparmData(file)
if reparm_data.reparm_input.should_continue:
    reparm_data.load()
else:
    Genesis(reparm_data=reparm_data)
    reparm_data.save()

#############################################
#         END USER INPUT
#############################################


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
original_fitness = eval.eval(IL)
print("original_fitness", original_fitness)

#############################################
#         END USER INPUT
#############################################

#############################################
#         BEGIN DEAP SETUP
#############################################

creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("ParamSet", list, fitness=creator.FitnessMax, best=None)

toolbox = base.Toolbox()
toolbox.register("individual", generator, IL, IMUTPT)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxSimulatedBinary)
toolbox.register("mutate", mutateset, pert=MUTPT, chance=MUTR)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", eval.eval)

pop = toolbox.population(n=PSIZE)

best = None

#############################################
#         END DEAP SETUP
#############################################

#############################################
#         BEGIN GENETIC ALGORITHM
#############################################
for g in range(NGEN):
    print("Starting gen:", g)
    offspring = toolbox.select(pop, len(pop))
    offspring = list(map(toolbox.clone, offspring))
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CXPB:
            toolbox.mate(child1, child2, CWD)
            del child1.fitness.values
            del child2.fitness.values
    for mutant in offspring:
        if random.random() < MUTPB:
            toolbox.mutate(mutant)
            del mutant.fitness.values
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = []
    for i in invalid_ind:
        try:
            fitness = toolbox.evaluate(i)
            fitnesses.append(fitness)
        except TypeError:
            fitnesses.append(None)
    for ind, fit in zip(invalid_ind, fitnesses):
        if fit:
            ind.fitness.values = fit
            if not best or fit < best.fitness.values:
                best = ind
                reparm_data.best_am1_individual.set_pfloats(best)
                reparm_data.save()
                print("NewBest Found:", fit)
    pop[:] = offspring
#############################################
#         End Genetic Algorithm
#############################################

#############################################
#         Begin Particle Simulation
#############################################
# for g in range(NGEN):
#     for part in pop:
#         part.fitness.values = toolbox.evaluate(part)
#         if not part.best or part.best.fitness < part.fitness:
#             part.best = creator.ParamSet(part)
#             part.best.fitness.values = part.fitness.values
#         if not best or best.fitness < part.fitness:
#             best = creator.ParamSet(part)
#             best.fitness.values = part.fitness.values
#     for part in pop:
#         toolbox.mutate(part)
#     print(best, "with fitness", best.fitness)
#############################################
#         End Particle Simulation
#############################################

#############################################
#         Begin Print Out
#############################################
gin_best = reparm_data.best_am1_individual.inputs[0]
fout = open("reparm_best.com", 'w')
fout.write(gin_best.str())

#############################################
#         End Print Out
#############################################
