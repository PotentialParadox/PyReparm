from evaluation import Evaluator
from reparm_data import ReparmData
from genesis import Genesis
from diff_evo import differential_evolution
import numpy as np
from scipy.optimize import basinhopping
from copy import deepcopy
import time

'''
PyReparm is a program interfaces DEAP, scipy, scikit-learn, rdkit-kit,
other packages in an attempt to reparameterize AM1 parameters
for exicted state calculations.

!!! Input !!!
reparm.in is the primary input file
An example reparm.in can be found on the git repository.

!!! Saving and Loading data !!!
All pertinent information from the main reparm program,
including the coordinates, population parameters, fitness, etc,
are stored in a file called reparm.dat managed by reparm_data.py.

!!! Population Hierarchy !!!
__________________________________________________________________________________
                           parameter_group
                   inputs        ||                      outputs
header, coordinates, parameters  || energy, dipole, frequencies, intensities, etc..
------------------------------------------------------------------------------------
where a parameter_group is the group of structures that share the same set of AM1 parameters.
For comparability with python packages, and for storage, we save only the parameter group.
For all other sets, we only store the parameters in reparm_data.features, their corresponding
outputs in reparm_data.observations and their fitness in reparm_data.target

!!! Using sci-py !!!
The sci-py functions will require two primary arguments.
The list:
    Will usually be a list of parameters that produces the best possible fit.
    This will be from reparm_data.best_am1_individual.inputs[0].parameters[0].pfloats
    Now pfloats is a data structure that contains parameter_value, label_id,
    label_count, and line_number, so we only want to take every forth value.
Cost Function:
    This is the cost function which will end up becoming a very complicated
    behemoth so I made it a functor in evaluation.py, it'll need to save
    data, so call it with reparm_data

!!! SciKitLearn !!!
Use reparm_data.features, reparm_data.observations, and reparm_data.targets.

'''


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
        # Create coordinates
        Genesis(reparm_data=reparm_data)
        reparm_data.save()
else:
    Genesis(reparm_data=reparm_data)
    reparm_data.save()

# Number of Generation
NGEN = reparm_data.reparm_input.number_generations
# PopulationSize
PSIZE = reparm_data.reparm_input.population_size
# Crossover Probability
CXPB = reparm_data.reparm_input.crossover_probability

############################################
#        END USER INPUT
############################################

############################################
#        BEGIN SCI-PY
############################################

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
diff_init=None
if should_continue:
    diff_init="saved"
else:
    diff_init="latinhypercube"
bounds = []
bp = 10
for i in IL:
    value = 0, bp
    bounds.append(value)

time_start = time.time()
ret = differential_evolution(eval.eval, bounds=bounds, popsize=PSIZE, maxiter=NGEN, init=diff_init,
                             mutation=(0.3, 0.9), recombination=CXPB, disp=True, strategy='best2bin')
time_finish = time.time()
print("Finished DE in", time_finish - time_start, "seconds")
best = reparm_data.best_am1_individual
best.set_pfloats(ret.x)
open('ga_best.com', 'w').write(best.inputs[0].str())

# BasinHopping
# ret = basinhopping(eval.eval, IL, niter=200)
# best = reparm_data.best_am1_individual
# best.set_pfloats(ret.x)
# open('ga_best.com', 'w').write(best.inputs[0].str())

############################################
#        END SCI-PY
############################################
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
############################################
#        BEGIN SCIKIT-LEARN
############################################

############################################
#        END SCIKIT-LEARN
############################################

