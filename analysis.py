from reparm_data import ReparmData
from header import Header
from gaussian_input import GaussianInput
from gaussian import gaussian_single as run
from gaussian_output import find_ground_energy as energy
from gaussian_output import find_opt_coordinates
from rdkit_converter import reparm_to_rdkit, rdkit_to_reparm
from rdkit.Chem import AllChem
from rdkit.Chem.rdMolTransforms import SetDihedralDeg, SetBondLength
import matplotlib.pyplot as plt
import pickle


class Analysis:
    def __init__(self, reparm_data):
        self.reparm_data = ReparmData.copy(reparm_data)
        self.hlt = self.reparm_data.reparm_input.high_level_theory
        # Stored AM1, Reparm, and HLT
        self.ftf_energies = [None, None, None]
        self.dftf_energies = [None, None, None]
        self.trithi_energies = [None, None, None]
        self.dithi_energies = [None, None, None]
        self.load()

    def face_to_face(self):
        number_steps = 20
        gin = GaussianInput(open("ftfthiophene.com", 'r').read())
        hlt = self.reparm_data.reparm_input.high_level_theory
        params = self.reparm_data.best_am1_individual.inputs[0].parameters[0]
        coords = gin.coordinates[0].coordinates
        gin.parameters[0] = params
        am1_energies = []
        reparm_energies = []
        hlt_energies = []
        for i in range(number_steps):
            for atom in coords[9:18]:
                atom[3] += 0.1
            # Run AM1
            if self.ftf_energies is None:
                am1_header_s = "#P AM1\n\nAM1\n"
                am1_header = Header(am1_header_s)
                gin.header[0] = am1_header
                am1_energies.append(energy(run(gin.str())))
            else:
                am1_energies = self.ftf_energies[0]
            # Run Reparm
            reparm_header_s = "#P AM1(Input,Print)\n\nReparm\n"
            reparm_header = Header(reparm_header_s)
            gin.header[0] = reparm_header
            reparm_energies.append(energy(run(gin.str())))
            # Run HLT
            if self.ftf_energies[2] is None:
                hlt_header_s = "#P " + hlt +"\n\nHLT\n"
                hlt_header = Header(hlt_header_s)
                gin.header[0] = hlt_header
                hlt_energies.append(energy(run(gin.str())))
            else:
                hlt_energies = self.ftf_energies[2]
        self.ftf_energies = [am1_energies, reparm_energies, hlt_energies]
        self.save()
        x_values = [i for i in range(number_steps - 1)]
        am1_diffs = distances(am1_energies)
        reparm_diffs = distances(reparm_energies)
        hlt_diffs = distances(hlt_energies)
        plt.plot(x_values, am1_diffs, 'r--', label="AM1")
        plt.plot(x_values, reparm_diffs, 'b--', label="Reparm")
        plt.plot(x_values, hlt_diffs, 'g--', label="HLT")
        plt.legend(loc="best")
        plt.show()

    def trithiophene(self):
        number_steps = 20
        max_angle = 90
        step_size = max_angle / number_steps

        gin = GaussianInput(open('trithiophene.com', 'r').read())
        rep_coords = gin.coordinates[0]
        rdk_coords = reparm_to_rdkit(rep_coords)
        AllChem.EmbedMolecule(rdk_coords)
        AllChem.UFFOptimizeMolecule(rdk_coords)
        c = rdk_coords.GetConformer()

        hlt = self.reparm_data.reparm_input.high_level_theory
        params = self.reparm_data.best_am1_individual.inputs[0].parameters[0]
        am1_energies = []
        reparm_energies = []
        hlt_energies = []
        for i in range(number_steps):
            deg = i * step_size
            SetDihedralDeg(c, 5, 4, 2, 3, deg)
            SetDihedralDeg(c, 7, 6, 8, 9, -deg)
            rep_coords = rdkit_to_reparm(rdk_coords)
            gin.coordinates[0] = rep_coords
            # Run AM1
            if self.trithi_energies[0] is None:
                am1_header_s = "#P AM1\n\nAM1\n"
                am1_header = Header(am1_header_s)
                gin.header[0] = am1_header
                am1_energies.append(energy(run(gin.str())))
            else:
                am1_energies = self.trithi_energies[0]
            # Run HLT
            if self.trithi_energies[2] is None:
                hlt_header_s = "#P " + hlt + "\n\nHLT\n"
                hlt_header = Header(hlt_header_s)
                gin.header[0] = hlt_header
                hlt_energies.append(energy(run(gin.str())))
            else:
                hlt_energies = self.trithi_energies[2]
            # Run Reparm
            reparm_header_s = "#P AM1(Input,Print)\n\nReparm\n"
            reparm_header = Header(reparm_header_s)
            gin.header[0] = reparm_header
            gin.parameters[0] = params
            reparm_energies.append(energy(run(gin.str())))
        self.trithi_energies = [am1_energies, reparm_energies, hlt_energies]
        self.save()
        x_values = [i*step_size for i in range(number_steps - 1)]
        am1_diffs = distances(am1_energies)
        reparm_diffs = distances(reparm_energies)
        hlt_diffs = distances(hlt_energies)
        plt.plot(x_values, am1_diffs, 'r--', label="AM1")
        plt.plot(x_values, reparm_diffs, 'b--', label="Reparm")
        plt.plot(x_values, hlt_diffs, 'g--', label="HLT")
        plt.legend(loc="best")
        plt.show()

    def dithi_face_to_face(self):
        number_steps = 20
        gin = GaussianInput(open("dithi_face_to_face.com", 'r').read())
        hlt = self.reparm_data.reparm_input.high_level_theory
        params = self.reparm_data.best_am1_individual.inputs[0].parameters[0]
        coords = gin.coordinates[0].coordinates
        gin.parameters[0] = params
        am1_energies = []
        reparm_energies = []
        hlt_energies = []
        for i in range(number_steps):
            for atom in coords[9:18]:
                atom[1] += 0.1
            print('testing', gin.coordinates[0].str())
            # Run AM1
            if self.dftf_energies[0] is None:
                am1_header_s = "#P AM1\n\nAM1\n"
                am1_header = Header(am1_header_s)
                gin.header[0] = am1_header
                am1_energies.append(energy(run(gin.str())))
            else:
                am1_energies = self.dftf_energies[0]
            # Run Reparm
            reparm_header_s = "#P AM1(Input,Print)\n\nReparm\n"
            reparm_header = Header(reparm_header_s)
            gin.header[0] = reparm_header
            reparm_energies.append(energy(run(gin.str())))
            # Run HLT
            if self.dftf_energies[2] is None:
                hlt_header_s = "#P " + hlt + "\n\nHLT\n"
                hlt_header = Header(hlt_header_s)
                gin.header[0] = hlt_header
                hlt_energies.append(energy(run(gin.str())))
            else:
                hlt_energies = self.dftf_energies[2]
        self.dftf_energies = [am1_energies, reparm_energies, hlt_energies]
        self.save()
        x_values = [i for i in range(number_steps - 1)]
        am1_diffs = distances(am1_energies)
        reparm_diffs = distances(reparm_energies)
        hlt_diffs = distances(hlt_energies)
        plt.plot(x_values, am1_diffs, 'r--', label="AM1")
        plt.plot(x_values, reparm_diffs, 'b--', label="Reparm")
        plt.plot(x_values, hlt_diffs, 'g--', label="HLT")
        plt.legend(loc="best")
        plt.show()

    def dithiophene(self):
        number_steps = 20
        max_angle = 90
        step_size = max_angle / number_steps

        gin = GaussianInput(open('dithiophene.com', 'r').read())
        rep_coords = gin.coordinates[0]
        rdk_coords = reparm_to_rdkit(rep_coords)
        AllChem.EmbedMolecule(rdk_coords)
        AllChem.UFFOptimizeMolecule(rdk_coords)
        c = rdk_coords.GetConformer()

        hlt = self.reparm_data.reparm_input.high_level_theory
        params = self.reparm_data.best_am1_individual.inputs[0].parameters[0]
        am1_energies = []
        reparm_energies = []
        hlt_energies = []
        for i in range(number_steps):
            deg = i * step_size
            SetDihedralDeg(c, 2, 3, 4, 5, deg)
            rep_coords = rdkit_to_reparm(rdk_coords)
            gin.coordinates[0] = rep_coords
            # Run AM1
            if self.dithi_energies[0] is None:
                am1_header_s = "#P AM1\n\nAM1\n"
                am1_header = Header(am1_header_s)
                gin.header[0] = am1_header
                am1_energies.append(energy(run(gin.str())))
            else:
                am1_energies = self.trithi_energies[0]
            # Run HLT
            if self.dithi_energies[2] is None:
                hlt_header_s = "#P " + hlt + "\n\nHLT\n"
                hlt_header = Header(hlt_header_s)
                gin.header[0] = hlt_header
                hlt_energies.append(energy(run(gin.str())))
            else:
                hlt_energies = self.trithi_energies[2]
            # Run Reparm
            reparm_header_s = "#P AM1(Input,Print)\n\nReparm\n"
            reparm_header = Header(reparm_header_s)
            gin.header[0] = reparm_header
            gin.parameters[0] = params
            reparm_energies.append(energy(run(gin.str())))
        self.dithi_energies = [am1_energies, reparm_energies, hlt_energies]
        self.save()
        x_values = [i * step_size for i in range(number_steps - 1)]
        am1_diffs = distances(am1_energies)
        reparm_diffs = distances(reparm_energies)
        hlt_diffs = distances(hlt_energies)
        plt.plot(x_values, am1_diffs, 'r--', label="AM1")
        plt.plot(x_values, reparm_diffs, 'b--', label="Reparm")
        plt.plot(x_values, hlt_diffs, 'g--', label="HLT")
        plt.legend(loc="best")
        plt.show()

    def save(self):
        pickle.dump(self, open("analysis.dat", 'wb'))

    def load(self):
        lf = pickle.load(open("analysis.dat", 'rb'))
        if lf.hlt == self.hlt and self.hlt is not None:
            self.ftf_energies = lf.ftf_energies
            self.trithi_energies = lf.trithi_energies


def distances(containter):
    values = []
    for i in range(1, len(containter)):
        values.append(containter[i] - containter[i-1])
    return values

