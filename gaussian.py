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
    stderr_value = None
    try:
        proc = subprocess.Popen(['g09 2>&1 <<END\n' + input_file + 'END'], shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        stdout_value, stderr_value = proc.communicate()
        p_normal = re.compile('Normal termination')
        if re.search(p_normal, str(stdout_value)):
            return str(stdout_value)
        return None
    except:
        return None


# Returns a list of type gaussian output
def run_gaussian(parameter_group=None, number_processors=1):
    input_list = []
    for i in parameter_group.inputs:
        input_list.append(i.str())
    p = Pool(number_processors)
    output_strings = p.map(gaussian_single, input_list)
    p.close()
    p.join()
    outputs = []
    for i in output_strings:
        if i:
            try:
                outputs.append(GaussianOutput(i))
            except AttributeError:
                return None
        else:
            return None
    return outputs
