import random
from evaluation import Evaluator
from generator import generator
from mutate import mutateset
from deap import base
from deap import creator
from deap import tools
from parameter_group import ParameterGroup
import gaussian_output
from analysis import Analysis
from gaussian_input import GaussianInput
from gaussian import gaussian_single
from header import Header
from reparm_data import ReparmData
from genesis import Genesis
import numpy as np
from scipy.optimize import minimize
from copy import deepcopy
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.linear_model import RidgeCV
from sklearn.ensemble import RandomForestRegressor

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

# The evaluator (fitness, cost) function
eval = Evaluator(reparm_data=reparm_data)
if reparm_data.best_fitness is None:
    reparm_data.best_fitness = list(eval.eval(IL))
    reparm_data.original_fitness = deepcopy(reparm_data.best_fitness)
else:
    reparm_data.best_fitness = list(eval.eval(IL))

print("original_fitness", reparm_data.original_fitness)
print("starting at", reparm_data.best_fitness)


#############################################
#         END USER INPUT
#############################################

#############################################
#         BEGIN DEAP SETUP
#############################################

creator.create("FitnessMax", base.Fitness, weights=(-1.0, 0, 0))
creator.create("ParamSet", list, fitness=creator.FitnessMax, best=None)

toolbox = base.Toolbox()
toolbox.register("individual", generator, IL, IMUTPT)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxSimulatedBinary)
toolbox.register("mutate", mutateset, pert=MUTPT, chance=MUTR)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", eval.eval)

pop = toolbox.population(n=PSIZE)

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
            reparm_data.observations.append(list(i))
            i.fitness.values = fitness
            if not reparm_data.best_fitness or fitness[0] < reparm_data.best_fitness[0]:
                print("Previous Best", reparm_data.best_fitness)
                reparm_data.best_fitness = list(fitness)
                reparm_data.best_am1_individual.set_pfloats(i)
                print("NewBest Found:", reparm_data.best_fitness)
        except TypeError:
            fitnesses.append(None)
    reparm_data.save()
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
s_opt_header = "#P AM1(Input,Print) opt\n\nAM1\n"
opt_header = Header(s_opt_header)
gin_opt = GaussianInput(header=opt_header,
                        coordinates=gin_best.coordinates[0],
                        parameters=gin_best.parameters[0])
fout = open("reparm_best_opt.com", 'w')
fout.write(gin_opt.str())
fout.close()

try:
    gout = gaussian_single(gin_opt.str())
    fout = open("reparm_best_opt.log", 'w')
    fout.write(gout)
    fout.close()
except TypeError:
    print("Could not get output file from input,"
          "most likely, optimization failed to converge")

#############################################
#         End Print Out
#############################################
#############################################
#         Begin ScikitLearn
#############################################
# # Preprocessor
# targets = np.array(reparm_data.targets)
# X = np.array(reparm_data.observations)
# y = targets[:, 0]  # 0, 1, 2 for total, energy, and dipole
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)
# stdsc = StandardScaler()
# X_train_std = stdsc.fit_transform(X_train)
# X_test_std = stdsc.transform(X_test)
#
# # Training
# clf = svm.SVR(C=1.3, kernel='rbf')
# # clf = RandomForestRegressor(n_estimators=20)
# clf.fit(X_train, y_train)
# print("Using {} samples with fitness score {}".format(len(y), clf.score(X_test, y_test)))
#
# initial_guess = np.array(IL)
# fun = lambda x: clf.predict(stdsc.transform(x.reshape(1, -1)))
# print("Predicting best parameters")
# min_params = (minimize(fun, initial_guess)).x
# stdsc.inverse_transform(min_params)
# params = min_params.tolist()
# skl_best = deepcopy(reparm_data.best_am1_individual)
# skl_best.set_pfloats(params)
# open("skl_best.com", 'w').write(skl_best.inputs[0].str())
# skl_fitness = eval.eval(params)
# if skl_fitness:
#     print("skl_fitness:", skl_fitness)

#############################################
#         End ScikitLearn
#############################################

#############################################
#         Begin Analysis
#############################################
anal = Analysis(reparm_data)
anal.trithiophene()
#############################################
#         End Analysis
#############################################
