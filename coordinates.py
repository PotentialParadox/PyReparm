import re


class Coordinates:
    def __init__(self, from_coordinate_string=None, charge=None, multiplicity=None, coordinates=None):
        self.charge = charge
        self.multiplicity = multiplicity
        self.coordinates = coordinates
        if from_coordinate_string:
            self.find_spins(from_coordinate_string)
            self.find_coordinates(from_coordinate_string)

    def find_spins(self, coordinate_string):
        p_spins = re.compile("(\\d+)\\s+(\\d+)\\s*\n")
        m = re.search(p_spins, coordinate_string)
        self.charge = int(m.group(1))
        self.multiplicity = int(m.group(2))

    def find_coordinates(self, coordinate_string):
        p_coord = re.compile("(\\S+)\\s+(-?\\d+\\.\\d+\\s+)(-?\\d+\\.\\d+\\s+)(-?\\d+\\.\\d+\\s*)")
        m = re.findall(p_coord, coordinate_string)
        coords = []
        for line in m:
            atom_type = ''
            try:
                atom_type = periodic_table(line[0])
            except KeyError:
                atom_type = line[0]
            n = [
                    str(atom_type),
                    float(line[1]),
                    float(line[2]),
                    float(line[3])
                ]
            coords.append(n)
        self.coordinates = coords

    def str(self):
        coord_str = str(self.charge) + " " + str(self.multiplicity) + "\n"
        if self.coordinates:
            for i in self.coordinates:
                coord_str += "{:>2}".format(i[0])
                for j in range(1, 4):
                        coord_str += "{: 19.6f}".format(i[j])
                coord_str += "\n"
            coord_str += "\n"
        return coord_str

    def xyz_string(self):
        ss = str(len(self.coordinates)) + "\nXYZ\n"
        for i in self.coordinates:
            ss += "{:>2}{: 19.6f}{: 19.6f}{: 19.6f}\n".format(i[0], i[1], i[2], i[3])
        return ss


def periodic_table(atomic_number):
    p_table = ({'1': 'H', '2': 'He', '3': 'Li', '4': 'Be', '5': 'B',
                '6': 'C', '16': 'S'})
    return p_table[atomic_number]

