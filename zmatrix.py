from coordinates import Coordinates
import re


class ZMatrix(Coordinates):
    def __init__(self, from_coordinate_string=None, charge=None, multiplicity=None, coordinates=None):
        Coordinates.__init__(self, from_coordinate_string, charge, multiplicity, coordinates)

    def find_coordinates(self, coordinate_string):
        p_atom = re.compile("(\s+\w{1,2}\s+(\d+\s+-?\d+\.\d+\s*)*)[\t ]*0*[\t ]*\n")
        m = re.findall(p_atom, coordinate_string)
        self.coordinates = []
        p_atom_type = re.compile("^\s*\w+")
        p_coord = re.compile("\d+\s+-?\d+\.\d+\s*")
        for i, atom in enumerate(m):
            atom_t = re.search(p_atom_type, atom[0]).group(0)
            values = re.findall(p_coord, atom[0])



    def str(self):
        coord_str = str(self.charge) + " " + str(self.multiplicity) + "\n"
        for i, value in enumerate(self.coordinates):
            coord_str += str(value)
        return coord_str
