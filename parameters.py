import re


class Parameters:
    def __init__(self, from_parameter_string=None,
                 labels=None, p_floats=None):
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

    def __extract_floats(self):
        p_float = re.compile("-?\\d+\\.\\d+")
        p_not_label = re.compile("-?\\d+\\.\\d+.*\n*")
        p_eisol = re.compile("EISol")
        p_eheat = re.compile("EHeat")
        p_gcore = re.compile("GCore")
        p_newline = re.compile("\n")
        p_floats = []
        line_count = 0
        if self.labels is None:
            return None
        for i, label in enumerate(self.labels):
            # print(label)
            if (not re.search(p_eheat, label) 
                and not re.search(p_eisol, label)
                and not re.search(p_gcore, label)):
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
