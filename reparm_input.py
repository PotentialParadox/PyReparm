import re


class ReparmInput:
    def __init__(self, input_string):
        self.file_name = find_file_name(input_string)
        self.high_level_theory = find_hlt(input_string)
        self.number_excited_states = find_number_es(input_string)
        self.number_generations = find_number_generations(input_string)
        self.number_processors = find_number_processors(input_string)
        self.number_geometries = find_number_geometries(input_string)
        self.number_elites = find_number_elites(input_string)
        self.training_sets = find_training_sets(input_string)
        self.population_size = find_population_size(input_string)
        self.temperature = find_temperature(input_string)
        self.mutation_probability = find_mutation_probability(input_string)
        self.mutation_rate = find_mutation_rate(input_string)
        self.mutation_perturbation = find_mutation_perturbation(input_string)
        self.crossover_probability = find_crossover_probability(input_string)
        self.crowding_factor = find_crowding_factor(input_string)
        self.survival_chance = find_survival_chance(input_string)
        self.should_continue = find_should_continue(input_string)


def find_file_name(input_string):
    p_search = re.compile("Input File:\s+(.+.com)")
    m = re.search(p_search, input_string)
    if m:
        return m.group(1)
    else:
        return None


def find_hlt(input_string):
    p_search = re.compile("High Level Theory:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return m.group(1)
    else:
        return None


def find_number_es(input_string):
    p_search = re.compile("Number of Excited States:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return int(m.group(1))
    else:
        return None


def find_number_generations(input_string):
    p_search = re.compile("Number of Generations:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return int(m.group(1))
    else:
        return None


def find_number_processors(input_string):
    p_search = re.compile("Number of Processors:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return int(m.group(1))
    else:
        return None


def find_number_geometries(input_string):
    p_search = re.compile("Number of Geometries:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return int(m.group(1))
    else:
        return None

def find_number_elites(input_string):
    p_search = re.compile("Number of Elites:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return int(m.group(1))
    else:
        return None

def find_training_sets(input_string):
    p_search = re.compile("Training Sets:\s+(.+)")
    training_string = re.search(p_search, input_string).group(0)
    p_digit = re.compile("\d")
    m = re.findall(p_digit, training_string)
    if m:
        ret_list = []
        for i in m:
            ret_list.append(int(i))
        return ret_list
    else:
        return None

def find_population_size(input_string):
    p_search = re.compile("Population Size:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return int(m.group(1))
    else:
        return None


def find_temperature(input_string):
    p_search = re.compile("Temperature:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return float(m.group(1))
    else:
        return 300


def find_mutation_probability(input_string):
    p_search = re.compile("Mutation Probability:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return float(m.group(1))
    else:
        return None


def find_mutation_rate(input_string):
    p_search = re.compile("Mutation Rate:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return float(m.group(1))
    else:
        return None


def find_mutation_perturbation(input_string):
    p_search = re.compile("Mutation Perturbation:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return float(m.group(1))
    else:
        return None


def find_crossover_probability(input_string):
    p_search = re.compile("Crossover Probability:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return float(m.group(1))
    else:
        return None


def find_crowding_factor(input_string):
    p_search = re.compile("Crowding Factor:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return float(m.group(1))
    else:
        return None


def find_survival_chance(input_string):
    p_search = re.compile("Survival Chance:\s+(.+)")
    m = re.search(p_search, input_string)
    if m:
        return float(m.group(1))
    else:
        return None


def find_should_continue(input_string):
    p_search = re.compile("Continue From Last Run:\s+(.+)")
    m = re.search(p_search, input_string)
    if m.group(1) == "True":
        return True
    return False
