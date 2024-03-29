from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.rdMolTransforms import SetDihedralDeg
import openbabel
from gaussian_input import GaussianInput
from gaussian import gaussian_single
from gaussian_output import find_opt_coordinates
from header import Header


def reparm_to_rdkit(coordinates):
    obConversion = openbabel.OBConversion()
    obConversion.SetInAndOutFormats("xyz", "mol")
    if coordinates.xyz_string() is None:
        header = Header("#P AM1\n\nam1\n")
        gin = GaussianInput(header=header, coordinates=coordinates)
        gout = gaussian_single(gin.str())
        coordinates = find_opt_coordinates(gout)
    xyz_str = coordinates.xyz_string()

    xyz = openbabel.OBMol()
    obConversion.ReadString(xyz, xyz_str)

    mol = obConversion.WriteString(xyz)
    rdk_coords = Chem.MolFromMolBlock(mol)
    return Chem.AddHs(rdk_coords)


def rdkit_to_reparm(rd):
    obConversion = openbabel.OBConversion()
    obConversion.SetInAndOutFormats("mol", "com")
    mol_str = Chem.MolToMolBlock(rd)

    mol = openbabel.OBMol()
    obConversion.ReadString(mol, mol_str)

    gin_str = obConversion.WriteString(mol)
    gin = GaussianInput(gin_str)
    return gin.coordinates[0]
