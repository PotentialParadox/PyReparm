from coordinates import Coordinates
import re


class ZMatrix(Coordinates):
    def __init__(self, from_coordinate_string=None, charge=None, multiplicity=None, coordinates=None):
        Coordinates.__init__(self, from_coordinate_string, charge, multiplicity, coordinates)

    def find_coordinates(self, coordinate_string):
        # Get coordinate block
        p_block = re.compile("((\n|.)*?)(?=\n\n)\n((\n|.)*)\n$")
        p = re.search(p_block, coordinate_string)
        p_atom = re.compile("(\n\s*\w{1,2}\s*(?=\n)|\n\s*\w{1,2}(\s+\d\s+-?\d+\.\d+)*[\t ]*0*[\t ]*(?=\n|$))")
        # print(p.group(3))
        m = re.findall(p_atom, p.group(1))
        self.coordinates = []
        p_atom_type = re.compile("^\s*\w+")
        p_coord = re.compile("((\d+)\s+(-?\d+\.\d+)\s*)")
        for i, atom in enumerate(m):
            # print(atom)
            atom_t = re.search(p_atom_type, atom[0]).group(0)
            self.coordinates.append(atom_t)
            values = re.findall(p_coord, atom[0])
            for v in values:
                self.coordinates.extend([int(v[1]), float(v[2])])
        if p.group(3):
            self.coordinates.append(p.group(3))

    def str(self):
        coord_str = str(self.charge) + " " + str(self.multiplicity)
        coords = self.coordinates
        # print(coords)
        if re.search("\d+\.\d+", str(coords[0])):
            raise AttributeError
        for i, value in enumerate(coords):
            try:
                if i == 0:
                    coord_str += str(value)
                if i == 1:
                    coord_str += str(coords[i]) + 18*" " + str(coords[i+1]) + 4*" " + "{0:.8f}".format(coords[i+2])
                if i == 4:
                    coord_str += str(coords[i]) + 18*" " + str(coords[i+1]) + 4*" " + "{0:.8f}".format(coords[i+2])
                    coord_str += 4*" " + str(coords[i+3]) + 2*" " + "{0:.8f}".format(coords[i+4])
                if i >= 9 and ((i-9) % 7) == 0:
                    coord_str += str(coords[i]) + 18*" " + str(coords[i+1]) + 4*" " + "{0:.8f}".format(coords[i+2])
                    coord_str += 4*" " + str(coords[i+3]) + 2*" " + "{0:.8f}".format(coords[i+4])
                    coord_str += 4*" " + str(coords[i+5]) + 2*" " + "{0:.8f}".format(coords[i+6])
                    coord_str += str(2*"\t" + str(0))
            except IndexError:
                coord_str += "\n" + coords[-1]
        return coord_str

    def xyz_string(self):
        return None