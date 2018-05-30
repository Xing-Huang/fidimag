import numpy as np
from fidimag.common.constant import mu_0
import fidimag.common.helper as helper
import inspect


class Zeeman(object):

    """
    A time independent external magnetic field that can be space dependent.
    The field energy in the micromagnetic theory reads:
                                 _
                               /   ->       ->
           E   =  - \mu_0     /    M  \cdot H   dV
                           _ /

    with H as the bias field in A / m, \mu_0 the vacuum permeability and M the
    magnetisation vector. Using finite differences, this quantity is computed
    through the summation

                              __  ->        ->
         E =  - \mu_0 * dV   \    M_i \cdot H_i
                             /__
                              i

    where M_i is the magnetisation at the i-th position of the mesh
    discretisation and dV = dx * dy * dz is the volume of a mesh unit cell.

    If the field is homogeneous, it can be specified in a simulation object
    *Sim* as

            Sim.add(Zeeman((H_x, H_y, H_z)))

    Otherwise, it can be specified as any Fidimag field, passing a function or
    an array. For example, a space dependent field function that changes
    linearly in the x-direction, and only has a x-component, can be defined as:

        def my_Zeeman_field(pos):
            H = 0.01 / (4 * np.pi * 1e-7)  # A / m
            return (H * pos[0], 0, 0)

        # Add field to Simulation object
        Sim.add(Zeeman(my_Zeeman_field))

    For a hysteresis loop, the field can be updated using the *update_field*
    function. For an already defined simulation object *Sim*, it is updated as

        Sim.get_interaction('Zeeman').update_field(new_field)

    where new_field is a 3-tuple, and array or a function, as shown before.
    It is recommended to reset the integrator with *Sim.reset_integrator()*
    to start a new relaxation after updating the field.

    """

    def __init__(self, H0, name='Zeeman'):
        # Raise an exception if H0 is not indexable or callable. This is
        # because H0 represents a vector.
        if hasattr(H0, "__getitem__") is False and\
           hasattr(H0, "__call__") is False:
            raise ValueError("H0 \"{}\" does not represent a vector"
                             .format(H0))
        self.H0 = H0
        self.name = name
        self.jac = False

    def setup(self, mesh, spin, Ms):
        self.mesh = mesh
        self.spin = spin
        self.n = mesh.n

        self.Ms = Ms
        self.Ms_long = np.zeros(3 * mesh.n)

        # TODO: Check if it is necessary to define a 3D matrix for
        # the Ms vectors. Maybe there is a way that uses less memory
        # (see the calculation in the *compute_energy* function)
        self.Ms_long.shape = (3, -1)
        for i in range(mesh.n):
            self.Ms_long[:, i] = Ms[i]

        self.Ms_long.shape = (-1,)
        self.field = np.zeros(3 * self.n)
        self.field[:] = helper.init_vector(self.H0, self.mesh)
        # print self.field

    def update_field(self, H0):
        self.H0 = H0
        self.field[:] = helper.init_vector(self.H0, self.mesh)

    def compute_field(self, t=0, spin=None):
        return self.field

    def average_field(self):
        # Remember that fields are: [fx0, fy0, fz0, fx1, fy1, fz1, fx2, ...]
        # So we jump in steps of 3 starting from the 0, 1 and 2nd elements
        hx = self.field[::3]
        hy = self.field[1::3]
        hz = self.field[2::3]
        return np.array([np.average(hx), np.average(hy), np.average(hz)])

    def compute_energy(self):

        sf = self.field * self.spin * self.Ms_long * mu_0

        energy = -np.sum(sf)

        return energy * (self.mesh.dx *
                         self.mesh.dy *
                         self.mesh.dz *
                         self.mesh.unit_length ** 3.)


