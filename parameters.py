import re


class Parameters:
    def __init__(self, from_parameter_string=None,
                 labels=None, p_floats=None, fetch_all=False):
        self.fetch_all = fetch_all
        if from_parameter_string:
            self.labels = self.__find_labels(from_parameter_string)
            self.p_floats = self.__extract_floats()
        else:
            self.labels=labels
            self.p_floats=p_floats

    def __find_labels(self, parameter_string):
        p_label = re.compile("(.*?=[^a-zA-Z]+?(?=[^\d\.\-\s\,]))|\n|(\S+\s)")
        m = re.findall(p_label, parameter_string)
        labels = []
        for i in m:
            if i[0] != '':
                labels.append(i[0])
            else:
                labels.append(i[1])
        # for i in labels:
            # print(i)
        if labels != []:
            return labels
        return None

    # Extract the floats from the list of labels.
    def __extract_floats(self):
        p_float = re.compile("-?\\d+\\.\\d+")
        p_not_label = re.compile("-?\\d+\\.\\d+.*\n*")
        p_eisol = re.compile("EISol")
        p_eheat = re.compile("EHeat")
        p_newline = re.compile("\n")
        p_floats = []
        line_count = 0
        if self.labels is None:
            return None
        for i, label in enumerate(self.labels):
            is_float_label = False
            # print(i, label)
            # These are the parameters to minimize, use the
            # print statement above to determine the number
            # for changes, currently we are using
            # H
            # zeta-overlap
            # C
            # F0sp, F0pp, F2pp, G1sp, U, 2nd DDN, 1st KON,
            # 3rd KON, DipHyp,
            # S
            # U, 1st DDN, CoreKO, 2nd KON, 4th KON
            ptm = [9, 28, 29, 30, 31, 33, 36, 38, 40,
                   45, 60, 62, 64, 66, 68]
            if i in ptm:
                is_float_label = True
            # For certain precedures we want to search the whole
            # Parameter Space
            if (self.fetch_all and not re.search(p_eisol, label)
                and not re.search(p_eheat, label)):
                is_float_label = True
            if is_float_label:
                m = re.findall(p_float, label)
                for j, floater in enumerate(m):
                    p_floats.append(float(floater))
                    p_floats.append(int(i))
                    p_floats.append(int(j))
                    p_floats.append(int(line_count))
                self.labels[i] = re.sub(p_not_label, "", label)
            if re.search(p_newline, label):
                line_count += 1
        return p_floats

    def str(self):
        parameters = list(self.labels)
        p = self.p_floats
        for i in range(0, len(self.p_floats), 4):
            ss = ""
            if p[i+2] == 0:
                ss += "{0:.10f}".format(p[i])
            else:
                ss += "," + "{0:.10f}".format(p[i])
            if i >= len(self.p_floats) - 4:
                ss += "\n"
            elif p[i+7] > p[i+3]:
                ss += "\n"
            elif p[i+1] < p[i+5]:
                ss += " "
            parameters[int(p[i+1])] += ss
        parameter_string = ""
        for i in parameters:
            parameter_string += i
        return parameter_string

    def get_floats(self):
        return self.p_floats[0::4]

    def set_floats(self, updated_floats):
        self.p_floats[0::4] = updated_floats
