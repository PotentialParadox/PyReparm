import numpy as np
from coordinates import Coordinates
import random
from gaussian_input import GaussianInput
from copy import deepcopy


def temperature_perturbation(reparm_data, opt_coords, normal_modes):
    # Our goal is the make the average energy per atom equal
    # to 3/2 kb T. That means the total energy of the molecule
    # should be 3/2 kb T Na, where Na is the number of atoms
    number_atoms = int((len(normal_modes[0]) - 1) / 3)
    kb = 1.380648E-23
    T = reparm_data.reparm_input.temperature
    Et = 3.0 / 2.0 * kb * float(T) * float(number_atoms)

    # We'll need these in the next loop
    force_consts = np.zeros(len(normal_modes))
    for i, value in enumerate(normal_modes):
        force_consts[i] = value[0]

    # We now want to distribute this energy to each of the nodes
    number_modes = len(normal_modes)
    number_geometries = reparm_data.reparm_input.number_geometries
    coordinates_a = [opt_coords]
    for geom in range(1, number_geometries):
        # We need to perturb our total energy by a normally
        # distributed value
        variance = 2.0 / (3.0 * number_atoms) * Et
        Et_modified = random.gauss(Et, variance)
        r_values = np.random.rand(number_modes)
        normalizer = sum(r_values)
        r_values = r_values / normalizer
        energy_per_mode = r_values * Et_modified

        # Given the energy and force constants, we can find
        # the max displacement using hooks law, E = 1/2 kx^2
        max_displacements = 2 * energy_per_mode / force_consts
        max_displacements = np.sqrt(max_displacements) * 1E10

        # Modes can go in either direction, so we need to
        # randomly assign a negative value to some of them
        r_direction = np.random.rand(number_modes)
        for r, rand in enumerate(r_direction):
            if rand < 0.5:
                max_displacements[r] = -max_displacements[r]

        # A diagonal matrix will be more useful
        m_max_displacements = np.zeros(shape=[number_modes, number_modes])
        for i, displacement in enumerate(max_displacements):
            m_max_displacements[i][i] = displacement

        # We now get the coordinate displacement for each of the normal
        # modes. To do this we create a matrix of normalized coordinate modes
        # where the rows represent each mode and the columns represent the
        # coordinates
        normal_displacement = np.zeros(shape=[number_modes, number_atoms * 3])
        for i, mode in enumerate(normal_modes):
            for j, value in enumerate(mode):
                normal_displacement[i, j - 1] = normal_modes[i][j]
        m_displacement = np.dot(m_max_displacements, normal_displacement)

        # Sum the rows for each column to an array representing the
        # displacement for each coordinate
        displacements = np.zeros(number_atoms * 3)
        for i in range(number_modes):
            for j in range(number_atoms * 3):
                displacements[j] += m_displacement[i][j]

        m_coordinates = deepcopy(opt_coords.coordinates)
        for i, atom in enumerate(m_coordinates):
            for j in range(1, len(atom)):
                index = int(3 * i + j - 1)
                m_coordinates[i][j] += displacements[index]

        coordinates = Coordinates(charge=opt_coords.charge,
                                  multiplicity=opt_coords.multiplicity,
                                  coordinates=m_coordinates)
        coordinates_a.append(coordinates)
        return coordinates_a


def face_to_face(reparm_data):
    fin = open("ftfthiophene.com", 'r')
    file = fin.read()
    gin = GaussianInput(input_string=file)
    coordinates = []
    ng = reparm_data.reparm_input.number_geometries
    coord = deepcopy(gin.coordinates[0])
    for _ in range(ng):
        coords = coord.coordinates
        for atom in coords[9:18]:
            atom[3] += 1/ng
        cl = deepcopy(coord)
        coordinates.append(cl)
    return coordinates


def dihedral(reparm_data):
    gin = GaussianInput(open("dithiophene.com", 'r').read())
    coordinates = []
    ng = reparm_data.reparm_input.number_geometries
    coord = deepcopy(gin.coordinates[0])
    for _ in range(ng):
        coords = coord.coordinates
        coords[29] = 500
        cc = deepcopy(coord)
        coordinates.append(cc)
    return coordinates
