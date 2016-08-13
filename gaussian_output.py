import re
from coordinates import Coordinates
from parameters import Parameters


class GaussianOutput:
    def __init__(self, output_string=None):
        self.ground_energy = None
        self.dipole = None
        self.parameters = None
        self.opt_coords = None
        if output_string:
            self.ground_energy = find_ground_energy(output_string)
            self.dipole = find_dipole(output_string)
            self.parameters = find_parameters(output_string)
            self.opt_coords = find_opt_coordinates(output_string)


# find_ground_energy
#               takes a string of the gaussian output and returns a integer
#               of the ground energy
def find_ground_energy(file_string):
    p_float = re.compile('\-?\d+\.\d+,?')
    p_energy = re.compile('SCF Done.*')
    m = re.findall(p_energy, file_string)
    final_line = m[-1]
    m = re.search(p_float, final_line)
    return float(m.group(0))


# find_dipole
#               takes a string of the gaussian output and returns a list
#               of the dipole moment
def find_dipole(file_string):
    p_float = re.compile('\-?\d+\.\d+,?')
    p_dipole = re.compile('Dipole moment \(field-independent'
                          + ' basis, Debye\)\:\n.+')
    m = re.findall(p_dipole, file_string)
    dipole = []
    for i in m:
        n = re.findall(p_float, i)
        for j in n:
            dipole.append(float(j))
    dipole = dipole[-4:-1]
    return dipole


# find_parameters
#               finds the parameters printed out from AM1(input,print)
def find_parameters(file_string):
    p_parameters = re.compile("Method=(.|\n)*?(?=Standard basis)")
    m = re.search(p_parameters, file_string)
    if not m:
        return None
    return Parameters(from_parameter_string=m.group(0))


# find_opt_coordinates
#               finds the optimized coordinates of an gaussian output with opt
def find_opt_coordinates(file_string):
    # We need to build the coordinate object so charge and multiplicity are needed
    p_charge_mult = re.compile("Charge\s+=\s+(\d+)\s+M.+(\d+)")
    m = re.search(p_charge_mult, file_string)
    charge = m.group(1)
    multiplicity = m.group(2)

    # Getting the optimized coordinates is a little harder.
    # We split it up into two tasks

    # Find the standard orientation block
    p_stand_orient = re.compile("(Standard orientation(.|\n)*?(?=Rotat))")
    m = re.findall(p_stand_orient, file_string)
    last_occurrence = m[-1][0]

    # Now we extract the coordinates from this block
    p_coord = re.compile("\n\s+\d+\s+(\d+)\s+\d+\s+(-?\d+\.\d+)"
                         "\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)")
    m = re.findall(p_coord, last_occurrence)
    coordinates = []
    for i in m:
        coordinates.append([int(i[0]), float(i[1]), float(i[2]), float(i[3])])
    return Coordinates(charge=charge, multiplicity=multiplicity, coordinates=coordinates)


# find_normal_modes
#               parses a guassian output and returns the normal modes
def find_normal_modes(file_string):
    # We first extract the general frequency information into a
    # vector of up to three modes per element
    p_float = re.compile("-?\\d+\\.\\d+")
    p_freq_block = re.compile("(Frequencies(.|\n)*?(?=(Thermo|Frequ)))")
    matches = re.findall(p_freq_block, file_string)

    # From each of these elements, we extract the force constants
    p_frc_const = re.compile("Frc.*")
    force_constants = []
    for i in matches:
        m = re.search(p_frc_const, i[0])
        numbers = re.findall(p_float, m.group(0))
        for n in numbers:
            force_constants.append(float(n) * 100)

    # To get the normal modes, we recognize that the rows we want from the output
    # are the only ones that begin with an integer and end with a double
    p_atom = re.compile("(\n\\s+\\d+\\s+.*-?\\d+\\.\\d+)")
    atoms = re.findall(p_atom, matches[0][0])
    number_atoms = len(atoms)
    normals_of_atoms = [[] for _ in range(number_atoms)]
    for i in matches:
        atoms = re.findall(p_atom, i[0])
        for atom_number, values in enumerate(atoms):
            modes = re.findall(p_float, values)
            mode_values = []
            for i in modes:
                mode_values.append(float(i))
            normals_of_atoms[atom_number].extend(mode_values)

    # Right now we have two data object. The first one is a simple list
    # list of the force constants per frequency. The second is a list
    # of lists representing [atoms][normal values]. We now want to merge
    # the two such to get a list of of lists, in which the inner list is
    # is composed of force_constants, x_atom1, y_atom1, z_atom1, x_atom2.
    # and the outer represents each frequency.
    number_force_constants = len(force_constants)
    normal_mods = [[] for _ in range(number_force_constants)]
    for k, f_const in enumerate(force_constants):
        normal_mods[k].append(f_const)
    for i in range(number_atoms):
        x = []
        y = []
        z = []
        for j in range(len(normals_of_atoms[i])):
            if (j % 3) == 0:
                x.append(normals_of_atoms[i][j])
            if (j % 3) == 1:
                y.append(normals_of_atoms[i][j])
            if (j % 3) == 2:
                z.append(normals_of_atoms[i][j])
        for j in range(len(x)):
            normal_mods[j].extend([x[j], y[j], z[j]])
    return normal_mods
