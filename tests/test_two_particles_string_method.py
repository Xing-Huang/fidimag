from __future__ import print_function
import pytest

# FIDIMAG:
from fidimag.micro import Sim
from fidimag.common import CuboidMesh
from fidimag.micro import UniformExchange, UniaxialAnisotropy
from fidimag.common.string_method import StringMethod
import numpy as np

# Material Parameters
# Parameters
A = 1e-12
Kx = 1e5
# Strong anisotropy
Ms = 3.8e5


"""
We will define two particles using a 4 sites mesh, letting the
sites in the middle as Ms = 0

"""


def two_part(pos):

    x = pos[0]

    if x > 6 or x < 3:
        return Ms
    else:
        return 0

# Finite differences mesh
mesh = CuboidMesh(nx=3,
                  ny=1,
                  nz=1,
                  dx=3, dy=3, dz=3,
                  unit_length=1e-9
                  )


# Simulation Function
def relax_string(maxst, simname, init_im, interp, save_every=10000):
    """
    """

    # Prepare simulation
    # We define the cylinder with the Magnetisation function
    sim = Sim(mesh)
    sim.Ms = two_part

    # sim.add(UniformExchange(A=A))

    # Uniaxial anisotropy along x-axis
    sim.add(UniaxialAnisotropy(Kx, axis=(1, 0, 0)))

    # Define many initial states close to one extreme. We want to check
    # if the images in the last step, are placed mostly in equally positions
    init_images = init_im

    # Number of images between each state specified before (here we need only
    # two, one for the states between the initial and intermediate state
    # and another one for the images between the intermediate and final
    # states). Thus, the number of interpolations must always be
    # equal to 'the number of initial states specified', minus one.
    interpolations = interp

    string = StringMethod(sim,
                          init_images,
                          interpolations=interpolations,
                          name=simname,
                          integrator='verlet'
                          )
    string.integrator.stepsize = 1e-4

    # dt = integrator.stepsize means after every integrator step, the images
    # are rescaled. We can run more integrator steps if we decrease the
    # stepsize, e.g. dt=1e-3 and integrator.stepsize=1e-4
    string.relax(max_iterations=maxst,
                 save_vtks_every=save_every,
                 save_npys_every=save_every,
                 stopping_dYdt=1e-14,
                 dt=1e-4
                 )

    return string


def mid_m(pos):
    if pos[0] > 4:
        return (0.5, 0, 0.2)
    else:
        return (-0.5, 0, 0.2)


def test_energy_barrier_2particles_string():
    # Initial images: we set here a rotation interpolating
    init_im = [(-1, 0, 0), mid_m, (1, 0, 0)]
    interp = [6, 6]

    barriers = []

    # Define different ks for multiple simulations
    # krange = ['1e8']

    string = relax_string(100,
                          'string_2particles_k1e8_10-10int',
                          init_im,
                          interp,
                          save_every=5000,
                          )

    _file = np.loadtxt('string_2particles_k1e8_10-10int_energy.ndt')
    barriers.append((np.max(_file[-1][1:]) - _file[-1][1]) / 1.602e-19)

    print('Energy barrier is:', barriers[-1])
    assert np.abs(barriers[-1] - 0.016019) < 1e-5

    print(barriers)


if __name__ == '__main__':
    test_energy_barrier_2particles_string()
