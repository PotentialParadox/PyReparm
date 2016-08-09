import random

def mutateset(part, pert, chance):
    if not part.best:
        for i in range(0, len(part)):
            go = random.random()
            if go < chance:
                l = part[i]
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
