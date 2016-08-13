from reparm_data import ReparmData
from gaussian_input import GaussianInput
from gaussian_output import GaussianOutput
import gaussian_output
from header import Header
from gaussian import gaussian_single, run_gaussian
from coordinates import Coordinates
from parameters import Parameters
from parameter_group import ParameterGroup
from copy import deepcopy
import numpy as np
import math
import random


class Genesis:
    def __init__(self, reparm_data):
        self.reparm_data = ReparmData.reference(reparm_data)
        self.opt_coords = None
        self.init_parameters = None
        self.normal_modes = None
        self.coordinates = []
        self.param_group = None
        self.read_user_input()
        print("Calculating HLT Opt")
        self.find_hlt_opt_normal()
        print("Finished HLT Opt")
        self.create_coordinates()
        self.create_initial_individual()
        print("Calculating HLT")
        self.create_HLT()
        print("Finished with HLT")

    def read_user_input(self):
        infile_name = self.reparm_data.reparm_input.file_name
        infile = open(infile_name).read()
        gin = GaussianInput(input_string=infile)
        self.opt_coords = gin.coordinates[0]
        # We'll try to get the parameters from the user,
        # If we can't we'll make our own
        self.init_parameters = gin.parameters[0]
        if not self.init_parameters:
            s_header = "#P AM1(Input,print)\n\nam1\n"
            header = Header(s_header)
            gin.header[0] = header
            gout = GaussianOutput(gaussian_single(gin.str()))
            self.init_parameters = gout.parameters

    def find_hlt_opt_normal(self):
        # We need to create a gaussian input file
        s_header1 = ("%chk=hlt\n#P " +
                     self.reparm_data.reparm_input.high_level_theory +
                     " opt\n\nhlt\n")
        header1 = Header(s_header1)
        gin1 = GaussianInput(header=header1, coordinates=self.opt_coords)

        # We're going to link it to a freq calculation
        gin2 = deepcopy(gin1)
        gin2.clear_coordinates()
        s_header2 = ("%chk=hlt\n#P " +
                     self.reparm_data.reparm_input.high_level_theory +
                     " freq geom=Checkpoint\n\nhlt\n")
        header2 = Header(s_header2)
        gin2.header[0] = header2
        gin1.link(gin2)
        fout = open("hlt_opt.com", 'w')
        fout.write(gin1.str())
        fout.close()

        # We run the job
        print("Running Job")
        gout = gaussian_single(gin1.str())
        fout = open("hlt_opt.log", 'w')
        fout.write(gout)
        fout.close()
        print("Finished Job")
        self.opt_coords = gaussian_output.find_opt_coordinates(gout)
        self.normal_modes = gaussian_output.find_normal_modes(gout)

    def create_coordinates(self):
        # Our goal is the make the average energy per atom equal
        # to 3/2 kb T. That means the total energy of the molecule
        # should be 3/2 kb T Na, where Na is the number of atoms
        number_atoms = int((len(self.normal_modes[0]) - 1) / 3)
        kb = 1.380648E-23
        T = self.reparm_data.reparm_input.temperature
        Et = 3.0 / 2.0 * kb * float(T) * float(number_atoms)

        # We'll need these in the next loop
        force_consts = np.zeros(len(self.normal_modes))
        for i, value in enumerate(self.normal_modes):
            force_consts[i] = value[0]

        # We now want to distribute this energy to each of the nodes
        number_modes = len(self.normal_modes)
        number_geometries = self.reparm_data.reparm_input.number_geometries
        self.coordinates.append(self.opt_coords)
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
            for i, mode in enumerate(self.normal_modes):
                for j, value in enumerate(mode):
                    normal_displacement[i, j - 1] = self.normal_modes[i][j]
            m_displacement = np.dot(m_max_displacements, normal_displacement)

            # Sum the rows for each column to an array representing the
            # displacement for each coordinate
            displacements = np.zeros(number_atoms * 3)
            for i in range(number_modes):
                for j in range(number_atoms * 3):
                    displacements[j] += m_displacement[i][j]

            m_coordinates = deepcopy(self.opt_coords.coordinates)
            for i, atom in enumerate(m_coordinates):
                for j in range(1, len(atom)):
                    index = int(3 * i + j - 1)
                    m_coordinates[i][j] += displacements[index]

            coordinates = Coordinates(charge=self.opt_coords.charge,
                                      multiplicity=self.opt_coords.multiplicity,
                                      coordinates=m_coordinates)
            self.coordinates.append(coordinates)

    def create_initial_individual(self):
        s_header1 = ("#P AM1(Input,Print) CIS(Singlets,NStates=" +
                     str(self.reparm_data.reparm_input.number_excited_states) +
                     ") pop(full)\n\nindividual\n")
        first_header = Header(from_header_string=s_header1)
        s_header2 = "#P AM1(Input,Print) freq\n\nAM1\n"
        second_header = Header(from_header_string=s_header2)
        inputs = []
        for i in self.coordinates:
            gin1 = GaussianInput(header=first_header,
                                 coordinates=i,
                                 parameters=self.init_parameters)
            gin2 = GaussianInput(header=second_header,
                                 coordinates=i,
                                 parameters=self.init_parameters)
            gin1.link(gin2)
            inputs.append(gin1)
        param_group = ParameterGroup(inputs=inputs)
        gouts = run_gaussian(parameter_group=param_group)
        param_group.outputs = gouts
        self.param_group = param_group
        fout = open("xyz_str.xyz", 'w')
        fout.write(self.param_group.xyz_str())
        fout.close()
        self.reparm_data.best_am1_individual = param_group

    def create_HLT(self):
        s_header1 = ("#P " +
                     str(self.reparm_data.reparm_input.high_level_theory) +
                     " CIS(Singlets,NStates=" +
                     str(self.reparm_data.reparm_input.number_excited_states) +
                     ") pop(full)\n\nhlt\n")
        s_header2 = ("#P " +
                     str(self.reparm_data.reparm_input.high_level_theory) +
                     " freq\n\nhlt\n")
        header1 = Header(from_header_string=s_header1)
        header2 = Header(from_header_string=s_header2)
        am1_inputs = self.param_group.inputs
        hlt_inputs = []
        for i in am1_inputs:
            hlt_input = GaussianInput(header=header1,
                                      coordinates=i.coordinates[0])
            hlt_freq = GaussianInput(header=header2,
                                     coordinates=i.coordinates[0])
            hlt_input.link(hlt_freq)
            hlt_inputs.append(hlt_input)
        hlt_group = ParameterGroup(inputs=hlt_inputs)
        np = self.reparm_data.reparm_input.number_processors
        self.reparm_data.high_level_outputs = run_gaussian(parameter_group=hlt_group, number_processors=np)
