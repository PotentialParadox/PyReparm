from reparm_data import ReparmData
from header import Header
from gaussian_input import GaussianInput
from gaussian import gaussian_single as run
from gaussian_output import find_ground_energy as energy
from gaussian_output import find_opt_coordinates
from rdkit_converter import reparm_to_rdkit, rdkit_to_reparm
from rdkit.Chem import AllChem
from rdkit.Chem.rdMolTransforms import SetDihedralDeg, SetBondLength
import numpy as np
import seaborn as sns
import math
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
            if self.ftf_energies[0] is None:
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
        print_graph(am1_energies, reparm_energies, hlt_energies)
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
        # Dustin Temp
        # gin_temp = GaussianInput(open('ga_best.com', 'r').read())
        # params = gin_temp.parameters[0]
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
        print_graph(am1_energies, reparm_energies, hlt_energies)

    def dithi_face_to_face(self):
        number_steps = 20
        gin = GaussianInput(open("dithi_face_to_face.com", 'r').read())
        hlt = self.reparm_data.reparm_input.high_level_theory
        # Dustin Temp
        # gin_temp = GaussianInput(open('ga_best.com', 'r').read())
        # params = gin_temp.parameters[0]
        params = self.reparm_data.best_am1_individual.inputs[0].parameters[0]
        coords = gin.coordinates[0].coordinates
        gin.parameters[0] = params
        am1_energies = []
        reparm_energies = []
        hlt_energies = []
        for i in range(number_steps):
            for atom in coords[16:36]:
                atom[1] += 0.1
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
        print_graph(am1_energies, reparm_energies, hlt_energies)

    def dithiophene(self):
        number_steps = 20
        max_angle = 180
        step_size = max_angle / number_steps

        gin = GaussianInput(open('dithiophene.com', 'r').read())
        rep_coords = gin.coordinates[0]
        rdk_coords = reparm_to_rdkit(rep_coords)
        AllChem.EmbedMolecule(rdk_coords)
        AllChem.UFFOptimizeMolecule(rdk_coords)
        c = rdk_coords.GetConformer()

        hlt = self.reparm_data.reparm_input.high_level_theory
        # Dustin Temp
        # gin_temp = GaussianInput(open('ga_best.com', 'r').read())
        # params = gin_temp.parameters[0]
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
                am1_energies = self.dithi_energies[0]
            # Run HLT
            if self.dithi_energies[2] is None:
                hlt_header_s = "#P " + hlt + "\n\nHLT\n"
                hlt_header = Header(hlt_header_s)
                gin.header[0] = hlt_header
                hlt_energies.append(energy(run(gin.str())))
            else:
                hlt_energies = self.dithi_energies[2]
            # Run Reparm
            reparm_header_s = "#P AM1(Input,Print)\n\nReparm\n"
            reparm_header = Header(reparm_header_s)
            gin.header[0] = reparm_header
            gin.parameters[0] = params
            reparm_energies.append(energy(run(gin.str())))
        self.dithi_energies = [am1_energies, reparm_energies, hlt_energies]
        self.save()
        print_rms(am1_energies, reparm_energies, hlt_energies)
        print_graph(am1_energies, reparm_energies, hlt_energies)

    def save(self):
        pickle.dump(self, open("analysis.dat", 'wb'))

    def load(self):
        lf = pickle.load(open("analysis.dat", 'rb'))
        if lf.hlt == self.hlt and self.hlt is not None:
            self.ftf_energies = lf.ftf_energies
            self.dftf_energies = lf.dftf_energies
            self.trithi_energies = lf.trithi_energies
            self.dithi_energies = lf.dithi_energies


def distances(container):
    values = np.zeros((len(container), len(container)))
    for i in range(1, len(container)):
        for j in range(1, len(container)):
            values[i][j] = abs(container[i] - container[j])
    return np.array(values)


def print_graph(am1, reparm, hlt):
    am1_e = np.array(am1)
    reparm_e = np.array(reparm)
    hlt_e = np.array(hlt)
    am1_e = am1_e - np.average(am1_e)
    reparm_e = reparm_e - np.average(reparm_e)
    hlt_e = hlt_e - np.average(hlt_e)
    plt.plot(am1_e, label='am1')
    plt.plot(reparm_e, label='reparm')
    plt.plot(hlt_e, label='hlt')
    plt.legend()
    plt.show()


def print_rms(am1, reparm, hlt):
    am1_e = np.array(am1) - np.average(np.array(am1))
    reparm_e = np.array(reparm) - np.average(np.array(reparm))
    hlt_e = np.array(hlt) - np.average(np.array(hlt))
    am1_e_diff = am1_e - hlt_e
    am1_rms = math.sqrt(np.sum(am1_e_diff**2)/len(am1_e_diff))
    reparm_e_diff = reparm_e - hlt_e
    reparm_rms = math.sqrt(np.sum(reparm_e_diff**2)/len(reparm_e_diff))
    print('AM1 RMS', am1_rms)
    print('Reparm RMS', reparm_rms)


fin = open("reparm.in", 'r')
file = fin.read()
reparm_data = ReparmData(file)
load_success = reparm_data.load()
if load_success:
    analysis = Analysis(reparm_data)
    analysis.dithiophene()
    print("Success")
else:
    print("Reparm.dat does not match reparm.in, analysis closed")

# 3, 22, 23, 24, 25, 28, 29, 33, 35, 37, 40, 62, 65, 67, 69, 71, 79
# X = np.array(reparm_data.features)
# print(X.shape)
# Y = np.array(reparm_data.observations)
# print(Y.shape)
# T = np.transpose(np.append(X[:,0:10], Y, axis=1))
# sns.set(style='whitegrid', context='notebook')
# sns.set(font_scale=1.0)
# cm = np.corrcoef(T)
# hm = sns.heatmap(cm,
#         cbar=True,
#         annot=True,
#         square=True,
#         fmt='.2f',
#         annot_kws={'size': 10})
# plt.show()
#
# IL = []
# for i in range(0, len(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats), 4):
#     IL.append(reparm_data.best_am1_individual.inputs[0].parameters[0].p_floats[i])
#
# for i, v in enumerate(IL):
#     print(i, v)
#
# print(reparm_data.best_am1_individual.inputs[0].parameters[0].str())
