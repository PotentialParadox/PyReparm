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

gin = GaussianInput(open('trithiophene.com', 'r').read())
rep_coords = gin.coordinates[0]
rdk_coords = reparm_to_rdkit(rep_coords)
# print(Chem.MolToMolBlock(rdk_coords))
AllChem.EmbedMolecule(rdk_coords)
AllChem.UFFOptimizeMolecule(rdk_coords)
for atom in rdk_coords.GetAtoms():
    print(atom.GetAtomicNum())
c = rdk_coords.GetConformer()
SetDihedralDeg(c, 5, 4, 2, 3, 90)
rep_coords = rdkit_to_reparm(rdk_coords)

header = Header("#P am1\n\nam1\n")
open('rdkit.com', 'w').write(GaussianInput(header=header, coordinates=rep_coords).str())
