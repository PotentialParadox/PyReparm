import random
from evaluation import Evaluator
from generator import generator
from mutate import mutateset
from parameter_group import ParameterGroup
import gaussian_output
from analysis import Analysis
from gaussian_input import GaussianInput
from gaussian import gaussian_single
from header import Header
from reparm_data import ReparmData
from genesis import Genesis
import numpy as np
from scipy.optimize import basinhopping
from scipy.optimize import differential_evolution
from copy import deepcopy

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
nIL = np.array(IL)
l_nIL = nIL / 2
u_nIL = nIL * 2

# The evaluator (fitness, cost) function
eval = Evaluator(reparm_data=reparm_data)
eval.eval(IL)

ret = basinhopping(eval.eval, IL)

