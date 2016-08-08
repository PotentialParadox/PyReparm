import random

def mutateset(part, pert, chance):
    if not part.best:
        for i, l in enumerate(part):
            go = random.random()
            if go < chance:
                a = l - (l * pert)
                b = l + (l * pert)
                part[i] = random.uniform(a, b)
    else:
        for i, l in enumerate(part.best):
            go = random.random()
            if go < chance:
                a = l - (l * pert)
                b = l + (l * pert)
                part[i] = random.uniform(a, b)
