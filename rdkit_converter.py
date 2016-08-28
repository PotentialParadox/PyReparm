from rdkit import Chem
import openbabel
from gaussian_input import GaussianInput

def reparm_to_rdkit(coordinates):
    obConversion = openbabel.OBConversion()
    obConversion.SetInAndOutFormats("xyz", "mol")
    xyz_str = coordinates.xyz_string()

    xyz = openbabel.OBMol()
    obConversion.ReadString(xyz, xyz_str)

    mol = obConversion.WriteString(xyz)
    return Chem.MolFromMolBlock(mol)

def rdkit_to_reparm(rd):
    obConversion = openbabel.OBConversion()
    obConversion.SetInAndOutFormats("mol", "com")
    mol_str = Chem.MolToMolBlock(rd)

    mol = openbabel.OBMol()
    obConversion.ReadString(mol, mol_str)

    gin_str = obConversion.WriteString(mol)
    gin = GaussianInput(gin_str)
    return gin.coordinates[0]

