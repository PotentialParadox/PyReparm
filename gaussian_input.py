import re
from header import Header
from copy import deepcopy
from coordinates import Coordinates
from parameters import Parameters
from zmatrix import ZMatrix


class GaussianInput:
    def __init__(self, input_string=None, header=None, coordinates=None, parameters=None, fetch_all=False):
        self.header = []
        self.coordinates = []
        self.parameters = []
        if input_string:
            self.find_header(input_string)
            self.find_coordinates(input_string)
            self.find_parameters(input_string, fetch_all)
        else:
            try:
                self.header.extend(header)
            except TypeError:
                self.header.append(header)
            try:
                self.coordinates.extend(coordinates)
            except TypeError:
                self.coordinates.append(coordinates)
            try:
                self.parameters.extend(parameters)
            except TypeError:
                self.parameters.append(parameters)

    def str(self):
        return_str = ""
        for i, head in enumerate(self.header):
            if i > 0:
                return_str += "--Link1--\n"
            if self.header[i]:
                return_str += self.header[i].str()
            if self.coordinates[i]:
                return_str += self.coordinates[i].str()
            if self.parameters[i]:
                return_str += self.parameters[i].str()
        return str(return_str)

    def find_header(self, file_string):
        p_header = re.compile('^(.+\n)+\n(.+\n)')
        m = re.search(p_header, file_string)
        if not m:
            self.header.append(None)
        else:
            header_string = m.group(0)
            self.header.append(Header(header_string))

    def find_coordinates(self, file_string):
        p_coordinates = re.compile("\d\s+\d\n(.*\n)+?(?=Method|--Link1|$)")
        m = re.search(p_coordinates, file_string)
        # print(m.group(0))
        try:
            zmat = ZMatrix(m.group(0))
            zmat.str()
            self.coordinates.append(zmat)
            return zmat
        except (AttributeError, IndexError):
            try:
                cmat = Coordinates(m.group(0))
                cmat.str()
                self.coordinates.append(cmat)
                return cmat
            except TypeError:
                self.coordinates.append(None)
        return None

    def find_parameters(self, file_string, fetch_all):
        p_parameters = re.compile("Method=(.|\n)*(?=--Link1)")
        m = re.search(p_parameters, file_string)
        if not m:
            p_parameters = re.compile("Method=(.|\n)*")
            m = re.search(p_parameters, file_string)
        if not m:
            self.parameters.append(None)
        else:
            parameter_string = m.group(0)
            self.parameters.append(Parameters(from_parameter_string=parameter_string, fetch_all=fetch_all))

    def link(self, gin):
        assert isinstance(gin, GaussianInput)
        self.header.extend(gin.header)
        self.coordinates.extend(gin.coordinates)
        self.parameters.extend(gin.parameters)

    def clear_coordinates(self):
        for i in self.coordinates:
            i.coordinates = None

    def copy(self):
        return deepcopy(self)
