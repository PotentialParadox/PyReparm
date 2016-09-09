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


class MyTakeStep(object):
    def __init__(self, pert=0.1, chance=0.1):
        self.pert = pert
        self.chance = chance

    def __call__(self, x):
        for i in range(len(x)):
            go = random.random()
            if go < self.chance:
                l = x[i]
                a = l - (l * self.pert)
                b = l + (l * self.pert)
                x[i] = random.uniform(a, b)
        return x

