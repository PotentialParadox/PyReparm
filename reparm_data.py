import re
import copy
from reparm_input import ReparmInput
from parameters import Parameters
from coordinates import Coordinates
from gaussian_input import GaussianInput
from gaussian_output import GaussianOutput
from parameter_group import ParameterGroup
from header import Header


class ReparmData():
    def __init__(self, file_name):
        self.reparm_input = ReparmInput(file_name)
        self.original_fitness = None
        # This is a list of gaussian outputs
        self.high_level_outputs = None
        # This is of type param_group
        self.best_am1_individual = None

    def copy(self):
        return copy.deepcopy(self)

    def reference(self):
        return self

    def save(self):
        number_geometries = self.reparm_input.number_geometries
        number_atoms = len(self.best_am1_individual.inputs[0].coordinates[0].coordinates)
        charge = self.best_am1_individual.inputs[0].coordinates[0].charge
        multiplicity = self.best_am1_individual.inputs[0].coordinates[0].multiplicity
        inputs = self.best_am1_individual.inputs
        parameter_floats = self.best_am1_individual.inputs[0].parameters[0].p_floats
        parameter_labels = self.best_am1_individual.inputs[0].parameters[0].labels

        coordinates = []
        for i in inputs:
            for j in i.coordinates[0].coordinates:
                for k in j:
                    coordinates.append(k)

        energies = []
        for i in self.high_level_outputs:
            energies.append(i.ground_energy)

        dipoles = []
        for i in self.high_level_outputs:
            for j in i.dipole:
                dipoles.append(j)

        fout = open("reparm.dat", 'w')
        fout.write(str(self.original_fitness) + "\n")
        fout.write(str(number_geometries) +"\n")
        fout.write(str(number_atoms) +"\n")
        fout.write(str(charge) +"\n")
        fout.write(str(multiplicity) +"\n")
        fout.write(str(len(parameter_floats)) +"\n")
        for i in parameter_floats:
            fout.write(str(i) +"\n")
        fout.write(str(len(parameter_labels)) +"\n")
        for i in parameter_labels:
            if i != "\n":
                fout.write(i + "\n")
            else:
                fout.writable("\\n\n")
        fout.write(str(len(coordinates)) +"\n")
        for i in coordinates:
            fout.write(str(i) +"\n")
        fout.write(str(len(energies)) +"\n")
        for i in energies:
            fout.write(str(i) +"\n")
        fout.write(str(len(dipoles)) +"\n")
        for i in dipoles:
            fout.write(str(i) +"\n")

    def load(self):
        fin = open("reparm.dat", 'r')
        of = fin.readline()
        if of != "None\n":
            self.original_fitness = float(of)
        number_geometries = int(fin.readline())
        number_atoms = int(fin.readline())
        charge = int(fin.readline())
        multiplicity = int(fin.readline())
        vector_size = int(fin.readline())
        best_pfloats = []
        for _ in range(vector_size):
            best_pfloats.append(float(fin.readline()))

        # Read the parameters
        vector_size = int(fin.readline())
        param_labels = []
        i = 0
        while i < vector_size:
            val = str(fin.readline())
            if val != '\n':
                val = val.rstrip('\n')
                param_labels.append(val)
                i += 1
            else:
                param_labels[-1] += val
        param_labels[-1] += "\n"
        params = Parameters(labels=param_labels, p_floats=best_pfloats)
        # Theres an extra newline that isn't read
        empty_newline = fin.readline()

        # Read the cooordinates
        vector_size = int(fin.readline())
        coordinates = []
        for _ in range(number_geometries):
            coord_data = []
            for _ in range(0, int(vector_size/number_geometries), 4):
                coordinate = [int(fin.readline()),
                              float(fin.readline()),
                              float(fin.readline()),
                              float(fin.readline())]
                coord_data.append(coordinate)
            coordinates.append(Coordinates(charge=charge, multiplicity=multiplicity,
                                           coordinates=coord_data))

        # Have now loaded all the info for the best am1 individual
        header_string = "#P AM1(Input,Print)\n\nAM1\n"
        header = Header(header_string)
        inputs = []
        for i in range(number_geometries):
            gin = GaussianInput(header=header, coordinates=coordinates[i],
                                parameters=params)
            inputs.append(gin)
        self.best_am1_individual = ParameterGroup(inputs=inputs)

        # Read the energies
        vector_size = int(fin.readline())
        energies = []
        for _ in range(vector_size):
            energies.append(float(fin.readline()))

        # Read the dipoles
        vector_size = int(fin.readline())
        dipoles = []
        for _ in range(vector_size):
            dipoles.append(float(fin.readline()))

        # Make the HighLevelTheory
        hlts = []
        for i in range(number_geometries):
            gout = GaussianOutput()
            gout.ground_energy = energies[i]
            v_dipole = []
            for j in range(3):
                v_dipole.append(dipoles[3*i + j])
            gout.dipole = v_dipole
            hlts.append(gout)
        self.high_level_outputs = hlts


