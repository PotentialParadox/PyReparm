from reparm_data import ReparmData
from header import Header
from gaussian_input import GaussianInput
from gaussian import gaussian_single as run
from gaussian_output import find_ground_energy as energy
import matplotlib.pyplot as plt


class Analysis:
    def __init__(self, reparm_data):
        self.reparm_data = ReparmData.copy(reparm_data)

    def face_to_face(self):
        hlt_energies = []
        hlt_exists = False
        try:
            fin = open("ftfthiophene_e.dat", 'r')
            hlt = fin.readline()
            if hlt == str(self.reparm_data.reparm_input.high_level_theory) + "\n":
                hlt_exists = True
                vlength = int(fin.readline())
                for _ in range(vlength):
                    hlt_energies.append(float(fin.readline()))
        except FileNotFoundError:
            hlt_exists = False

        hlt = self.reparm_data.reparm_input.high_level_theory
        fin = open("ftfthiophene.com", 'r')
        file = fin.read()
        gin = GaussianInput(input_string=file)
        params = self.reparm_data.best_am1_individual.inputs[0].parameters[0]
        coords = gin.coordinates[0].coordinates
        gin.parameters[0] = params
        am1_energies = []
        reparm_energies = []
        for i in range(20):
            for atom in coords[9:18]:
                atom[3] += 0.1
            # Run AM1
            am1_header_s = "#P AM1\n\nAM1\n"
            am1_header = Header(am1_header_s)
            gin.header[0] = am1_header
            am1_energies.append(energy(run(gin.str())))
            # Run Reparm
            reparm_header_s = "#P AM1(Input,Print)\n\nReparm\n"
            reparm_header = Header(reparm_header_s)
            gin.header[0] = reparm_header
            reparm_energies.append(energy(run(gin.str())))
            # Run HLT
            if hlt_exists == False:
                hlt_header_s = "#P " + hlt +"\n\nHLT\n"
                hlt_header = Header(hlt_header_s)
                gin.header[0] = hlt_header
                hlt_energies.append(energy(run(gin.str())))
        am1_diffs = distances(am1_energies)
        reparm_diffs = distances(reparm_energies)
        hlt_diffs = distances(hlt_energies)
        fout = open("ftfthiophene_e.dat", 'w')
        fout.write(hlt + "\n")
        fout.write(str(len(hlt_diffs)) + "\n")
        for i in hlt_energies:
            fout.write(str(i) + "\n")
        fout.close()
        plt.plot(am1_diffs, 'r--', label="AM1")
        plt.plot(reparm_diffs, 'b--', label="Reparm")
        plt.plot(hlt_diffs, 'g--', label="HLT")
        plt.legend(loc="best")
        plt.show()


def distances(containter):
    values = []
    for i in range(1, len(containter)):
        values.append(containter[i] - containter[i-1])
    return values