class TimeZeeman(Zeeman):
    """
    The time dependent external field, also can vary with space

    The function time_fun must be a function which takes two arguments:

    def time_fun(pos, t):
        x, y, z = pos
        # compute Bx, By, Bz as a function of x y, z and t.
        Bx = ...
        By = ...
        Bz = ...
        return (Bx, By, Bz)

    Extra arguments can be passed to the function to allow more
    general code. These must be set when initialising the TimeZeeman class. For
    example:

    freq = 10e9

    def time_fun(pos, t, frequency):
        x, y, z = pos
        if x < 50:
            return (0.0, 0.0, np.sin(frequency*t))
        else:
            return (0.0, 0.0, 0.0)

    zee = TimeZeeman(time_fun, extra_args=[freq])

    These arguments are then passed into the time_fun code function in
    order.

    """

    def __init__(self, time_fun, extra_args=[], name='TimeZeeman'):
        self.time_fun = time_fun
        self.name = name
        self.jac = True
        self.extra_args = extra_args

    def setup(self, mesh, spin, Ms):
        self.mesh = mesh
        self.spin = spin
        self.n = mesh.n

        self.Ms = Ms
        self.Ms_long = np.zeros(3 * mesh.n)

        # TODO: Check if it is necessary to define a 3D matrix for
        # the Ms vectors. Maybe there is a way that uses less memory
        # (see the calculation in the *compute_energy* function)
        self.Ms_long.shape = (3, -1)
        for i in range(mesh.n):
            self.Ms_long[:, i] = Ms[i]

        self.Ms_long.shape = (-1,)
        self.field = np.zeros(3 * self.n)

    def compute_field(self, t=0, spin=None):
        self.field[:] = helper.init_vector(self.time_fun,
                                           self.mesh,
                                           False,
                                           t, *self.extra_args)
        return self.field


class TimeZeemanSimple(Zeeman):

    """
    Time Dependent Zeeman Interaction with no spatial dependence.

    The function time_fun must be a function which takes one argument:

    def time_fun(t):
        x, y, z = pos
        # compute Bx, By, Bz as a function of x y, z and t.
        Bx = ...
        By = ...
        Bz = ...
        return (Bx, By, Bz)


    Extra arguments can be passed to the function to allow more
    general code. These must be set when initialising the TimeZeeman class. For
    example:

    freq = 10e9

    def time_fun(t, frequency):
        return (0.0, 0.0, np.sin(frequency*t))

    zee = SimpleTimeZeeman(time_fun, extra_args=[freq])

    These arguments are then passed into the time_fun code function in
    order.


    """

    def __init__(self, time_fun, extra_args=[], name='TimeZeemanFast'):
        self.time_fun = time_fun
        self.name = name
        self.jac = True
        self._v = np.zeros(3)
        self.extra_args = extra_args

    def setup(self, mesh, spin, Ms):
        self.mesh = mesh
        self.spin = spin
        self.n = mesh.n

        self.Ms = Ms
        self.Ms_long = np.zeros(3 * mesh.n)

        # TODO: Check if it is necessary to define a 3D matrix for
        # the Ms vectors. Maybe there is a way that uses less memory
        # (see the calculation in the *compute_energy* function)
        self.Ms_long.shape = (3, -1)
        for i in range(mesh.n):
            self.Ms_long[:, i] = Ms[i]

        self.Ms_long.shape = (-1,)
        self.field = np.zeros(3 * self.n)

    def compute_field(self, t=0, spin=None):
        v = self.time_fun(t, *self.extra_args)
        self.field[0::3] = v[0]
        self.field[1::3] = v[1]
        self.field[2::3] = v[2]
        #self.field[::3] = v
        return self.field


class TimeZeemanFast(Zeeman):

    """
    The time dependent external field, also can vary with space. This uses
    an unsafe setting function. Should not be used except by advanced users.

    The function must handle coordinates

    The function time_fun must be a function which takes three or more arguments. The time variable is always passed in as the first argument
    in params.

    e.g.

    from libc.math cimport sin

    def fast_sin_init(mesh, double[:] field, *params):
        t, axis, Bmax, fc = params
        for i in range(mesh.n):
            x, y, z = mesh.coordinates[i]
            if x < 10:
                field[3*i+0] = Bmax * axis[0] * sin(fc*t)
                field[3*i+1] = Bmax * axis[1] * sin(fc*t)
                field[3*i+2] = Bmax * axis[2] * sin(fc*t)

    Add the function to a user Cython module in fidimag/user/ and recompile.

    """

    def __init__(self, time_fun, extra_args=[], name='TimeZeemanFast'):
        self.time_fun = time_fun
        self.name = name
        self.jac = True
        self.extra_args = extra_args

    def setup(self, mesh, spin, Ms):
        self.mesh = mesh
        self.spin = spin
        self.n = mesh.n

        self.Ms = Ms
        self.Ms_long = np.zeros(3 * mesh.n)

        # TODO: Check if it is necessary to define a 3D matrix for
        # the Ms vectors. Maybe there is a way that uses less memory
        # (see the calculation in the *compute_energy* function)
        self.Ms_long.shape = (3, -1)
        for i in range(mesh.n):
            self.Ms_long[:, i] = Ms[i]

        self.Ms_long.shape = (-1,)
        self.field = np.zeros(3 * self.n)

    def compute_field(self, t=0, spin=None):
        helper.init_vector_func_fast(self.time_fun,
                                     self.mesh,
                                     self.field,
                                     False,
                                     t, *self.extra_args)
        return self.field
