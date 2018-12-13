import os
import subprocess
from fidimag.common import CuboidMesh
from fidimag.atomistic.hexagonal_mesh import HexagonalMesh
from fidimag.common.field import scalar_field, vector_field
from fidimag.common.vtk import VTK
import pyvtk
import pytest

MODULE_DIR = os.path.realpath(os.path.dirname(__file__))
REF_DIR = os.path.dirname(__file__) + '/vtk_refs/'

def same_as_ref(filepath, ref_dir):
    """
    Looks for file with the same filename as `filepath` in `ref_dir`
    and compares the two.

    """
    filename = os.path.basename(filepath)
    reference = os.path.join(ref_dir, filename)
    ret = subprocess.call(["diff", filepath, reference])
    f = open(filepath, 'r').read()
    print('new\n', f)
    f = open(reference, 'r').read()
    print('ref\n', f)

    return ret == 0  # 0 means files are the same, c.f. man diff exit codes

@pytest.mark.skip(reason="Need a better way to test; precision means comparing diffs does not work.")
def test_save_scalar_field(tmpdir):
    mesh = CuboidMesh(4, 3, 2, 4, 3, 2)
    s = scalar_field(mesh, lambda r: r[0] + r[1] + r[2])
    vtk = VTK(mesh, directory=str(tmpdir), filename="save_scalar")
    vtk.save_scalar(s, name="s")
    assert same_as_ref(vtk.write_file(), REF_DIR)

@pytest.mark.skip(reason="Need a better way to test; precision means comparing diffs does not work.")
def test_save_vector_field(tmpdir):
    mesh = CuboidMesh(4, 3, 2, 4, 3, 2)
    s = vector_field(mesh, lambda r: (r[0], r[1], r[2]))
    vtk = VTK(mesh, directory=str(tmpdir), filename="save_vector")
    vtk.save_vector(s, name="s")
    assert same_as_ref(vtk.write_file(), REF_DIR)

@pytest.mark.skip(reason="Need a better way to test; precision means comparing diffs does not work.")
def test_save_scalar_field_hexagonal_mesh(tmpdir):
    mesh = HexagonalMesh(1, 3, 3)
    s = scalar_field(mesh, lambda r: r[0] + r[1])
    vtk = VTK(mesh, directory=str(tmpdir), filename="scalar_hexagonal")
    vtk.save_scalar(s, name="s")
    assert same_as_ref(vtk.write_file(), REF_DIR)
