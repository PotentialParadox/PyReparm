from gaussian_input import GaussianInput


class ParameterGroup:
    def __init__(self, inputs=None, outputs=None):
        if inputs:
            input_list = []
            for i in inputs:
                input_list.append(GaussianInput(i.str()))
            self.inputs = input_list
        if outputs:
            self.outputs = list(outputs)
        if not inputs:
            self.inputs = inputs
        if not outputs:
            self.outputs = outputs

    def get_parameter_floats(self):
        if self.inputs:
            gin = GaussianInput(self.inputs[0])
            return gin.parameters.get_floats()
        return None

    def get_inputs(self):
        return list(self.inputs)

    def set_pfloats(self, pfloats):
        for i in self.inputs:
            for j in i.parameters:
                j.p_floats = pfloats
