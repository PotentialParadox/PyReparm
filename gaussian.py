from multiprocessing import Process, Pool
from parameter_group import ParameterGroup
from gaussian_input import GaussianInput
from gaussian_output import GaussianOutput
import subprocess
import re


# gaussian single
#               takes the string of an input file, and returns
#               the string of the gaussian output
def gaussian_single(input_file):
    proc = subprocess.Popen(['g09 2>&1 <<END\n' + input_file + 'END'], shell=True,
                            stdout=subprocess.PIPE, universal_newlines=True)
    stdout_value = str(proc.communicate()[0])
    p_normal = re.compile('Normal termination')
    if re.search(p_normal, str(stdout_value)):
        return stdout_value
    else:
        return None


def run_gaussian(parameter_group=None):
    input_list = []
    for i in parameter_group.inputs:
        input_list.append(i.str())
    p = Pool(4)
    output_strings = p.map(gaussian_single, input_list)
    outputs = []
    for i in output_strings:
        if i:
            outputs.append(GaussianOutput(i))
    if not output_strings:
        return None
    return outputs
