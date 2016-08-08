import random
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
CXPB = 0.5
# Mutation Probability
# How likely and individual will be mutated
MUTPB = reparm_data.reparm_input.mutation_probability
# Mutation Rate
# How likely a member of an individual will be mutated
MUTR = reparm_data.reparm_input.mutation_rate
# Mutation Perturbation
MUTPT = reparm_data.reparm_input.mutation_perturbation
# Initial Perturbation
IMUTPT = 0.05
# Initial List of parameters
IL = [200.45, 3.8, 6.89, 20, 43, 5]
# Goal List
goal = [6, 6, 6, 6, 6, 6, 6]
# The evaluator (fitness, cost) function
eval = Evaluator(goal=goal, reparm_data=reparm_data)

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
toolbox.register("mate", tools.cxTwoPoint)
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
    offspring = toolbox.select(pop, len(pop))
    offspring = list(map(toolbox.clone, offspring))
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CXPB:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values
    for mutant in offspring:
        if random.random() < MUTPB:
            toolbox.mutate(mutant)
            del mutant.fitness.values
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    pop[:] = offspring
# print(pop[1])
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

# fin = open("reparm.in", 'r')
# file = fin.read()
# reparm_data = ReparmData(file)
# reparm_data.load()
# Genesis(reparm_data)

# fin = open("test.com")
# file = fin.read()
# gin = GaussianInput(input_string=file)
# gin2 = GaussianInput(header=gin.header,
#                      coordinates=gin.coordinates,
#                      parameters=gin.parameters)
# inputs = [gin, gin2]
# paramgroup = ParameterGroup(inputs=inputs)
# print(paramgroup.inputs[0].str())
# paramgroup.set_pfloats(gin.parameters[0].p_floats)
# print(paramgroup.inputs[0].str())
